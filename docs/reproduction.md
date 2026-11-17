# Reproduction

Use [v1.0.0](https://github.com/dqswordman/program-structure-certificates/tree/v1.0.0) for the frozen research artifact. Run the commands from the repository root.

## Quick check

Python 3.11 or newer suffices for both commands.

    python -B verify_manifest.py
    python -B replay_fixture.py

Both print PASS. The fixture prints the certificate minima for the Figure 1 task pair, and the displayed, witness, uniform, and rule-active successes of four archived programs. The fixture starts from the exact task strings, checks each selected program against the stored parser output, and rebuilds the evaluation counts.

## Full replay

The validated environment used Python 3.12.7 and NumPy 1.26.4. Install the NumPy dependency in your environment before replay.

    python -m pip install -r requirements.txt
    python -B reproduce.py --out replay

Choose a new output directory each time. The replay enumerates **960** certificates for **480** pairs, checks all **7,680** wider reference labels and both rules' activation on the **3,840** active inputs, then recertifies the **1,008** archived tasks. It reconstructs **1,920** per-trajectory rows, **348** paired-effect rows, and **2,872** family-difference rows. Each CSV is compared with its archived counterpart under results/. Expected status and file digests appear in [the verification report](reproduction_report.json).

The full replay uses text and selected programs from precomputed trajectories. Model checkpoints and neural inference are outside this replay. The generation protocol and exact model revisions are in [the model contract](../data/model_contract.json).

## Paper coverage

The base-count panel uses shared family IDs and the original paired-family analysis. At bases three and four the certified cohort contains 119 families, while at bases five and six it contains 120. The base-five point estimates for Qwen and Olmo correspond to the original held-out evaluation. The original adjusted intervals and the historical studies listed in [release scope](../RELEASE_SCOPE.txt) are documented separately. [Result map](result-map.csv) · [Readout and bootstrap contract](../data/analysis_contract.json)
