# 固定预算下的组合覆盖与故障检出

Soma · 使用 GPT 6.2 辅助完成 · 2026-11-26 · 未经同行评审

[阅读中文论文（PDF）](paper/paper-zh.pdf) · [查看 12 项最优配置](lower/settings.csv) · [复核完整穷举](upper/UPPER.md)

在 JHipster 3.6.1 的固定 14 字段模型中，12 种配置的二项覆盖最优值是 642。在独立的 MinePump 基准上，两份清单都测 12 种配置，都覆盖了全部 60 个可行二项组合。第一份漏掉了全部八个历史失败配置，第二份命中全部八个。四个外部基准的精确端点和验证程序见[外部验证报告](transfer/README.md)。全部实验均是回顾性研究。“失败配置数”“失败事件数”“故障类别数”是不同单位。六值覆盖阵列是另一项数学构造，其复核材料单列于 six-level 和 formal。

## 证据和信任边界

|结论|如何复核|
|---|---|
|JHipster 的 12 个真实配置覆盖 642 项|原始 CSV 逐行复算。将全部 26,256 行无损转为 Lean 表示后，由内核确认具体清单的分数及通用 648 上界。逐行编码与原始文件的对应关系另由 Python 和数据指纹核实。|
|JHipster 不可能达到 643 项|整数搜索排除 29 个等价类，另行枚举直方图、核对对称性，并对剪枝程序做边界测试。upper/formal/LossIdentity.lean 证明了目标与损失之间的恒等式及剪枝的必要条件。完整 C# 穷举器和直方图转换尚未形式化。|
|四个基准在二项满覆盖下能够命中的历史失败配置数的最小值和最大值|transfer/formal/Transfer.lean 核实全部端点的清单和普适上下界。transfer/formal/MinePumpMinimum.lean 核实六个布尔开关的完整数据空间，证明其三项全覆盖最少需要 12 行。两个模块使用 Lean 标准库和内核有限计算。|
|六值构造有 2,340 行、10,609 列并且具有三项覆盖|formal/GridResult.lean 给出完整存在性定理。几何归约由内核证明。四个有限事实使用 Lean 的 native_decide，信任边界包括 Lean 编译器的计算结果；源代码与内核输出列出这四处。独立 Python 程序另外从完整 CSV 核对其 24,825,060 个单元。|

## 重放 JHipster 的精确结果

从研究者的[固定 GitHub 提交](https://github.com/xdevroey/jhipster-dataset/blob/5e6103044c968561ad3f68d07f4f70982b7a718b/v3.6.1/test/jhipster3.6.1-testresults.csv)下载原始 CSV，存为仓库根目录的 jhipster.csv。其 SHA-256 是 fb842702e78a9db71687822d7e4950729c28a7a0d17c3e67c8357d8f7da6157a。以下命令以仓库根目录为当前目录。需要 Python 3.11+。上界的穷举另外需要 .NET 10 SDK，或 Windows 的 .NET Framework C# 编译器。upper/rerun.py 的 --csc 参数接受 csc.exe 的绝对路径。

~~~sh
python lower/check.py jhipster.csv lower/best17.txt reproduced-plan.json
python lower/historical_baseline.py jhipster.csv lower/plan642.json
python upper/check_run.py upper/proofrun/top.txt upper/proofrun/excludes643.log 643
python upper/rerun.py jhipster.csv upper/bound.json reproduced-upper.log --jobs 3
~~~

第三条命令核实保存的输出是否囊括所有代表；重新执行完整排除使用第四条。程序从 CSV 重新生成输入并重编译，最后一个类最耗时。lower/upper-audit.md 说明使用另一种枚举方式与已知正确答案做的独立检查。具体的 12 项设置在 lower/settings.csv。

## 外部验证

transfer/README.md 记录了预定筛选条件、排除的四个基准、各项目的真实可行配置数、随机基线、报告计数与原论文的两处差异，以及下载固定档案的步骤。transfer/frozen.json 是基于设置锁定的清单。transfer/extreme-plans.json 与 transfer/minepump-threeway.json 是解盲后用于证明可达性的清单，两类用途不同。结果表保留全部纳入项目。该基准未含未见软件版本或前瞻部署。

lower/tiebreak 中另有回顾性探索。从固定候选池中先选二项覆盖数最大的清单，再以三项覆盖数打破平局。JHipster 中原 642 分清单命中六个已知故障类别，三项覆盖最多的同分清单命中四类。该比较没有证明一种通用的故障检出策略。

## 形式化复核

工具链为 Lean 4.30.0-rc2，mathlib 提交 5450b53e5ddc75d46418fabb605edbf36bd0beb6。formal 中含可用 Lake 构建的项目文件和源代码。若已经安装相应版本并缓存依赖，可在此目录运行 lake build。也可用随附脚本及预编译 mathlib 运行：

~~~sh
python formal/check_lean.py --lean-bin PATH_TO_LEAN_BIN --mathlib PATH_TO_MATHLIB Budget CensusData CensusResult Grid GridData GridFacts GridResult
~~~

在根目录复核 CSV 到两组 Lean 数据的转换、导出文件字节或内容可与 formal 中的固定文件对照：

~~~sh
python formal/export_census.py jhipster.csv lower/plan642.json upper/bound.json --output regenerated-census
python formal/export_grid.py six-level/test-plan.csv.gz --output regenerated-grid.lean
python formal/verify_grid.py six-level/test-plan.csv.gz
~~~

若要单独核验上界的损失恒等式，在 formal 目录执行 `lake env lean ../upper/formal/LossIdentity.lean`。四个外部项目的端点、对照表和最少行数证明可按[外部验证说明](transfer/README.md)重放。纸面研究、真实数据采集、文献优先权及来源标签的准确性均不能由 Lean 代为验证。

## 来源

- JHipster 的总体和历史失败类别来自 Halin 等人的配置测试实验。字段选择、目标定义和证明在本仓库中给出。[原始研究](https://doi.org/10.1007/s10664-018-9635-4)
- 四个外部基准来自 Ferreira 等人的 SPLC Failure Observation Challenge。[原始研究](https://splc2020.net/wp-content/uploads/2020/03/SPLC_2020_paper_1.pdf) · [固定归档](https://github.com/fischerJF/challenge/tree/eb6d88977219f1b090ab340b45b6bb3f10d30ce1)
- 三项相互作用可以逃过二项覆盖是组合测试中的已知原理。六个布尔因素的三项最小覆盖数 12 也是已有结果。本文给出的是具体数据上的精确界、反例与重放证据。[Kuhn 等，2013](https://csrc.nist.gov/pubs/book/2013/06/introduction-to-combinatorial-testing/final) · [Lawrence 等，表 1](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=51256)
- six-level/covering-array-note.md 详列圆分种子、构造先例和固定参数表。相对于所查公开表的改进已复核，全球首创性和行数最优性尚未确定。
