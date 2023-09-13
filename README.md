# Bilibili视频弹幕分析可视化工具

该工具的分析原理是用特定的关键字搜索Bilibili，从默认排序的搜索结果中拉取多个视频的弹幕数据，随后输出弹幕云图并统计数量位于前20的弹幕。

# 模块构成

本工具主要由两大模块组成：`danmaku_db`和`analyzer_server`。其中，`analyzer_server`对外提供Web API接口以及调用该接口的UI页面，而`danmaku_db`负责调用Bilibili API获取视频弹幕数据并输出数据分析结果。

# 构建

在构建前请确保你已经安装了Python3.x以及Node.js。

在本文档所在目录下执行下列命令：
```shell
cd 022104120
pip install -r requirements.txt
cd visualizer_ui
npm i
npm run build
```
这样就构建完毕了。

要运行该工具，你需要在`022104120`目录下执行这条命令：
```shell
python main.py
```