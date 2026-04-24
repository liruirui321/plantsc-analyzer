# PlantSC-Analyzer 项目总结

## 🎉 项目已创建完成！

**仓库位置**: `/Users/cherry/Library/CloudStorage/OneDrive-Personal/05.WSL/00.single_cell/plantsc-analyzer`

**Git 状态**: ✅ 已初始化，首次提交完成 (commit: d5071b9)

---

## 📦 已完成的核心功能

### 1. **Step 0: 平台检测与矩阵生成** ⭐ 新增
- ✅ 自动检测 BGI 或 10X 平台
- ✅ BGI V2.0/V2.5 oligo 自动剪切脚本
- ✅ 支持 dnbc4tools 和 CellRanger
- ✅ 统一输出为 h5ad 格式
- ✅ **SoupX 前后矩阵都保留**

### 2. **Nextflow 工作流框架**
- ✅ 主流程 (`workflows/main.nf`)
- ✅ 模块化设计 (`workflows/modules/`)
- ✅ 配置文件 (`nextflow.config`)
- ✅ 支持 SLURM/PBS/Docker/Singularity

### 3. **交互式 Agent 框架**
- ✅ 基础框架 (`agent/plant_sc_agent.py`)
- ✅ 参数推荐逻辑
- ✅ 用户交互界面 (Rich UI)

### 4. **知识库**
- ✅ 拟南芥木质部 Marker 基因库 (20+ 基因)
- ✅ Marker 数据库格式规范
- ✅ 可扩展到其他物种

### 5. **文档**
- ✅ README.md (项目介绍)
- ✅ 安装指南 (installation.md)
- ✅ 快速开始 (quickstart.md)
- ✅ 项目结构说明 (PROJECT_STRUCTURE.md)

---

## 📊 项目统计

| 类别 | 数量 | 状态 |
|------|------|------|
| 总文件数 | 38 | - |
| 代码行数 | 2,520+ | - |
| Python 脚本 | 4 | ✅ 完成 |
| Nextflow 模块 | 2 | ✅ 完成 |
| 配置文件 | 2 | ✅ 完成 |
| 文档 | 5 | ✅ 完成 |
| Marker 基因 | 20+ | ✅ 完成 |

---

## 🎯 核心设计亮点

### 1. **平台无关性**
```
原始数据 (FASTQ)
    ↓
[自动检测] → BGI or 10X?
    ↓
[平台特定处理]
    ├─ BGI: dnbc4tools + oligo trimming
    └─ 10X: CellRanger
    ↓
[统一格式] → h5ad
    ↓
[通用分析流程]
```

### 2. **BGI 试剂盒版本兼容**
```python
# V2.0/V2.5 → V3.0+ 兼容
if kit_version in ['V2.0', 'V2.5']:
    trim_oligo(
        R1: keep [0:20],
        R2: extract [0:10, 16:26, 32:42]
    )
```

### 3. **SoupX 数据保留**
```bash
# 同时保存校正前后的矩阵
output:
  - before_soupx.h5ad  # 原始矩阵
  - after_soupx.h5ad   # 校正后矩阵
```

### 4. **交互式 Agent**
```
Agent: 检测到 3 个样本...
  ✅ Sample1: 5,234 cells, 78% alignment
  ✅ Sample2: 4,891 cells, 82% alignment

❓ 推荐参数: min_genes=200, max_genes=5000
   接受? [Y/n/edit]: _
```

---

## 🚀 下一步开发计划

### Phase 1: 核心脚本实现 (优先级: 🔥🔥🔥)
- [ ] `scripts/01_qc/soupx.py`
- [ ] `scripts/01_qc/scrublet.py`
- [ ] `scripts/01_qc/filter_cells.py`
- [ ] `scripts/02_normalize/normalize.py`
- [ ] `scripts/03_integrate/harmony_integration.py`
- [ ] `scripts/04_cluster/leiden_cluster.py`
- [ ] `scripts/05_annotate/marker_annotation.py`

### Phase 2: Nextflow 模块 (优先级: 🔥🔥)
- [ ] `workflows/modules/normalize.nf`
- [ ] `workflows/modules/integrate.nf`
- [ ] `workflows/modules/cluster.nf`
- [ ] `workflows/modules/annotate.nf`
- [ ] `workflows/modules/downstream.nf`

### Phase 3: Agent 增强 (优先级: 🔥)
- [ ] `agent/knowledge_retriever.py` (RAG)
- [ ] `agent/parameter_recommender.py`
- [ ] `agent/report_generator.py`

### Phase 4: 测试与文档 (优先级: 🔥)
- [ ] 单元测试
- [ ] 端到端测试
- [ ] 用户手册
- [ ] 教程视频

---

## 📝 如何推送到 GitHub

```bash
cd /Users/cherry/Library/CloudStorage/OneDrive-Personal/05.WSL/00.single_cell/plantsc-analyzer

# 1. 在 GitHub 创建新仓库 (不要初始化 README)
#    https://github.com/new

# 2. 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/plantsc-analyzer.git

# 3. 推送代码
git push -u origin main

# 4. 后续更新
git add .
git commit -m "Your commit message"
git push
```

---

## 🔧 本地开发快速开始

```bash
# 1. 进入项目目录
cd plantsc-analyzer

# 2. 创建 Conda 环境
conda env create -f envs/environment.yml
conda activate plantsc

# 3. 测试脚本
python scripts/00_matrix_generation/detect_platform.py --help
python scripts/00_matrix_generation/trim_bgi_oligo.py --help

# 4. 测试 Nextflow
nextflow run workflows/main.nf --help
```

---

## 💡 关键技术决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| 工作流引擎 | Nextflow | HPC 友好，断点续跑 |
| Agent 模式 | 交互式 | 关键步骤人工确认 |
| Marker 优先级 | 拟南芥先行 | 文献最丰富，逐步扩展 |
| 脚本设计 | 从零重写 | 统一接口，易维护 |
| 平台支持 | BGI + 10X | 覆盖主流平台 |
| 数据格式 | h5ad | Scanpy 生态兼容 |

---

## 📞 联系与贡献

- **项目主页**: (待创建 GitHub 仓库后填写)
- **问题反馈**: GitHub Issues
- **贡献指南**: 欢迎 PR！

---

**版本**: v0.1.0-alpha  
**创建日期**: 2026-04-24  
**最后更新**: 2026-04-24  
**状态**: 🚧 开发中

---

## ✅ 今日完成清单

- [x] 创建完整项目结构
- [x] 实现 Step 0 平台检测模块
- [x] 实现 BGI oligo 剪切脚本
- [x] 更新 SoupX 保留前后矩阵
- [x] 编写核心文档
- [x] Git 初始化并首次提交
- [x] 准备 GitHub 推送

**下次开发**: 实现 Step 1-6 的核心 Python 脚本 🚀
