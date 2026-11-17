"""Frozen native scoring path; the sole alignment is empty-alpha identity."""
import re,types
from .common import VOCAB
from src.metrics import functional_correctness as native
from src.data_generation.primitives import ProgramBFCCNode

class PaperConstrainedNode(ProgramBFCCNode):
    @classmethod
    def from_string(cls,*args,**kwargs):
        node=super().from_string(*args,**kwargs)
        assert len(node.alpha)>0, 'paper forbids empty alpha'
        return node

_globals=dict(native.eval_outputs.__globals__)
_globals['ProgramBFCCNode']=PaperConstrainedNode
eval_outputs=types.FunctionType(native.eval_outputs.__code__,_globals,'paper_eval_outputs',native.eval_outputs.__defaults__)
def extract(text):
    return native.try_ast_literal_eval(native.extract_program_str_from_last_python_block(text))
def score(text,inputs,outputs):
    cascade=extract(text)
    predicted,valid,invalid=eval_outputs(inputs,outputs,cascade,VOCAB,5)
    reasons=[]
    for item in cascade[:5]:
        if not isinstance(item,str): reasons.append('NON_STRING_RULE'); continue
        try:
            node=PaperConstrainedNode.from_string(item,vocabulary=native.ProgramVocabulary(VOCAB))
        except (AssertionError,IndexError) as exc:
            reasons.append(str(exc) or type(exc).__name__)
    return {'pass_at_1':int(predicted==outputs),'predicted_outputs':predicted,'predicted_cascade':cascade,'valid_rules':valid,'invalid_rules':invalid,'invalid_rule_reasons':reasons,'complete_python_block_found':bool(re.search(r'```python\s(.*?)```',text,re.S)),'empty_cascade':not cascade}
