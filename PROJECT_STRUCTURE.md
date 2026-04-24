# PlantSC-Analyzer Project Structure

## 📁 完整目录结构

```
plantsc-analyzer/
├── README.md                           # 项目主文档
├── LICENSE                             # MIT 开源协议
├── CHANGELOG.md                        # 版本更新日志
├── .gitignore                          # Git 忽略文件
│
├── workflows/                          # Nextflow 工作流
│   ├── main.nf                         # 主流程入口
│   ├── nextflow.config                 # Nextflow 配置
│   └── modules/                        # 子流程模块
│       ├── matrix_generation.nf        # Step 0: 矩阵生成 (BGI/10X)
│       ├── qc.nf                       # Step 1: 质控
│       ├── normalize.nf                # Step 2: 标准化
│       ├── integrate.nf                # Step 3: 批次整合
│       ├── cluster.nf                  # Step 4: 聚类
│       ├── annotate.nf                 # Step 5: 注释
│       └── downstream.nf               # Step 6: 下游分析
│
├── scripts/                            # Python/R 核心脚本
│   ├── 00_matrix_generation/           # 矩阵生成脚本
│   │   ├── detect_platform.py          # 平台检测 (BGI/10X)
│   │   ├── trim_bgi_oligo.py           # BGI V2.0 oligo 剪切
│   │   └── convert_to_h5ad.py          # 转换为 h5ad 格式
│   ├── 01_qc/                          # 质控脚本
│   │   ├── soupx.py                    # SoupX 环境 RNA 去除
│   │   ├── scrublet.py                 # Scrublet doublet 检测
│   │   ├── filter_cells.py             # 细胞过滤
│   │   └── qc_report.py                # QC 报告生成
│   ├── 02_normalize/                   # 标准化脚本
│   ├── 03_integrate/                   # 整合脚本
│   ├── 04_cluster/                     # 聚类脚本
│   ├── 05_annotate/                    # 注释脚本
│   ├── 06_downstream/                  # 下游分析脚本
│   └── utils/                          # 工具函数
│
├── knowledge_base/                     # Agent 知识库
│   ├── markers/                        # Marker 基因库
│   │   ├── README.md                   # Marker 数据库说明
│   │   └── arabidopsis/                # 拟南芥 Marker
│   │       ├── xylem_markers.csv       # 木质部细胞 Marker
│   │       └── root_markers.csv        # 根细胞 Marker
│   ├── methods/                        # 方法学文档
│   ├── papers/                         # 文献库
│   └── embeddings/                     # RAG 向量数据库
│       └── vector_db/
│
├── configs/                            # 配置文件模板
│   └── project_template.yaml           # 项目配置模板
│
├── envs/                               # 环境配置
│   ├── requirements.txt                # Python 依赖
│   ├── environment.yml                 # Conda 环境
│   ├── Dockerfile                      # Docker 镜像 (待添加)
│   └── singularity.def                 # Singularity 容器 (待添加)
│
├── agent/                              # Agent 系统
│   ├── plant_sc_agent.py               # Agent 主程序
│   ├── knowledge_retriever.py          # RAG 检索器 (待添加)
│   ├── parameter_recommender.py        # 参数推荐引擎 (待添加)
│   └── report_generator.py             # 报告生成器 (待添加)
│
├── tests/                              # 单元测试
│   └── test_data/                      # 测试数据
│       └── mini_dataset/
│
├── docs/                               # 文档
│   ├── installation.md                 # 安装指南
│   ├── quickstart.md                   # 快速开始
│   ├── user_guide.md                   # 用户手册 (待添加)
│   ├── api_reference.md                # API 参考 (待添加)
│   ├── tutorials/                      # 教程
│   └── images/                         # 图片资源
│
├── examples/                           # 示例项目
│   ├── arabidopsis_xylem/              # 拟南芥木质部示例
│   │   ├── config.yaml                 # 配置文件 (待添加)
│   │   ├── sample_sheet.csv            # 样本表
│   │   └── run.sh                      # 运行脚本
│   └── multi_species/                  # 多物种示例 (待添加)
│
└── results/                            # 输出结果 (gitignore)
    └── .gitkeep
```

## 🎯 核心功能模块

### Step 0: 矩阵生成 (新增)
- **平台检测**: 自动识别 BGI 或 10X 平台
- **BGI 支持**: 
  - dnbc4tools 流程
  - V2.0/V2.5 oligo 自动剪切
  - V3.0+ 直接处理
- **10X 支持**: CellRanger 流程
- **输出**: 统一的 h5ad 格式

### Step 1-6: 标准分析流程
- 质控 → 标准化 → 整合 → 聚类 → 注释 → 下游

### Agent 系统
- 交互式参数推荐
- 知识库查询 (RAG)
- 自动报告生成

## 📝 已完成文件

### 核心文件
- ✅ README.md
- ✅ LICENSE
- ✅ CHANGELOG.md
- ✅ .gitignore

### 工作流
- ✅ workflows/main.nf
- ✅ workflows/nextflow.config
- ✅ workflows/modules/matrix_generation.nf
- ✅ workflows/modules/qc.nf

### 脚本
- ✅ scripts/00_matrix_generation/detect_platform.py
- ✅ scripts/00_matrix_generation/trim_bgi_oligo.py
- ✅ scripts/00_matrix_generation/convert_to_h5ad.py

### 配置
- ✅ configs/project_template.yaml (已更新 Step 0)
- ✅ envs/requirements.txt
- ✅ envs/environment.yml

### 知识库
- ✅ knowledge_base/markers/README.md
- ✅ knowledge_base/markers/arabidopsis/xylem_markers.csv

### Agent
- ✅ agent/plant_sc_agent.py (框架)

### 文档
- ✅ docs/installation.md
- ✅ docs/quickstart.md

### 示例
- ✅ examples/arabidopsis_xylem/sample_sheet.csv
- ✅ examples/arabidopsis_xylem/run.sh

## 🚧 待完成

### 高优先级
1. **核心脚本实现** (Step 1-6)
   - 01_qc/: soupx.py, scrublet.py, filter_cells.py
   - 02_normalize/: normalize.py, hvg_selection.py
   - 03_integrate/: harmony_integration.py, scvi_integration.py
   - 04_cluster/: leiden_cluster.py, umap_visualization.py
   - 05_annotate/: marker_annotation.py
   - 06_downstream/: deg_analysis.py

2. **Nextflow 模块** (Step 2-6)
   - normalize.nf
   - integrate.nf
   - cluster.nf
   - annotate.nf
   - downstream.nf

3. **Agent 组件**
   - knowledge_retriever.py (RAG)
   - parameter_recommender.py
   - report_generator.py

### 中优先级
4. **测试**
   - 单元测试
   - 集成测试
   - 测试数据集

5. **文档**
   - user_guide.md
   - api_reference.md
   - tutorials/

6. **容器化**
   - Dockerfile
   - singularity.def

### 低优先级
7. **扩展功能**
   - 多物种 Marker 库
   - Web UI
   - GPU 加速

## 🔄 下一步行动

1. **完成核心脚本** - 实现 Step 1-6 的 Python 脚本
2. **完成 Nextflow 模块** - 编写剩余的 .nf 文件
3. **测试端到端流程** - 用小数据集测试完整流程
4. **完善 Agent** - 实现 RAG 和参数推荐
5. **编写文档** - 用户手册和教程

## 📊 进度统计

- **总文件数**: ~80 个
- **已完成**: ~20 个 (25%)
- **核心框架**: ✅ 完成
- **脚本实现**: 🚧 进行中
- **测试**: ⏳ 待开始
- **文档**: 🚧 进行中
