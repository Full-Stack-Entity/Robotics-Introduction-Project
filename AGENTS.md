# AGNETS.md

## 项目简介
- 项目用途：机器人学导论的期末仿真作业的文件夹
- 技术栈：使用SAPIEN仿真软件编写控制程序完成基础任务并进行GUI画面展示，展示传统机器人学方法；基于RoboTwin2.0框架进行数据生成和具身智能模型训练并在多种任务上开展评测，展示成功rollout录像/评测实时效果展示，代表现代具身智能

## 启动与开发命令

- 依赖配置：与python相关的依赖一般在主目录使用pixi进行环境配置，遇到环境冲突可以修改pixi.toml或者使用pixi add 命令增加依赖，特殊情况下可以在得到许可后使用apt命令安装依赖
- 本地运行：通过pixi shell进入环境，或者使用pixi run 运行脚本
- 测试：无要求
- 构建：无要求

  ## 代码结构说明
  - `src/`：核心代码
  - `output/`：输出内容的存放位置
  - `report/`：撰写实验报告的文件夹
  - `reference/`:实验的参考资料
  - `tests/`：测试
  - `scripts/`：辅助脚本

## 代码规定

- 如果使用matplotlib进行绘图，使用font_manager访问中文字体，本地可用的中文字体有"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"，"/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

## 工作流程

- 无要求

## 限制情况与行为

- 任何情况下不要在主环境使用pip、conda等命令进行环境配置（对于某些pixi实在处理不了的依赖，可以允许在pixi环境下使用pip进行安装）
- 任何删除非你生成的文件的操作都要征求我的同意并告知我删除的文件的内容

## 协作规则

- 遇到冲突、不确定、有多种选择的情况：先和我讨论可行的方案，阐明优缺点，我再从中选择
