# JLPT N2 学习目录使用说明

## 每天怎么用

在本目录启动 Codex。

第一次可以执行 `/init`，但本目录已经提供了 `AGENTS.md`，请检查不要让自动生成内容覆盖现有学习规则。

然后输入：

`开始今天的 N2 学习。`

更稳妥的完整启动语在 `START_PROMPT.md`。

## 文件职责

- `AGENTS.md`：固定教学规则。短小、长期稳定。
- `CURRENT_STATE.md`：当前状态唯一权威来源。每次必读。
- `REVIEW_QUEUE.md`：今天到期的间隔复测。
- `JLPT_N2_MASTER.md`：完整知识地图和 94 天路线。按需读取，不必每次全读。
- `N2_OFFICIAL_BLUEPRINT.md`：官方题型、量尺得分、真题使用和阶段检查点。
- `materials/official_n2/`：官方资料来源与可重复下载工具；受版权保护的PDF／MP3只保存在Git忽略的本地目录。
- `progress/`：每日详细日志。
- `mistakes/ACTIVE_MISTAKES.md`：仍可能重复犯的错误。
- `archive/`：已经解决的旧信息。

## 核心思想

聊天上下文可以丢。

文件状态不能丢。

只要 `CURRENT_STATE.md + REVIEW_QUEUE.md + ACTIVE_MISTAKES.md` 被正确维护，
即使每天开一个全新的 Codex 会话，也应该可以恢复学习。
