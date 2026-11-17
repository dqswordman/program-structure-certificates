"""Portable native scorer: verbatim used definitions from the archived scientific sources.
The source files are retained in code/frozen. Only imports/namespace binding are adapted.
No generated program is executed as Python code.
"""
import ast, re, types
from typing import Union
VOCAB="abcdefghijkuvwxyz"

class ProgramVocabulary(set):
    """The set of characters used for creating predicate (input) and 
    transform (output) windows where a given program operates
    """
    def __init__(self, *args, **kwargs):
        if len(args) > 2: # just some syntax sugar.
            super().__init__(list(args))
        else: super().__init__(*args, **kwargs)

    def __str__(self):
        return "".join(list(self))
    
    def __repr__(self):
        return "".join(list(self))

    def has_word(self, word: str):
        word_vocab = set(list(word.strip()))
        
        return word_vocab.issubset(self)

class ProgramBFCCNode:
    """Abstract representation of program in the BFCC interaction graph."""
    def __init__(self, predicate: str, transform: str, vocabulary: ProgramVocabulary=ProgramVocabulary('a','b','c','d','e','f'), max_window_size: int=3):
        self.predicate = predicate
        self.transform = transform
        self.vocabulary = vocabulary
        self.max_window_size = max_window_size

    @property
    def alpha(self):
        return self.predicate
    
    @property
    def beta(self):
        return self.transform

    @classmethod
    def from_string(cls, string_repr: str, max_window_size: int=3, vocabulary: ProgramVocabulary=ProgramVocabulary('a','b','c','d','e','f')):
        self = cls("","")
        self.vocabulary = vocabulary
        self.max_window_size = max_window_size
        assert string_repr.strip() != '', "passed blank program input"
        assert 'replace(' in string_repr, f"replace function not found in program string: {string_repr}"
        
        # extract predicate and transform
        predicate = string_repr.split("replace(")[-1].split(",")[0].strip()
        transform = string_repr.split("replace(")[-1].split(",")[1].split(")")[0].strip()

        # strip quotations off
        predicate = predicate.replace("'","").replace('"','')
        transform = transform.replace("'","").replace('"','')
        # print("predicate:", predicate)
        # print("transform:", transform)
        
        # restrict the length of predicate and transform windows (no. of characters in them).
        assert len(predicate) <= self.max_window_size, f"predicate has more than {self.max_window_size} characters: {predicate} in ({string_repr})"
        assert len(transform) <= self.max_window_size, f"transform has more than {self.max_window_size} characters: {transform} in ({string_repr})"
        
        # restrict the vocabulary of predicates and transforms.
        assert self.vocabulary.has_word(predicate), f"the predicate {predicate} has some symbols not in the vocabulary: {self.vocabulary}" 
        assert self.vocabulary.has_word(transform), f"the transform {transform} has some symbols not in the vocabulary: {self.vocabulary}" 

        self.predicate = predicate
        self.transform = transform

        return self
    
    def __call__(self, inputs: list[str]) -> list[str]:
        outputs: list[str] = []
        for input in inputs:
            output = input.replace(self.predicate, self.transform)
            outputs.append(output)

        return outputs

    def __eq__(self, other):
        return self.predicate == other.predicate and self.transform == other.transform

    def __repr__(self):
        return f'replace("{self.predicate}", "{self.transform}")'
    
    def __str__(self):
        return self.__repr__()

def identity(x: list[str]) -> list[str]: return x

def eval_outputs(
        inputs: list[str], outputs: list[str], 
        pred_cascade: list[Union[str, ProgramBFCCNode]], 
        vocab_chars: str="abcdefghijkuvwxyz", max_programs: int=5):
    pred_outputs: list[str] = [i for i in inputs]
    valid_programs = 0
    invalid_programs = 0
    for program in pred_cascade[:max_programs]: # we should only pick the first max_programs (m in the paper) programs predicted by the model in the cascade (in case the model disobeys the instruction and uses more programs than max_programs)
        if isinstance(program, str):
            try: 
                program = ProgramBFCCNode.from_string(program, vocabulary=ProgramVocabulary(vocab_chars))
                valid_programs += 1
            except IndexError as e:
                # print(f"\x1b[31;1m{e}\x1b[0m")
                program = identity
                invalid_programs += 1
            except AssertionError as e:
                # print(f"\x1b[31;1m{e}\x1b[0m")
                program = identity # replace invalid programs with identity programs.
                invalid_programs += 1
        else: 
            # assert isinstance(program, ProgramBFCCNode), f"Invalid program type: {type(program)}"
            # print(f"\x1b[31;1mInvalid program type: {type(program)}. Replacing with identity. Check if this isn't the result of WRONG FORMATTING!!!\x1b[0m")
            program = identity
            invalid_programs += 1
        pred_outputs: list[str] = program(pred_outputs)
    
    return pred_outputs, valid_programs, invalid_programs

def extract_last_python_block(markdown_text: str) -> str:
    """
    Extracts first Python code block from a markdown string.

    Args:
        markdown_text (str): The markdown text containing code blocks.

    Returns:
        List[str]: A list of Python code blocks.
    """
    code_block_pattern = r"```python\s(.*?)```"
    matches = re.findall(code_block_pattern, markdown_text, re.DOTALL)
    try: return [block.strip() for block in matches][-1]
    except IndexError: return "[]"

def extract_program_str_from_last_python_block(model_response: str) -> str:
    try: pred = extract_last_python_block(model_response) 
    except TypeError as e:
        if model_response is None: pass
        else: print(e)
        pred = "replace('x','x')"

    # wrap any replace(...) that isn’t already quoted in single quotes
    # e.g.  replace('kd','ka')  →  'replace('kd','ka')'
    pred = re.sub(
        r"(?<!['\"])(replace\([^)]*\))(?!['\"])",
        r'"\1"',
        pred
    )

    return pred

def try_ast_literal_eval(string): # do some minor fixes.
    """Takes program sequence string and returns the extracted sequence of actual replace programs."""
    try:
        try: 
            program_seq = ast.literal_eval(string)
            if isinstance(program_seq, str):
                program_seq = [program_seq] 
            # print(program_seq, type(program_seq))
            try: 
                assert isinstance(program_seq, list), f"program sequence of list form couldn't be extracted or derived: {program_seq}"
                return program_seq
            except AssertionError: return []
        except ValueError: return []
    except SyntaxError: return []

native=types.SimpleNamespace(eval_outputs=eval_outputs, try_ast_literal_eval=try_ast_literal_eval, extract_program_str_from_last_python_block=extract_program_str_from_last_python_block, ProgramVocabulary=ProgramVocabulary)

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
