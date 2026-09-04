# JLPT N2 官方资料入口

本目录用于获取并使用JLPT官方网站公开的N2练习资料。

## 为什么不把题目二进制文件提交到Git

官方页面允许在线查看／下载，但题目、阅读材料和听力音频受主办方及第三方版权保护。为避免在GitHub重新发布受版权保护的完整资料，仓库只提交：

- 官方来源与文件清单；
- 一键下载脚本；
- 教学使用规划。

下载后的PDF和MP3保存在本目录的 `downloads/` 中，供本地学习使用；该目录已被Git忽略。

## 获取方法

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\materials\official_n2\download_official_n2.ps1
```

脚本会下载：

- 2012官方练习册N2：词汇、语法、阅读、听力题册、答案、答题纸、听力原文、Q1～Q5音频；
- 2018官方练习册Vol.2 N2：同上。

下载完成后会生成本地SHA-256清单：`checksums.local.sha256`。

## 官方来源

- 官方练习册总页：https://www.jlpt.jp/e/samples/sampleindex.html
- 官方说明：2012版和2018版各自题量接近一次正式考试，题目选自2010年改版后实际使用过的试题。
- 官方版权说明：https://www.jlpt.jp/e/samples/sampleindex.html#anchor03

## 使用顺序

1. 9月：只用公开样题做题型侦察，不提前看这两套完整资料。
2. 11月上旬：2012版作为第一次接近完整强度的官方诊断。
3. 11月下旬：2018版Vol.2作为考前官方模拟。
4. 做完只记录题号、题型、错因和能力缺口，不把整题复制进进度文件。

