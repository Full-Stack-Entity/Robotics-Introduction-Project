# SAPIEN Phase 1 基础任务产物

控制链路：`Cartesian target -> MPlib IK -> Franka Panda qpos -> SAPIEN URDF rendering`。

| 任务 | 帧数 | 最大末端误差 (m) | 视频 | 轨迹图 | CSV |
| --- | ---: | ---: | --- | --- | --- |
| 六点空间点位控制 | 176 | 0.00001033 | `outputs/sapien/videos/six_points.mp4` | `outputs/sapien/plots/six_points_trajectory.png` | `outputs/sapien/logs/six_points_trajectory.csv` |
| 8 字形末端轨迹 | 180 | 0.00001016 | `outputs/sapien/videos/figure_eight.mp4` | `outputs/sapien/plots/figure_eight_trajectory.png` | `outputs/sapien/logs/figure_eight_trajectory.csv` |
| 椭圆末端轨迹 | 180 | 0.00001016 | `outputs/sapien/videos/ellipse.mp4` | `outputs/sapien/plots/ellipse_trajectory.png` | `outputs/sapien/logs/ellipse_trajectory.csv` |

本地浏览器回放：

```bash
xdg-open outputs/sapien/viewer.html
```

实时浏览器预览：

```bash
pixi run sapien-basic-live
```
