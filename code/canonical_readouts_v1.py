"""Prospective reference readouts for NECESSARY_STRUCTURE_PILOT_02.
Native PILOT_01 scores are immutable. This module uses no learned judge, arbitrary
code execution, reference program, hidden tests, or answer-dependent final selection.
All verification is against the finite, prompt-visible I/O specification.
"""
from __future__ import annotations
import ast
import re
from typing import Optional, Sequence
VOCAB=frozenset('abcdefghijkuvwxyz')
LIST_SPAN=re.compile(r'\[[^\[\]]{1,1800}\]',re.S)
FENCED=re.compile(r'```python\s+(.*?)```',re.S)
NOTATION=re.compile(r'^([abcdefghijkuvwxyz]{1,3})\s*(?:->|:|,)\s*([abcdefghijkuvwxyz]{0,3})$')
EOS=re.compile(r'(?:<\|endoftext\|>|<\|im_end\|>|<\|eot_id\|>)\s*$')
Rules=list[tuple[str,str]]

def parse_rule(rule: str)->Optional[tuple[str,str]]:
    if not isinstance(rule,str):return None
    m=NOTATION.fullmatch(rule.strip())
    if m:return m.group(1),m.group(2)
    try:
        node=ast.parse(rule.strip(),mode='eval').body
        if not (isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='replace' and len(node.args)==2 and not node.keywords):return None
        a,b=(ast.literal_eval(x) for x in node.args)
        if not isinstance(a,str) or not isinstance(b,str) or not 1<=len(a)<=3 or len(b)>3 or not set(a+b)<=VOCAB:return None
        return a,b
    except (ValueError,SyntaxError,TypeError,RecursionError):return None

def parse_list(text: str)->Optional[Rules]:
    if len(text)>1800:return None
    try:
        seq=ast.literal_eval(text.strip())
        if not isinstance(seq,list) or not 1<=len(seq)<=5 or not all(isinstance(r,str) for r in seq):return None
        rules=[parse_rule(r) for r in seq]
        return None if any(r is None for r in rules) else rules
    except (ValueError,SyntaxError,TypeError,RecursionError):return None

def apply(inputs: Sequence[str],rules: Rules)->list[str]:
    outputs=list(inputs)
    for a,b in rules:outputs=[s.replace(a,b) for s in outputs]
    return outputs

def final_rules(raw_text: str)->Optional[Rules]:
    """Select the last final-section block/list, WITHOUT consulting target outputs."""
    if '</think>' not in raw_text:return None
    final=EOS.sub('',raw_text.rsplit('</think>',1)[1]).strip()
    blocks=list(FENCED.finditer(final))
    if blocks:return parse_list(blocks[-1].group(1))
    spans=list(LIST_SPAN.finditer(final))
    return parse_list(spans[-1].group()) if spans else None

def readouts(raw_text: str,inputs: Sequence[str],outputs: Sequence[str])->dict:
    if len(inputs)!=len(outputs) or not inputs:raise ValueError('Nonempty paired specification required')
    selected=final_rules(raw_text)
    good=[]
    for m in LIST_SPAN.finditer(raw_text):
        r=parse_list(m.group())
        if r is not None and apply(inputs,r)==list(outputs):good.append({'char_end':m.end(),'rules':r})
    return {'canonical_final_correct':int(selected is not None and apply(inputs,selected)==list(outputs)),
            'canonical_final_parseable':selected is not None,'selected_final_rules':selected,
            'canonical_candidate_available':bool(good),'first_verified_candidate':good[0] if good else None,
            'candidate_count':len(good),'think_closed':'</think>' in raw_text}

def self_test()->dict:
    tests=0
    for text,expected in [("[\"replace('ab','c')\"]",[('ab','c')]),("['ab->c']",[('ab','c')]),("['ab,c']",[('ab','c')]),("['ab:c']",[('ab','c')]),("['a->']",[('a','')]),("[\"replace('','a')\"]",None),("[\"replace('l','a')\"]",None),("[\"replace('a','bbbb')\"]",None),("[\"replace(a='a',b='b')\"]",None),("[('a','b')]",None),("[]",None),(repr(['a->b']*6),None)]:
        assert parse_list(text)==expected,(text,parse_list(text));tests+=1
    xs=['ab','d'];ys=['c','d']
    for text,final,cand in [("Thinking ['ab->c']",0,True),("Thinking ['ab->c']</think>python\n['ab->c']<|endoftext|>",1,True),("Thinking ['ab->c']</think>```python\n['ab->a']\n```",0,True),("</think>```python\n['ab->c']\n```\n```python\n['ab->a']\n```",0,True),("</think>['ab->c'] then ['ab->a']",0,True),("</think>['ab->a']",0,False)]:
        r=readouts(text,xs,ys);assert r['canonical_final_correct']==final and r['canonical_candidate_available']==cand,(text,r);tests+=1
    r=readouts("</think>['ab->c']",['ab','ab'],['c','b']);assert r['canonical_final_correct']==0;tests+=1
    return {'status':'PASS','checks':tests,'role':'implementation fixtures, not scientific observations'}
if __name__=='__main__':
    import json
    print(json.dumps(self_test(),indent=2))
