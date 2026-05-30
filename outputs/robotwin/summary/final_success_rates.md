# Final RoboTwin Success Rates

Date: 2026-05-30

## Evaluation Setup

- Policy: Diffusion Policy (`DP`)
- Task config: `demo_clean_100`
- Checkpoint setting: `demo_clean_100`
- Expert data per task: `100`
- Seed: `0`
- Instruction type: `unseen`
- Final checkpoint number: `100`
- Final evaluation command: `CHECKPOINT_NUM=100 pixi run robotwin-phase5-eval`

The final checkpoints were trained with:

```bash
TRAIN_EPOCHS=100 \
CHECKPOINT_EVERY=100 \
BATCH_SIZE=16 \
MAX_TRAIN_STEPS=null \
MAX_VAL_STEPS=null \
USE_EMA=True \
pixi run robotwin-phase4-train
```

## Final Official Results

| Task | Final official success | Earlier capped-training result | Absolute change | Evidence |
| --- | ---: | ---: | ---: | --- |
| `grab_roller` | 100/100 = 100% | 90% | +10 pp | `outputs/robotwin/artifacts/eval_result/grab_roller/DP/demo_clean_100/demo_clean_100/2026-05-30 09:20:46/_result.txt` |
| `adjust_bottle` | 71/100 = 71% | 49% | +22 pp | `outputs/robotwin/artifacts/eval_result/adjust_bottle/DP/demo_clean_100/demo_clean_100/2026-05-30 09:49:09/_result.txt` |
| `place_burger_fries` | 98/100 = 98% | incomplete; 0 successes before interruption | not comparable | `outputs/robotwin/artifacts/eval_result/place_burger_fries/DP/demo_clean_100/demo_clean_100/2026-05-30 10:58:14/_result.txt` |

## Interpretation

- The earlier `MAX_TRAIN_STEPS=100` profile was a useful debugging profile but
  underfit the longer/harder tasks and mismatched the full dataloader schedule.
- The final full-dataloader + EMA profile fixed the main failure mode:
  `place_burger_fries` moved from no observed success before interruption to
  98/100 official eval success.
- `adjust_bottle` remains the weakest final task at 71/100, but it is a clear
  improvement over 49/100 and is sufficient as a course demonstration result.
- `grab_roller` and `place_burger_fries` are the strongest video/report anchors.

## Reporting Rule

Use this table for quantitative results. Use the custom single-rollout videos
only as qualitative presentation evidence.

