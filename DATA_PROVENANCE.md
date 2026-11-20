# Data provenance

## Task and output records

| Component | Origin and coverage |
| --- | --- |
| task families, variants, and certificates | Study-generated bounded string transformations and independently checked minimum-length certificates. The feeding-only proposal grammar follows PBEBench. |
| evaluation inputs | Shared, wholly unshown, uniform, and rule-active strings with executable reference outputs. |
| normalized trajectories | The study's archived Qwen and Olmo evaluations, including generation text, token IDs, and parser outputs. See the model contract and normalization record. |
| retrospective archive | The saved 1,008 configurations and outputs used to audit one-rule shortcuts. Source row digests and the original reference descriptions travel with the archive. The upstream sampling and filtering chain for this saved roster is unresolved in the paper and archive. |
| historical results | Earlier evidence summarized in the paper and the analysis history record. The reproduction scope lists the underlying records available in the release. |

[Model contract](data/model_contract.json) · [Normalization record](provenance/NORMALIZATION.json) · [Retrospective archive](data/native1008.csv) · [Coverage](RELEASE_SCOPE.txt)

## Model revisions

| Model | Revision |
| --- | --- |
| Qwen3-8B | [b968826d9c46dd6066d109eabc6255188de91218](https://huggingface.co/Qwen/Qwen3-8B/tree/b968826d9c46dd6066d109eabc6255188de91218) |
| Olmo-3-7B-Think | [d97e442d7cc678210054dbcc9b440894d62c89a4](https://huggingface.co/allenai/Olmo-3-7B-Think/tree/d97e442d7cc678210054dbcc9b440894d62c89a4) |

The model contract preserves model and tokenizer revisions, chat template source, prompt provenance, and generation settings. Model weights are obtained from the respective publishers under their terms. The replay uses archived outputs.

## PBEBench attribution and reuse

The three PBEBench source files in code/frozen match the following upstream paths byte for byte at commit b2312327558e81c947ed8b543001169075062491.

| Included path | Upstream path |
| --- | --- |
| code/frozen/PBEBench_functional_correctness.py | src/metrics/functional_correctness.py |
| code/frozen/PBEBench_primitives.py | src/data_generation/primitives.py |
| code/frozen/PBEBench_utils.py | src/data_generation/utils.py |

The portable native scoring adapter retains the benchmark's scoring definitions. The upstream MIT copyright notice applies to the distributed PBEBench code and those adaptations. Original study software is MIT-licensed. Original task constructions, numerical annotations and companion materials are under CC BY 4.0. The historical 1,008-task roster retains its upstream provenance limits; the author's grant covers the author's audit measurements. Model-generated material, external templates and third-party components retain their applicable upstream terms. [Public-edition scope](PUBLICATION.md). [PBEBench code revision](https://github.com/cmu-llab/PBEBench/tree/b2312327558e81c947ed8b543001169075062491) · [MIT notice](licenses/PBEBench-MIT.txt) · [Benchmark paper](https://aclanthology.org/2026.findings-acl.432/)
