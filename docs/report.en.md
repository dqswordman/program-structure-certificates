# When does an example force a second rule?

Wenzhang Du · arXiv:2611.24975v1 · v1.0 · 2026-11-20

A model can explain every demonstration with a shortcut. One carefully chosen example lets us certify when that shortcut disappears, then measure what the model does on the task and on new strings.

## Change one example, keep the reference program

Imagine inferring a program from six input–output pairs. Five pairs are shared. In the control, the last pair maps iiiexa to iiiazy. The single replacement exa → azy fits all six. The same observations also admit a two-step explanation: replace ex with azw, then wa with y.

In the matched separation task the final pair becomes wbawex → wbayzw. The shortcut leaves wbawex unchanged. The two-step program produces wbawazw after its first rule and wbayzw after its second. All other demonstrations stay fixed. The figure traces both explanations on this archived task.

![Worked example comparing the control and separation demonstrations and the one- and two-rule programs.](figures/construction.png)

Figure 1. Both tasks use the same two-rule reference. The final demonstration determines whether a one-rule solution remains possible.

## What the certificate proves

Here a rule replaces every non-overlapping occurrence of a literal string. Rules run in sequence. The study fixes a finite alphabet, a left-hand side of one to three characters and a right-hand side of up to three. A changed output rules out the empty program. The verifier enumerates the legal one-rule explanations and executes a two-rule witness.

For this example one single-rule program survives in the control and none survives in separation. The successful witness gives an upper bound of two, so the minimum lengths are exactly one and two. Certification uses the displayed pairs before inference. This statement depends on the chosen language and rule lengths.

## Solving the prompt and passing the hidden pair

Each of the 120 reference families supplies matched control and separation tasks with three to six shared examples, plus one arm-specific example. The panel contains 1,440 new trajectories and 480 previously saved base-five trajectories for Qwen3-8B and Olmo-3-7B-Think. The certified comparison uses 119 families at bases three and four and all 120 at bases five and six.

With five shared examples, Qwen completes 67 of 120 control tasks and 12 separation tasks. Olmo completes 52 and 15. In both models, success on a separate witness pair hidden from both prompts increases. The table uses separation minus control in percentage points and paired, pointwise 95% intervals for this panel.

| Model | Displayed, control → separation | Displayed Δ (pp) | Hidden pair Δ (pp) |
| --- | --- | --- | --- |
| Qwen3-8B | 67 → 12 / 120 | −45.83 [−55.00, −36.67] | +9.17 [+4.17, +15.00] |
| Olmo-3-7B-Think | 52 → 15 / 120 | −30.83 [−40.83, −20.83] | +11.67 [+6.67, +17.50] |

Five shared examples plus the changed example. Across all eight model and base-count settings, the displayed effect ranges from −45.83 to −23.53 points and the hidden-pair effect from +8.40 to +13.45.

## What happens on other strings?

The hidden pair was chosen to distinguish programs. A second evaluation draws 32 uniform strings and 32 strings that activate both reference rules for each family. Uniform-input agreement falls in every model and base-count setting. Of the 3,840 uniform inputs, 3,325 map to themselves under the reference.

On the rule-active inputs the absolute agreement of separation programs is only 1.93–5.78%. At base five, Qwen reaches 2.76% and Olmo 2.01%. A gain on targeted witnesses therefore supports a narrower conclusion than recovering the reference transformation across inputs.

## An unchanged output can rule out a shortcut

In a separate archived family, the reference first replaces f with fdd and then db with c. The pair iyxbdc → iyxbdc looks uneventful. A competing rule b → dc predicts iyxdcdc. Keeping this identity example excludes that candidate; removing it at the smaller base counts lets a one-rule solution return. This family was selected from its certificate transition before inspecting the model outcomes.

## Replay the evidence

Extract the release, enter its top-level folder and run the first two commands with Python 3.11 or later. The third uses NumPy and writes to a new directory. It verifies 960 certificates, 7,680 reference labels and the saved programs, then compares the three reconstructed tables with their archived counterparts.

The release supplies normalized trajectories, task specifications and executable checks. Earlier discovery and timed-search studies have separate coverage in the result map. The historical sampling chain of the 1,008-task retrospective roster remains unresolved. The companion reports the scope of those records separately from the matched 120-family experiment.

```sh
python -B verify_manifest.py
python -B replay_fixture.py
python -B reproduce.py --out replay
```

## Sources

- [Paper and version history · arXiv](https://arxiv.org/abs/2611.24975)
- [Version 1 with appendix · HTML](https://arxiv.org/html/2611.24975v1)
- [Figure 1 executable fixture](https://github.com/dqswordman/program-structure-certificates/blob/v1.0.0/fixtures/end_to_end.json)
- [Primary and witness effects](https://github.com/dqswordman/program-structure-certificates/blob/v1.0.0/results/PRIMARY_PANEL_READABLE.csv)
- [Uniform and active input panel](https://github.com/dqswordman/program-structure-certificates/blob/v1.0.0/results/BROADER_PANEL_READABLE.csv)
- [Identity-example certificate](https://github.com/dqswordman/program-structure-certificates/blob/v1.0.0/worked_case.json)
- [Paper-to-artifact result map](https://github.com/dqswordman/program-structure-certificates/blob/v1.0.0/docs/result-map.csv)
- [Interactive certificate explorer](https://huggingface.co/spaces/DQSWORDMAN/program-structure-certificates)
