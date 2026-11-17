#!/usr/bin/env python3
"""Reproduce the scientific evidence from normalized archived observations.

Requires Python 3.11+ and NumPy. No network, tokenizer, model, or GPU is used.
Run: python reproduce.py --out /path/to/a/new/output_directory
"""
from pathlib import Path
import argparse,ast,collections,csv,gzip,hashlib,json,sys,time
import numpy as np

BUNDLE=Path(__file__).resolve().parent
sys.path.insert(0,str(BUNDLE/'code'))
import canonical_readouts_v1 as canonical
import native_score
from family_statistics import ci

ENDPOINTS=['displayed_success','short_solution_delivered','common9_consistency','unshown_pair_success','original_unseen9_success','uniform_fraction','active_fraction','candidate_available','native_success']
VOCAB=set('abcdefghijkuvwxyz')

def rows(path):
    with path.open(encoding='utf-8')as f:return [json.loads(line)for line in f if line.strip()]

def csvread(path):
    with path.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))

def csvwrite(path,records):
    records=list(records);path.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for r in records for k in r))
    with path.open('w',encoding='utf-8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(records)

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def rule_pair(text):
    call=ast.parse(text,mode='eval').body
    assert isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='replace'and len(call.args)==2 and not call.keywords
    a,b=map(ast.literal_eval,call.args)
    assert isinstance(a,str)and isinstance(b,str)and 1<=len(a)<=3 and len(b)<=3 and set(a+b)<=VOCAB
    return (a,b)

def one_rules(xs,ys):
    anchor=next(i for i,(x,y)in enumerate(zip(xs,ys))if x!=y)
    def substrings(s):return {s[i:i+k]for k in (1,2,3)for i in range(len(s)-k+1)}
    return sorted((a,b)for a in substrings(xs[anchor])for b in substrings(ys[anchor])|{''}if all(x.replace(a,b)==y for x,y in zip(xs,ys)))

def verify_worked_case(families,variants):
    case=json.loads((BUNDLE/'worked_case.json').read_text(encoding='utf-8'))
    sid=case['family_id'];family=families[sid]
    by={(v['sample_id'],v['base_count']):v for v in variants}
    returned={v['sample_id']for v in variants if v['certificate_status']=='SHORTCUT_RETURN_1_TO_1'}
    assert returned=={sid}
    assert case['reference_program']==family['reference_rules']
    ref=[rule_pair(s)for s in family['reference_rules']]
    assert [list(r)for r in ref]==case['reference_rule_pairs']
    shown=family['witness_pairs'][family['displayed_witness_index']-1]
    for arm in ('control','separation'):
        item=case['displayed_'+arm+'_witness']
        assert all(item[k]==shown[arm][k]for k in ('input','output','signature'))
    for b in (3,4,5):
        item=case['counts'][str(b)];v=by[sid,b]
        assert item['base_original_indices']==v['base_original_indices']and item['certificate_status']==v['certificate_status']
        for arm in ('CONTROL','SEPARATION'):
            assert item[arm]==v['arms'][arm]
            cert=item[arm];rr=one_rules(cert['inputs'],cert['outputs'])
            assert rr==sorted(tuple(r)for r in cert['one_rule_solutions'])
        assert item['SEPARATION']['minimum_length']==(1 if b<5 else 2)
    critical=case['critical_identity_example'];x=critical['input'];rule=[critical['candidate_rule']]
    assert canonical.apply([x],ref)==[critical['reference_output']]==[x]
    assert canonical.apply([x],rule)==[critical['candidate_output']]==['iyxdcdc']
    for b in (3,4):
        cert=by[sid,b]['arms']['SEPARATION'];assert canonical.apply(cert['inputs'],rule)==cert['outputs']
        assert x not in cert['inputs']
    cert=by[sid,5]['arms']['SEPARATION'];assert x in cert['inputs']and canonical.apply(cert['inputs'],rule)!=cert['outputs']
    return {'family_id':sid,'verified':True,'reference_identity_output':x,'shortcut_output':critical['candidate_output'],'separation_minimum_by_base':{'3':1,'4':1,'5':2},'selection':'Unique certificate-defined shortcut-return family; no model outcomes used.'}

def verify_inputs(families,variants,audits):
    certificates=rows(BUNDLE/'data/certificate_records.jsonl')
    cby={(r['sample_id'],r['base_count'],r['arm']):r for r in certificates}
    assert len(certificates)==len(cby)==960
    base_stats=[];status=collections.Counter()
    for v in variants:
        sid,b=v['sample_id'],v['base_count'];family=families[sid];ref=[rule_pair(s)for s in family['reference_rules']]
        witness=family['witness_pairs'][family['displayed_witness_index']-1]
        for arm in ('CONTROL','SEPARATION'):
            cert=v['arms'][arm];assert cert==cby[sid,b,arm]
            xs,ys=cert['inputs'],cert['outputs'];assert len(xs)==len(ys)==b+1
            assert len(set(xs))==len(xs)and all(set(x+y)<=VOCAB for x,y in zip(xs,ys))
            solved=one_rules(xs,ys)
            assert solved==sorted(tuple(rule)for rule in cert['one_rule_solutions'])
            assert len(solved)==cert['one_rule_count']
            assert cert['minimum_length']==(1 if solved else 2)
            assert canonical.apply(xs,ref)==ys
            if arm=='CONTROL':assert solved
        observed_status='CERT_1_TO_2'if v['arms']['SEPARATION']['one_rule_count']==0 else'SHORTCUT_RETURN_1_TO_1'
        assert v['certificate_status']==observed_status
        status[b,observed_status]+=1
        xs,ys=v['arms']['CONTROL']['inputs'],v['arms']['CONTROL']['outputs']
        base=[(x,y)for x,y in zip(xs,ys)if x!=witness['control']['input']]
        solutions=one_rules(*map(list,zip(*base)))
        base_stats.append({'sample_id':sid,'base_count':b,'base_one_rule_solutions':len(solutions),'base_nonidentity':sum(x!=y for x,y in base),'control_one_rule_solutions':v['arms']['CONTROL']['one_rule_count'],'separation_one_rule_solutions':v['arms']['SEPARATION']['one_rule_count'],'certificate_status':observed_status})
    checked=active=0
    for sid,groups in audits.items():
        ref=[rule_pair(s)for s in families[sid]['reference_rules']]
        for stratum,points in groups.items():
            assert len(points)==32
            xs=[p['input']for p in points];ys=[p['output']for p in points]
            assert canonical.apply(xs,ref)==ys
            checked+=len(points)
            if stratum=='ACTIVE':
                for x in xs:
                    y=x
                    for a,b in ref:
                        z=y.replace(a,b);assert z!=y;y=z
                    active+=1
    native=csvread(BUNDLE/'data/native1008.csv');native_counts=collections.Counter()
    for r in native:
        xs,ys=json.loads(r['inputs']),json.loads(r['outputs']);ref=[rule_pair(s)for s in json.loads(r['reference_programs'])]
        assert canonical.apply(xs,ref)==ys
        if xs==ys:lower=upper=0;classification='IDENTITY_SHORTCUT'
        else:
            solutions=one_rules(xs,ys);assert len(solutions)==int(r['one_rule_solution_count'])
            lower=upper=1 if solutions else len(ref)
            if not solutions:lower=2
            classification='ONE_RULE_SHORTCUT'if solutions and len(ref)>1 else'ONE_RULE_REFERENCE'if solutions else'CERTIFIED_MINIMUM2'if len(ref)==2 else'NO_ONE_RULE_BOUND2_TO_K'
        assert int(r['minimum_lower_bound'])==lower and int(r['minimum_upper_bound'])==upper and r['status']==classification
        native_counts[classification,len(ref)]+=1
    return {'panel_certificates_checked':len(certificates),'panel_variants_checked':len(variants),'broader_reference_labels_checked':checked,'active_inputs_with_both_rules_verified':active,'native_archive_rows_checked':len(native),'certificate_counts':{str(k):v for k,v in status.items()},'native_archive_counts':{str(k):v for k,v in native_counts.items()}},base_stats

def score_observations(families,vby,audits):
    by_request={};parse_mismatch=[];new_counts=collections.Counter();ledger=[]
    with gzip.open(BUNDLE/'data/trajectories.jsonl.gz','rt',encoding='utf-8')as f:
        for line in f:
            t=json.loads(line);mid,sid,b,arm=t['model_id'],t['sample_id'],t['base_count'],t['arm'];request=t['request_id']
            assert request==f'{mid}|{sid}|B{b}|{arm}'and request not in by_request
            family=families[sid];v=vby[sid,b];spec=v['arms'][arm];xs,ys=spec['inputs'],spec['outputs']
            selected=canonical.final_rules(t['raw_text']);normal=[list(rule)for rule in selected]if selected is not None else None
            assert normal==t['selected_final']['rules'],request
            assert t['selected_final']['parseable']==(selected is not None)
            assert t['generated_tokens']==len(t['generated_token_ids'])<=8192
            assert t['prompt_tokens']==len(t['prompt_token_ids'])
            def ok(xx,yy):return int(selected is not None and canonical.apply(xx,selected)==yy)
            shown=family['witness_pairs'][family['displayed_witness_index']-1]
            other=family['witness_pairs'][2-family['displayed_witness_index']]
            allx=family['original_inputs']+[pair[k]['input']for pair in family['witness_pairs']for k in ('control','separation')]
            ally=family['original_outputs']+[pair[k]['output']for pair in family['witness_pairs']for k in ('control','separation')]
            hidden=[(x,y)for x,y in zip(allx,ally)if x not in family['original_inputs']and x!=shown[arm.lower()]['input']]
            assert len(hidden)==3 and not set(x for x,y in hidden)&set(xs)
            metrics={'displayed_success':ok(xs,ys),'short_solution_delivered':int(ok(xs,ys)and len(selected)==1),'common9_consistency':ok(allx,ally),'unshown_pair_success':ok([other[k]['input']for k in ('control','separation')],[other[k]['output']for k in ('control','separation')]),'original_unseen9_success':ok([x for x,y in hidden],[y for x,y in hidden])}
            for stratum,name in [('UNIFORM','uniform_fraction'),('ACTIVE','active_fraction')]:
                points=audits[sid][stratum];assert len(points)==32 and not set(p['input']for p in points)&set(xs)
                metrics[name]=float(np.mean([selected is not None and canonical.apply([p['input']],selected)==[p['output']]for p in points]))
            candidates=[canonical.parse_list(match.group())for match in canonical.LIST_SPAN.finditer(t['raw_text'])]
            metrics['candidate_available']=int(any(rule is not None and canonical.apply(xs,rule)==ys for rule in candidates))
            metrics['native_success']=int(native_score.score(t['raw_text'],xs,ys)['pass_at_1'])
            by_request[request]={'request_id':request,'sample_id':sid,'model_id':mid,'base_count':b,'arm':arm,'certificate_status':v['certificate_status'],'origin':t['origin'],'parseable':selected is not None,'selected_rule_count':len(selected)if selected is not None else None,'generated_tokens':t['generated_tokens'],'stop_reason':t['stop_reason'],'scientific_invalid_final':selected is None,**metrics}
            if t['origin']=='NEW_R1':
                new_counts['rows']+=1;new_counts[t['stop_reason']]+=1;new_counts['tokens']+=t['generated_tokens'];new_counts['unparseable']+=selected is None
    assert len(by_request)==1920
    return by_request,dict(new_counts)

def effects_from_records(records,families,variants,vby):
    rby={(r['model_id'],r['sample_id'],r['base_count'],r['arm']):r for r in records}
    common=sorted(sid for sid in families if all(vby[sid,b]['certificate_status']=='CERT_1_TO_2'for b in [3,4,5,6]))
    effects=[];family_deltas=[]
    for mid in ['M1','M2']:
        for b in [3,4,5,6]:
            for group in ['CERT_1_TO_2','ALL_LEGAL','SHORTCUT_RETURN_1_TO_1','COMMON_CERT_INTERSECTION']:
                eligible=sorted(sid for sid in families if vby[sid,b]['certificate_status']!='INVALID_OR_UNRESOLVED'and(group=='ALL_LEGAL'or group=='COMMON_CERT_INTERSECTION'and sid in common or group==vby[sid,b]['certificate_status']))
                present=[sid for sid in eligible if all((mid,sid,b,arm)in rby for arm in ['CONTROL','SEPARATION'])]
                for metric in ENDPOINTS:
                    ctrl=np.array([rby[mid,sid,b,'CONTROL'][metric]for sid in present],float);sep=np.array([rby[mid,sid,b,'SEPARATION'][metric]for sid in present],float);delta=sep-ctrl
                    result=ci(delta,f'{mid}|{b}|{group}|{metric}')
                    effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'SEPARATION_MINUS_CONTROL','planned_n':len(eligible),'completed_n':len(present),'control_numerator_sum':float(ctrl.sum()),'separation_numerator_sum':float(sep.sum()),'control_mean':float(ctrl.mean())if len(ctrl)else None,'separation_mean':float(sep.mean())if len(sep)else None,**result})
                    if group=='COMMON_CERT_INTERSECTION'and b!=5:
                        full=[sid for sid in present if all((mid,sid,5,arm)in rby for arm in ['CONTROL','SEPARATION'])]
                        dd=np.array([(rby[mid,sid,b,'SEPARATION'][metric]-rby[mid,sid,b,'CONTROL'][metric])-(rby[mid,sid,5,'SEPARATION'][metric]-rby[mid,sid,5,'CONTROL'][metric])for sid in full])
                        effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'DELTA_BASE_MINUS_DELTA_BASE5',**ci(dd,f'{mid}|{b}|DID|{metric}')})
                        if metric=='displayed_success':effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'DELTA_BASE_MINUS_DELTA_BASE5_SIMULTANEOUS',**ci(dd,f'{mid}|{b}|DID|{metric}',True)})
                for sid in present:family_deltas.append({'model_id':mid,'sample_id':sid,'base_count':b,'cohort':group,**{metric:rby[mid,sid,b,'SEPARATION'][metric]-rby[mid,sid,b,'CONTROL'][metric]for metric in ENDPOINTS}})
    return effects,family_deltas,len(common)

def compare_csv(actual,expected):
    a,b=csvread(actual),csvread(expected);assert len(a)==len(b),(actual.name,len(a),len(b))
    mismatches=[]
    for i,(left,right)in enumerate(zip(a,b)):
        assert set(left)==set(right),(actual.name,'fields')
        for key,x in left.items():
            y=right[key]
            if x==y:continue
            try:
                if abs(float(x)-float(y))<=1e-12:continue
            except(ValueError,TypeError):pass
            mismatches.append({'row':i,'field':key,'actual':x,'expected':y})
    assert not mismatches,(actual.name,mismatches[:3])
    return {'table':actual.name,'rows':len(a),'numeric_and_categorical_values_match':True,'CSV_bytes_match':actual.read_bytes()==expected.read_bytes(),'sha256':hashlib.sha256(actual.read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    assert not args.out.exists(),'Choose a new output directory';args.out.mkdir(parents=True)
    started=time.perf_counter();families={f['sample_id']:f for f in rows(BUNDLE/'data/families.jsonl')};variants=rows(BUNDLE/'data/base_variants.jsonl');vby={(v['sample_id'],v['base_count']):v for v in variants}
    assert len(families)==120 and len(variants)==len(vby)==480
    audits=collections.defaultdict(dict)
    for r in rows(BUNDLE/'data/broader_inputs.jsonl'):audits[r['sample_id']][r['stratum']]=r['accepted']
    checked,base_stats=verify_inputs(families,variants,audits)
    checked['worked_case']=verify_worked_case(families,variants)
    observed,new_counts=score_observations(families,vby,audits)
    records=[observed[f"{mid}|{v['sample_id']}|B{v['base_count']}|{arm}"]for mid in ['M1','M2']for v in variants for arm in ['CONTROL','SEPARATION']]
    effects,differences,common_n=effects_from_records(records,families,variants,vby)
    csvwrite(args.out/'per_family_metrics.csv',records);csvwrite(args.out/'paired_effects.csv',effects);csvwrite(args.out/'family_paired_differences.csv',differences);csvwrite(args.out/'base_certificate_summary.csv',base_stats)
    comparisons=[compare_csv(args.out/rel,BUNDLE/'results'/rel)for rel in ['per_family_metrics.csv','paired_effects.csv','family_paired_differences.csv']]
    result={'status':'PASS','scientific_tables':comparisons,'checks':checked,'scored_requests':len(records),'paired_effect_rows':len(effects),'common_certified_family_count':common_n,'new_observation_counts':new_counts,'numpy_version':np.__version__,'CPU_elapsed_seconds':time.perf_counter()-started,'model_or_GPU_calls':0,'original_raw_JSON_byte_layout_reconstructed':False,'normalization_scope':'Scientific contents and score tables are reproduced from the normalized observations.'}
    dump(args.out/'REPLAY_VALIDATION.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
