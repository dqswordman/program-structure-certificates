# When Is Program Structure Required? Certificate-Grounded Calibration of Program-Induction Difficulty

Wenzhang Du · Independent Researcher, China

A generator can use two string-replacement rules even when the displayed examples admit a one-rule solution. This artifact follows a matched pair of specifications through complete one-rule enumeration, executable two-rule witnesses, and the programs returned by language models.

[Reproduction guide](docs/reproduction.md) · [Result map](docs/result-map.csv) · [Data provenance](DATA_PROVENANCE.md) · [Frozen artifact v1.0.0](https://github.com/dqswordman/program-structure-certificates/tree/v1.0.0)

## Follow one archived task pair

From the repository root with Python 3.11 or newer:

    python -B verify_manifest.py
    python -B replay_fixture.py

The fixture checks the six-example pair in Figure 1. The control admits the single replacement from exa to azy. The separation example excludes that rule, and the shared two-rule reference satisfies both specifications. The command reports certified minima of **one** and **two**, then executes four saved Qwen and Olmo programs on the displayed, witness, uniform, and rule-active inputs. It uses the included archive and the Python standard library.

[![Three-panel example showing how changing one input-output example excludes the one-rule control solution.](docs/figures/construction.png)](docs/figures/construction.pdf)

## Results at a glance

Across both models and the three-to-six base-example settings, the certified separation tasks reduce displayed-task completion by **23.53 to 45.83 percentage points** and increase exact success on the wholly unshown witness pair by **8.40 to 13.45 points**. Agreement on strings activating both reference rules ranges from **1.93% to 5.78%** in the separation conditions. The archived tables distinguish these evaluation targets. [Primary panel](results/PRIMARY_PANEL_READABLE.csv) · [Broader-input panel](results/BROADER_PANEL_READABLE.csv)

## Replay the panel

Create an environment with NumPy, then run the full CPU check from the frozen tag:

    python -m pip install -r requirements.txt
    python -B reproduce.py --out replay

This reads **1,920 saved outputs**, checks **960 certificates** and **7,680 additional reference labels**, and regenerates the three comparison CSVs. The result map marks which historical analyses are available as aggregate tables and protocols. [Full instructions](docs/reproduction.md) · [Verification report](docs/reproduction_report.json)

## Citation

Cite Wenzhang Du, *When Is Program Structure Required? Certificate-Grounded Calibration of Program-Induction Difficulty*, for the research. For the archived observations or CPU replay, cite the versioned research artifact described in [CITATION.cff](CITATION.cff). [Version record](docs/release-manifest.json)
