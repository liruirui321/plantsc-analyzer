# PlantSC-Analyzer

**植物单细胞 RNA-seq 分析系统** - 基于 Nextflow + 交互式 Agent 的模块化分析流程

## 🌱 项目简介

PlantSC-Analyzer 是一个专为植物单细胞转录组分析设计的自动化系统，特别针对木质部细胞类型鉴定和跨物种比较分析。

### 核心特性

- **Nextflow 工作流引擎** - 适配 HPC 集群，支持断点续跑
- **交互式 Agent** - 关键步骤智能推荐参数，用户确认后执行
- **拟南芥 Marker 基因库** - 内置木质部细胞类型标记基因
- **模块化设计** - 每个分析步骤独立封装，易于扩展
- **完整文档** - 从原理到实战的全流程指南

## 📁 项目结构

```
plantsc-analyzer/
├── README.md                    # 项目说明
├── LICENSE                      # 开源协议
├── CHANGELOG.md                 # 版本更新日志
│
├── workflows/                   # Nextflow 工作流
│   ├── main.nf                  # 主流程入口
│   ├── modules/                 # 子流程模块
│   │   ├── qc.nf
│   │   ├── normalize.nf
│   │   ├── integrate.nf
│   │   ├── cluster.nf
│   │   ├── annotate.nf
│   │   └── downstream.nf
│   └── nextflow.config          # Nextflow 配置
│
├── scripts/                     # Python/R 核心脚本
│   ├── 01_qc/
│   │   ├── run_qc.py
│   │   ├── soupx.py
│   │   ├── scrublet.py
│   │   └── qc_report.py
│   ├── 02_normalize/
│   │   ├── normalize.py
│   │   ├── hvg_selection.py
│   │   └── scale.py
│   ├── 03_integrate/
│   │   ├── harmony_integration.py
│   │   ├── scvi_integration.py
│   │   └── batch_correction.py
│   ├── 04_cluster/
│   │   ├── leiden_cluster.py
│   │   ├── umap_visualization.py
│   │   └── resolution_tuning.py
│   ├── 05_annotate/
│   │   ├── marker_annotation.py
│   │   ├── singler_annotation.py
│   │   └── annotation_report.py
│   ├── 06_downstream/
│   │   ├── deg_analysis.py
│   │   ├── trajectory.py
│   │   ├── grn_inference.py
│   │   └── cell_communication.py
│   └── utils/
│       ├── io_utils.py
│       ├── plot_utils.py
│       └── validation.py
│
├── knowledge_base/              # Agent 知识库
│   ├── markers/
│   │   ├── arabidopsis/
│   │   │   ├── xylem_markers.csv
│   │   │   ├── vessel_markers.csv
│   │   │   ├── fiber_markers.csv
│   │   │   └── ray_parenchyma_markers.csv
│   │   └── README.md
│   ├── methods/
│   │   ├── qc_methods.md
│   │   ├── integration_methods.md
│   │   ├── annotation_strategies.md
│   │   └── parameter_tuning.md
│   ├── papers/
│   │   ├── plant_scrna_reviews.md
│   │   └── wood_formation_papers.md
│   └── embeddings/
│       └── vector_db/           # RAG 向量数据库
│
├── configs/                     # 配置文件模板
│   ├── project_template.yaml
│   ├── arabidopsis_default.yaml
│   ├── hpc_slurm.config
│   └── docker_profiles.config
│
├── envs/                        # 环境配置
│   ├── requirements.txt         # Python 依赖
│   ├── environment.yml          # Conda 环境
│   ├── Dockerfile               # Docker 镜像
│   └── singularity.def          # Singularity 容器
│
├── agent/                       # Agent 系统
│   ├── plant_sc_agent.py        # Agent 主程序
│   ├── knowledge_retriever.py   # RAG 检索器
│   ├── parameter_recommender.py # 参数推荐引擎
│   ├── interactive_ui.py        # 交互界面
│   └── report_generator.py      # 报告生成器
│
├── tests/                       # 单元测试
│   ├── test_qc.py
│   ├── test_normalize.py
│   ├── test_cluster.py
│   └── test_data/
│       └── mini_dataset/        # 测试数据集
│
├── docs/                        # 文档
│   ├── installation.md
│   ├── quickstart.md
│   ├── user_guide.md
│   ├── api_reference.md
│   ├── tutorials/
│   │   ├── 01_basic_workflow.md
│   │   ├── 02_batch_correction.md
│   │   ├── 03_cell_annotation.md
│   │   └── 04_downstream_analysis.md
│   └── images/
│
├── examples/                    # 示例项目
│   ├── arabidopsis_xylem/
│   │   ├── config.yaml
│   │   ├── sample_sheet.csv
│   │   └── run.sh
│   └── multi_species/
│       ├── config.yaml
│       └── run.sh
│
└── results/                     # 输出结果 (gitignore)
    └── .gitkeep
```

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/plantsc-analyzer.git
cd plantsc-analyzer

# 创建 Conda 环境
conda env create -f envs/environment.yml
conda activate plantsc

# 安装 Nextflow
conda install -c bioconda nextflow

# 验证安装
nextflow run workflows/main.nf --help
```

### 2. 准备数据

```bash
# 创建项目配置
cp configs/arabidopsis_default.yaml my_project.yaml

# 编辑配置文件
vim my_project.yaml
```

### 3. 运行分析

```bash
# 交互式运行（Agent 辅助）
python agent/plant_sc_agent.py --config my_project.yaml

# 或直接运行 Nextflow
nextflow run workflows/main.nf -c my_project.yaml
```

## 📊 工作流程

```
FASTQ 数据
    ↓
[Step 1] 表达矩阵生成 (dnbc4tools/CellRanger)
    ↓
[Step 2] 第一轮 QC (Knee plot, 饱和度)
    ↓ [Agent 交互: 质量是否合格?]
    ↓
[Step 3] 精细 QC (SoupX, Scrublet)
    ↓ [Agent 交互: 推荐过滤阈值]
    ↓
[Step 4] 标准化 & 聚类 (Harmony/scVI, Leiden)
    ↓ [Agent 交互: 推荐 resolution]
    ↓
[Step 5] 细胞类型注释 (Marker 基因库)
    ↓ [Agent 交互: 确认注释结果]
    ↓
[Step 6] 下游分析 (DEG, Trajectory, GRN)
    ↓
最终报告
```

## 🧬 拟南芥 Marker 基因库

内置木质部细胞类型标记基因：

| 细胞类型 | 代表性 Marker | 数量 |
|---------|--------------|------|
| 导管/管胞 (Vessel) | VND6, VND7, XCP1 | 50+ |
| 木纤维 (Fiber) | NST1, NST2, MYB46 | 40+ |
| 射线薄壁细胞 (Ray) | RAY1, RAY3 | 30+ |

## 🤖 Agent 交互示例

```
🌱 PlantSC Agent: 检测到 3 个样本，开始质控分析...

📊 第一轮 QC 完成:
  - Sample1: 5,234 cells, 比对率 78%
  - Sample2: 4,891 cells, 比对率 82%
  - Sample3: 6,102 cells, 比对率 75%

❓ 所有样本质量合格，是否继续? [Y/n]: Y

🔍 推荐过滤参数:
  - min_genes: 200 (基于基因数分布)
  - max_genes: 5000 (排除 doublets)
  - mito_threshold: 5% (线粒体比例)

❓ 是否接受推荐参数? [Y/n/edit]: Y

✅ 开始精细 QC...
```

## 📚 文档

- [安装指南](docs/installation.md)
- [快速开始](docs/quickstart.md)
- [用户手册](docs/user_guide.md)
- [API 参考](docs/api_reference.md)
- [教程合集](docs/tutorials/)

## 🛠️ 技术栈

- **工作流引擎**: Nextflow
- **核心语言**: Python 3.9+, R 4.2+
- **单细胞分析**: Scanpy, Seurat, Harmony, scVI
- **Agent 框架**: LangChain + RAG
- **容器化**: Docker, Singularity
- **HPC 支持**: SLURM, PBS

## 🤝 贡献指南

欢迎贡献代码、Marker 基因、文档或报告 Bug！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

- **作者**: Cherry
- **项目主页**: https://github.com/YOUR_USERNAME/plantsc-analyzer
- **问题反馈**: https://github.com/YOUR_USERNAME/plantsc-analyzer/issues

## 🙏 致谢

- scLine 项目提供的脚本参考
- Scanpy/Seurat 社区
- 植物单细胞研究社区

---

**版本**: v0.1.0-alpha  
**最后更新**: 2026-04-24
