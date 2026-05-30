# Video Segment Plan

Date: 2026-05-30

This is the first cut of the course presentation video plan. It selects stable
artifact paths and assigns narration points. Manual playback trimming can happen
later, but the evidence source for each segment is fixed here.

## Segment Sequence

| Order | Segment | Source artifact | Suggested duration | Narration focus | Evidence type |
| ---: | --- | --- | ---: | --- | --- |
| 1 | Project overview | `outputs/phase6_visual_index.md` | 20-30s | Explain two-part design: SAPIEN traditional control plus RoboTwin learned policy evaluation. | Structure |
| 2 | SAPIEN six-point control | `outputs/sapien/videos/six_points.mp4` | 20-30s | Cartesian targets are converted to Franka Panda joint motion through MPlib IK and rendered in SAPIEN. | Required control demo |
| 3 | SAPIEN figure-eight trajectory | `outputs/sapien/videos/figure_eight.mp4` | 20-30s | Show continuous end-effector trajectory tracking and mention max error from `outputs/sapien/summary.md`. | Required trajectory demo |
| 4 | SAPIEN ellipse trajectory | `outputs/sapien/videos/ellipse.mp4` | 15-25s | Show a second smooth trajectory and use the plot for report comparison. | Required trajectory demo |
| 5 | RoboTwin data generation: `grab_roller` | `outputs/robotwin/artifacts/data/grab_roller/demo_clean_100/video/episode0.mp4` | 10-15s | Expert demonstrations provide supervised trajectories for DP training. | Expert demo |
| 6 | RoboTwin data generation: `adjust_bottle` | `outputs/robotwin/artifacts/data/adjust_bottle/demo_clean_100/video/episode0.mp4` | 10-15s | Explain that every task has 100 clean-domain demonstrations. | Expert demo |
| 7 | RoboTwin data generation: `place_burger_fries` | `outputs/robotwin/artifacts/data/place_burger_fries/demo_clean_100/video/episode0.mp4` | 10-15s | Highlight the semantic pick-and-place nature of the task. | Expert demo |
| 8 | DP training result | `outputs/robotwin/summary/training_loss_curves.png` | 20-30s | Explain the final full-dataloader + EMA retraining profile and avoid claiming loss as task success. | Optimization evidence |
| 9 | Official eval success table | `outputs/robotwin/summary/final_success_rates.md` | 20-30s | Report final success rates: 100%, 71%, and 98%; distinguish official eval from single rollout. | Quantitative evidence |
| 10 | Learned rollout: `grab_roller` | `outputs/robotwin/single_rollouts/grab_roller/demo_clean_100_seed0_ckpt100_20260530-094826/episode0.mp4` | 20-30s | Show the final DP policy successfully completing the task. | Presentation rollout |
| 11 | Learned rollout: `adjust_bottle` | `outputs/robotwin/single_rollouts/adjust_bottle/demo_clean_100_seed0_ckpt100_20260530-105724/episode0.mp4` | 20-30s | Show the weaker but still successful presentation rollout; mention official eval is 71/100. | Presentation rollout |
| 12 | Learned rollout: `place_burger_fries` | `outputs/robotwin/single_rollouts/place_burger_fries/demo_clean_100_seed0_ckpt100_20260530-121045/episode0.mp4` | 20-30s | Use as the strongest RoboTwin visual example and report 98/100 official eval. | Presentation rollout |
| 13 | Closing | `outputs/robotwin/summary/phase5_eval_summary.md` | 20-30s | Summarize that Phase5 is complete and Phase6 artifacts are ready for report/PPT. | Conclusion |

## PPT Mapping

| PPT section | Primary assets |
| --- | --- |
| Task requirements and environment | `outputs/environment.md`, `outputs/command_log.md` |
| SAPIEN control method | `outputs/sapien/viewer.html`, SAPIEN videos and trajectory plots |
| RoboTwin data and training | `outputs/robotwin/summary/phase3_data_summary.md`, expert demo clips, `training_loss_curves.png` |
| Evaluation and results | `outputs/robotwin/summary/final_success_rates.md`, `outputs/robotwin/summary/phase5_eval_summary.md` |
| Demo clips | Three `outputs/robotwin/single_rollouts/.../episode0.mp4` final ckpt100 videos |

## Manual Follow-Up Before Recording

- Open each selected mp4 once and choose exact start/end timestamps for the
  final edited video.
- Keep official eval results as table narration; do not show a single rollout as
  if it were a 100-trial success-rate proof.
- For `adjust_bottle`, explicitly say the final official result is 71/100 even
  though the selected presentation rollout succeeded.

