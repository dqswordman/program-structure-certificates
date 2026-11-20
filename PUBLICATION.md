# Public edition · November 2026

**When Is Program Structure Required? Certificate-Grounded Calibration of Program-Induction Difficulty**

Wenzhang Du · arXiv:2611.24975v1 · submitted 17 November 2026.

[Paper · arXiv:2611.24975](https://arxiv.org/abs/2611.24975) · [Technical report](https://dqswordman.github.io/technical-reports/program-structure-certificates/) · [中文伴读](https://dqswordman.github.io/zh/technical-reports/program-structure-certificates/) · [Interactive Space](https://huggingface.co/spaces/DQSWORDMAN/program-structure-certificates)

The scientific artifact is tagged `v1.0.0` at `8b0f2e0dd17ee36ce9233a9053dc55c22110dfce`. The single ZIP combines that exact tagged tree with this public-edition note, the reuse notices and the English and Chinese companions. The original 49-file manifest verifies the frozen contents. `PUBLICATION_MANIFEST.json` records the source revision and checksums of the public-edition additions. The repository default branch also catalogs the live publication links.

- [Read the English companion offline](docs/report.en.md) or [read it in Chinese](docs/report.zh.md).
- Run `python -B verify_manifest.py` and `python -B replay_fixture.py` from the extracted folder.
- With Python 3.11+ and NumPy, run `python -B reproduce.py --out replay` with a new output directory. The archived inputs regenerate the three primary CSVs on CPU. [Reproduction guide](docs/reproduction.md)
- Cite the preprint and the v1.0.0 research artifact. [Paper](https://arxiv.org/abs/2611.24975) · [Release](https://github.com/dqswordman/program-structure-certificates/releases/tag/v1.0.0)

## Reuse

Original software by Wenzhang Du is available under the [MIT License](LICENSE). The author's original synthetic tasks, numerical measurements, companion text and original figures are available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit Wenzhang Du, identify the source, link the license and indicate modifications. A local copy of the [data and documentation license](licenses/CC-BY-4.0.txt) is included.

The PBEBench files and adaptations carry their [upstream MIT notice](licenses/PBEBench-MIT.txt). Archived model-generated text, token records, model templates and other third-party material retain their applicable upstream terms. The 1,008-row retrospective roster is included as a separately identified historical audit input; its sampling and filtering chain is unresolved. The CC grant covers the author's own recorded audit measurements, with upstream rights reserved in any underlying material. The release contains no model weights. [Data provenance](DATA_PROVENANCE.md)
