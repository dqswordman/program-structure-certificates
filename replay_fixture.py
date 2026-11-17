#!/usr/bin/env python3
"""Check the Figure 1 task pair and four saved base-five outputs using only CPU.

Run from the extracted package root: python -B replay_fixture.py
No model, tokenizer, network access, or new model generation is used.
"""
from pathlib import Path
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
import canonical_readouts_v1 as canonical


def load_lines(path: Path) -> list[dict]:
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def complete_one_rules(inputs: list[str], outputs: list[str]) -> list[list[str]]:
    """Enumerate all solutions using the nonidentity-anchor completeness lemma."""
    anchor = next((i for i, (x, y) in enumerate(zip(inputs, outputs)) if x != y), None)
    if anchor is None:
        raise ValueError('Fixture enumeration requires a nonidentity example.')
    def pieces(text: str) -> set[str]:
        return {text[i:i+k] for k in (1, 2, 3) for i in range(len(text)-k+1)}
    return [list(rule) for rule in sorted(
        (a, b) for a in pieces(inputs[anchor])
        for b in pieces(outputs[anchor]) | {''}
        if all(x.replace(a, b) == y for x, y in zip(inputs, outputs))
    )]


def run_fixture() -> dict:
    fixture = json.loads((ROOT / 'fixtures/end_to_end.json').read_text(encoding='utf-8'))
    sid, base = fixture['sample_id'], fixture['base_count']
    family = next(x for x in load_lines(ROOT / 'data/families.jsonl') if x['sample_id'] == sid)
    variant = next(x for x in load_lines(ROOT / 'data/base_variants.jsonl')
                   if x['sample_id'] == sid and x['base_count'] == base)
    if fixture['task_pair'] != {arm: {k: variant['arms'][arm][k] for k in ('inputs', 'outputs')}
                                for arm in ('CONTROL', 'SEPARATION')}:
        raise ValueError('Fixture specification differs from the saved variant.')
    reference = [tuple(pair) for pair in fixture['reference_rule_pairs']]
    certificates = {}
    for arm in ('CONTROL', 'SEPARATION'):
        task = variant['arms'][arm]
        solutions = complete_one_rules(task['inputs'], task['outputs'])
        if solutions != sorted(task['one_rule_solutions']):
            raise ValueError(f'{arm}: one-rule solutions differ from the saved certificate.')
        if canonical.apply(task['inputs'], reference) != task['outputs']:
            raise ValueError(f'{arm}: reference fails the specification.')
        minimum = 1 if solutions else 2
        if minimum != task['minimum_length']:
            raise ValueError(f'{arm}: minimum-length certificate mismatch.')
        certificates[arm] = {'complete_one_rule_solutions': solutions,
                             'minimum_length': minimum, 'two_rule_reference_passes': True}
    target_rows = [x for x in load_lines(ROOT / 'data/broader_inputs.jsonl') if x['sample_id'] == sid]
    targets = {x['stratum']: x['accepted'] for x in target_rows}
    other = family['witness_pairs'][2-family['displayed_witness_index']]
    common = list(zip(family['original_inputs'], family['original_outputs']))
    common += [(pair[k]['input'], pair[k]['output'])
               for pair in family['witness_pairs'] for k in ('control', 'separation')]
    unshown = [(other[k]['input'], other[k]['output']) for k in ('control', 'separation')]
    requested = set(fixture['request_ids'])
    outputs = {}
    with gzip.open(ROOT / 'data/trajectories.jsonl.gz', 'rt', encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            key = record['request_id']
            if key not in requested:
                continue
            selected = canonical.final_rules(record['raw_text'])
            normalized = [list(pair) for pair in selected] if selected is not None else None
            if normalized != record['selected_final']['rules']:
                raise ValueError(f'{key}: selected program mismatch.')
            task = variant['arms'][record['arm']]
            def hits(pairs: list[tuple[str, str]]) -> int:
                return sum(selected is not None and canonical.apply([x], selected) == [y]
                           for x, y in pairs)
            evaluation = {'displayed': list(zip(task['inputs'], task['outputs'])),
                          'common_nine': common, 'wholly_unshown_pair': unshown,
                          **{name.lower(): [(p['input'], p['output']) for p in pts]
                             for name, pts in targets.items()}}
            outputs[key] = {
                'selected_rules': normalized,
                'legal_selected_program': selected is not None,
                'targets': {name: {'hits': hits(pairs), 'inputs': len(pairs),
                                   'all_pass': hits(pairs) == len(pairs)}
                            for name, pairs in evaluation.items()}}
    if set(outputs) != requested:
        raise ValueError('Missing requested saved model output.')
    return {'status': 'PASS', 'family': sid, 'base_count': base,
            'certificates': certificates, 'saved_outputs': outputs, 'model_inference_calls': 0}


def main() -> int:
    try:
        expected = json.loads((ROOT / 'fixtures/end_to_end.json').read_text())['expected']
        actual = run_fixture()
        if actual != expected:
            raise ValueError('Fixture results differ from the recorded expected output.')
        print(json.dumps(actual, indent=2))
        return 0
    except (OSError, KeyError, ValueError, StopIteration) as exc:
        print(f'Fixture verification failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
