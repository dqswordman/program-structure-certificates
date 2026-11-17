"""Pre-output analysis specification: family pairing, fixed endpoints, no outcome selection."""
from rb_common import *
import collections,time
import numpy as np
from pilot_common import apply_pairs
import canonical_readouts_v1 as c
import legacy_readouts as legacy

ENDPOINTS=['displayed_success','short_solution_delivered','common9_consistency','unshown_pair_success','original_unseen9_success','uniform_fraction','active_fraction','candidate_available','native_success']
def ci(x,label,simultaneous=False):
 x=np.asarray(x,float);n=len(x)
 if not n:return {'n_families':0,'estimate':None,'ci_low':None,'ci_high':None}
 # Same-family whole-row resampling. Separate conditional cohorts have separate deterministic streams.
 rng=np.random.Generator(np.random.PCG64(20261107))
 means=np.empty(20000)
 for off in range(0,20000,1000):means[off:off+1000]=x[rng.integers(0,n,(1000,n))].mean(1)
 q=[.025,.975] if not simultaneous else [.05/(2*6),1-.05/(2*6)]
 lo,hi=np.quantile(means,q)
 return {'n_families':n,'estimate':float(x.mean()),'ci_low':float(lo),'ci_high':float(hi),'bootstrap_replicates':20000,'interval':'percentile_family_paired' if not simultaneous else 'Bonferroni_percentile_six_model_by_newbase_comparisons'}
def main():
 started=time.perf_counter();frozen=assert_freeze()
 families={f['sample_id']:f for f in rows(OLD/'artifacts/families.jsonl')};variants=rows(RUN/'base_variant_manifest.jsonl');vby={(v['sample_id'],v['base_count']):v for v in variants}
 audits=collections.defaultdict(dict)
 for r in rows(A/'E1/audit_inputs.jsonl'):audits[r['sample_id']][r['stratum']]=r['accepted']
 selected={(r['model_id'],r['sample_id'],r['structure']):r for r in rows(OLD/'artifacts/selected_finals.jsonl') if r['model_id'] in ['M1','M2']}
 oldtexts={}
 for mid in ['M1','M2']:
  for path in sorted((OLD/f'artifacts/trajectories/{mid}').glob('batch_*.json')):
   for t in read(path)['trajectories']:oldtexts[mid,t['sample_id'],t['variant']]=t
 records=[]
 for mid in ['M1','M2']:
  for v in variants:
   if v['certificate_status']=='INVALID_OR_UNRESOLVED':continue
   sid=v['sample_id'];b=v['base_count'];f=families[sid];w=f['witness_pairs'][f['displayed_witness_index']-1];other=f['witness_pairs'][2-f['displayed_witness_index']]
   for arm in ['CONTROL','SEPARATION']:
    request=f'{mid}|{sid}|B{b}|{arm}'
    if b==5:
     t=oldtexts[mid,sid,arm];s=selected[mid,sid,arm]['selected_final'];origin='CACHED_BASE5'
    else:
     path=RUN/'raw'/mid/(request.replace('|','_')+'.json')
     if not path.exists():continue
     t=read(path);s=t['selected_final'];origin='NEW_R1'
    rules=s['rules'];spec=v['arms'][arm];xs=spec['inputs'];ys=spec['outputs']
    def ok(xx,yy):return int(rules is not None and c.apply(xx,rules)==yy)
    allx=f['original_inputs']+[p[k]['input'] for p in f['witness_pairs'] for k in ['control','separation']]
    ally=f['original_outputs']+[p[k]['output'] for p in f['witness_pairs'] for k in ['control','separation']]
    hidden=[(x,y) for x,y in zip(allx,ally) if x not in f['original_inputs'] and x!=w[arm.lower()]['input']]
    # Deleted original base examples do not become new hidden tests.
    assert len(hidden)==3 and not set(x for x,y in hidden)&set(xs)
    ux=[other[k]['input'] for k in ['control','separation']];uy=[other[k]['output'] for k in ['control','separation']]
    metrics={'displayed_success':ok(xs,ys),'short_solution_delivered':int(ok(xs,ys) and len(rules)==1),'common9_consistency':ok(allx,ally),'unshown_pair_success':ok(ux,uy),'original_unseen9_success':ok([x for x,y in hidden],[y for x,y in hidden])}
    for st,name in [('UNIFORM','uniform_fraction'),('ACTIVE','active_fraction')]:
     aa=audits[sid][st];assert len(aa)==32 and not set(x['input'] for x in aa)&set(xs)
     metrics[name]=float(np.mean([rules is not None and c.apply([x['input']],rules)==[x['output']] for x in aa]))
    candidates=[c.parse_list(m.group()) for m in c.LIST_SPAN.finditer(t['raw_text'])]
    metrics['candidate_available']=int(any(r is not None and c.apply(xs,r)==ys for r in candidates))
    metrics['native_success']=int(legacy.score(t['raw_text'],xs,ys)['pass_at_1'])
    records.append({'request_id':request,'sample_id':sid,'model_id':mid,'base_count':b,'arm':arm,'certificate_status':v['certificate_status'],'origin':origin,'parseable':s['parseable'],'selected_rule_count':len(rules) if rules is not None else None,'generated_tokens':t['generated_tokens'],'stop_reason':t['stop_reason'],'scientific_invalid_final':not s['parseable'],**metrics})
 csvwrite(RUN/'per_family_metrics.csv',records)
 rby={(r['model_id'],r['sample_id'],r['base_count'],r['arm']):r for r in records}
 common=sorted(sid for sid in families if all(vby[sid,b]['certificate_status']=='CERT_1_TO_2' for b in [3,4,5,6]))
 effects=[];family_deltas=[]
 for mid in ['M1','M2']:
  for b in [3,4,5,6]:
   for group in ['CERT_1_TO_2','ALL_LEGAL','SHORTCUT_RETURN_1_TO_1','COMMON_CERT_INTERSECTION']:
    eligible=sorted(sid for sid in families if vby[sid,b]['certificate_status']!='INVALID_OR_UNRESOLVED' and (group=='ALL_LEGAL' or group=='COMMON_CERT_INTERSECTION' and sid in common or group==vby[sid,b]['certificate_status']))
    present=[sid for sid in eligible if all((mid,sid,b,a) in rby for a in ['CONTROL','SEPARATION'])]
    for metric in ENDPOINTS:
     ctrl=np.array([rby[mid,sid,b,'CONTROL'][metric] for sid in present],float);sep=np.array([rby[mid,sid,b,'SEPARATION'][metric] for sid in present],float);delta=sep-ctrl
     result=ci(delta,f'{mid}|{b}|{group}|{metric}')
     effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'SEPARATION_MINUS_CONTROL','planned_n':len(eligible),'completed_n':len(present),'control_numerator_sum':float(ctrl.sum()),'separation_numerator_sum':float(sep.sum()),'control_mean':float(ctrl.mean()) if len(ctrl) else None,'separation_mean':float(sep.mean()) if len(sep) else None,**result})
     if group=='COMMON_CERT_INTERSECTION' and b!=5:
      full=[sid for sid in present if all((mid,sid,5,a) in rby for a in ['CONTROL','SEPARATION'])]
      dd=np.array([(rby[mid,sid,b,'SEPARATION'][metric]-rby[mid,sid,b,'CONTROL'][metric])-(rby[mid,sid,5,'SEPARATION'][metric]-rby[mid,sid,5,'CONTROL'][metric]) for sid in full])
      effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'DELTA_BASE_MINUS_DELTA_BASE5',**ci(dd,f'{mid}|{b}|DID|{metric}')})
      if metric=='displayed_success':effects.append({'model_id':mid,'base_count':b,'cohort':group,'metric':metric,'contrast':'DELTA_BASE_MINUS_DELTA_BASE5_SIMULTANEOUS',**ci(dd,f'{mid}|{b}|DID|{metric}',True)})
    for sid in present:
     family_deltas.append({'model_id':mid,'sample_id':sid,'base_count':b,'cohort':group,**{m:rby[mid,sid,b,'SEPARATION'][m]-rby[mid,sid,b,'CONTROL'][m] for m in ENDPOINTS}})
 csvwrite(RUN/'paired_effects.csv',effects);csvwrite(RUN/'results/family_paired_differences.csv',family_deltas)
 oldbroader=read(A/'E1/extra_audit_results.json');write(RUN/'results/broader_original_immutable.json',oldbroader)
 write(RUN/'results/analysis_completeness.json',{'updated_utc':now(),'records_completed':len(records),'records_planned':1920,'new_completed':sum(r['origin']=='NEW_R1' for r in records),'base5_reused':sum(r['origin']=='CACHED_BASE5' for r in records),'common_cert_intersection_n':len(common),'common_cert_family_ids':common,'scientific_invalid_outputs':sum(r['scientific_invalid_final'] for r in records),'wall_seconds':time.perf_counter()-started,'complete':len(records)==1920,'independent_unit':'family','bootstrap_seed':20261107,'bootstrap_actual_stream':'PCG64(20261107); same sorted-family resampling stream reused jointly across endpoints/model/base with the same cohort; paired rows and differences resampled together','status':'COMPLETED' if len(records)==1920 else 'PARTIAL','common9_scope':'Original nine-example finite consistency includes original visible examples; original_unseen9 excludes originally shown examples and never promotes removed bases to new tests.'})
 print('ANALYSIS',len(records),'rows',len(effects),'effects','commonN',len(common),flush=True)
if __name__=='__main__':main()
