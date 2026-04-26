# PlantSC-Analyzer 用户指南

## 目录

1. [简介](#简介)
2. [安装](#安装)
3. [快速开始](#快速开始)
4. [详细使用](#详细使用)
5. [参数配置](#参数配置)
6. [输出结果](#输出结果)
7. [常见问题](#常见问题)

---

## 简介

PlantSC-Analyzer 是一个专为植物单细胞 RNA-seq 数据设计的分析平台，提供从原始数据到细胞类型注释的完整流程。

### 核心功能

- ✅ 自动平台检测 (BGI/10X)
- ✅ 质控和过滤
- ✅ 标准化和批次校正
- ✅ 聚类和降维
- ✅ 细胞类型注释
- ✅ 下游分析 (DEG、富集、拟时序)
- ✅ 智能参数推荐
- ✅ 自动报告生成

---

## 安装

### 方式 1: Conda 环境

```bash
# 克隆仓库
git clone https://github.com/liruirui321/plantsc-analyzer.git
cd plantsc-analyzer

# 创建环境
conda env create -f envs/environment.yml
conda activate plantsc
```

### 方式 2: Docker

```bash
docker pull plantsc/plantsc-analyzer:latest
```

### 方式 3: Singularity

```bash
singularity pull plantsc-analyzer.sif docker://plantsc/plantsc-analyzer:latest
```

---

## 快速开始

### 1. 准备输入数据

#### 从 FASTQ 开始

创建样本表 `samples.csv`:

```csv
sample_id,fastq_1,fastq_2,platform
sample1,/path/to/sample1_R1.fq.gz,/path/to/sample1_R2.fq.gz,BGI
sample2,/path/to/sample2_R1.fq.gz,/path/to/sample2_R2.fq.gz,10X
```

#### 从矩阵开始

创建样本表 `samples.csv`:

```csv
sample_id,matrix_dir
sample1,/path/to/sample1/matrix/
sample2,/path/to/sample2/matrix/
```

### 2. 运行分析

```bash
nextflow run workflows/main.nf \
    --sample_sheet samples.csv \
    --species arabidopsis \
    --tissue root \
    --outdir results \
    -profile standard
```

### 3. 查看结果

```bash
# 查看结果目录
ls results/

# 打开 HTML 报告
open results/report.html
```

---

## 详细使用

### Step 0: 平台检测与矩阵生成

如果从 FASTQ 开始，系统会自动检测平台并生成表达矩阵。

```bash
nextflow run workflows/main.nf \
    --data_type fastq \
    --sample_sheet samples.csv \
    --outdir results
```

**支持的平台**:
- BGI (dnbc4tools)
- 10X Genomics (CellRanger)

### Step 1: 质控 (QC)

质控包括：
- SoupX 环境 RNA 去除
- Scrublet doublet 检测
- 细胞和基因过滤

**参数**:
```bash
--qc.min_genes 200 \
--qc.max_genes 6000 \
--qc.mito_threshold 5.0 \
--qc.run_soupx true \
--qc.run_scrublet true
```

### Step 2: 标准化

标准化和高变基因选择。

**参数**:
```bash
--normalize.method log1p \
--normalize.target_sum 10000 \
--normalize.n_hvg 3000 \
--normalize.hvg_flavor seurat
```

### Step 3: 批次整合 (可选)

如果有多个批次，建议进行批次校正。

**参数**:
```bash
--integration.run true \
--integration.method harmony \
--integration.batch_key batch
```

**支持的方法**:
- Harmony (快速，推荐)
- scVI (准确，需要 GPU)

### Step 4: 聚类

PCA 降维、聚类、UMAP 可视化。

**参数**:
```bash
--cluster.n_neighbors 15 \
--cluster.n_pcs 50 \
--cluster.resolution 0.4,0.6,0.8,1.0 \
--cluster.algorithm leiden
```

### Step 5: 细胞类型注释

基于 Marker 基因自动注释细胞类型。

**参数**:
```bash
--annotation.marker_database ./knowledge_base/markers/arabidopsis/root_markers.csv \
--annotation.confidence_threshold 0.7
```

### Step 6: 下游分析 (可选)

包括差异表达、富集分析、拟时序分析。

**参数**:
```bash
--downstream.deg.run true \
--downstream.enrichment.run true \
--downstream.trajectory.run true
```

---

## 参数配置

### 使用配置文件

创建 `config.yaml`:

```yaml
project_name: "Arabidopsis_Root"
species: "arabidopsis"
tissue: "root"

data_type: "matrix"
sample_sheet: "./samples.csv"
outdir: "./results"

qc:
  min_genes: 200
  max_genes: 6000
  mito_threshold: 5.0

normalize:
  n_hvg: 3000
  hvg_flavor: "seurat"

cluster:
  resolution: [0.4, 0.6, 0.8, 1.0]
  algorithm: "leiden"

annotation:
  marker_database: "./knowledge_base/markers/arabidopsis/root_markers.csv"
```

运行:
```bash
nextflow run workflows/main.nf -c config.yaml
```

### 使用 Agent 获取参数推荐

```bash
# 分析数据并获取推荐参数
python agent/plant_sc_agent.py --analyze data.h5ad

# 交互式模式
python agent/plant_sc_agent.py
```

---

## 输出结果

### 目录结构

```
results/
├── 00_matrix_generation/    # 矩阵生成（如果从 FASTQ 开始）
├── 01_qc/                    # 质控结果
│   ├── soupx/
│   ├── scrublet/
│   ├── filtered.h5ad
│   └── qc_report.html
├── 02_normalize/             # 标准化结果
│   ├── normalized.h5ad
│   └── hvg_plot.pdf
├── 03_integrate/             # 批次整合（可选）
│   └── integrated.h5ad
├── 04_cluster/               # 聚类结果
│   ├── clustered.h5ad
│   ├── umap.pdf
│   └── cluster_composition.pdf
├── 05_annotate/              # 注释结果
│   ├── annotated.h5ad
│   ├── cell_type_annotation.csv
│   └── annotation_umap.pdf
├── 06_downstream/            # 下游分析（可选）
│   ├── deg/
│   ├── enrichment/
│   └── trajectory/
├── report.html               # 分析报告
└── timeline.html             # 运行时间线
```

### 主要输出文件

1. **annotated.h5ad** - 最终注释的 AnnData 对象
2. **cell_type_annotation.csv** - 细胞类型注释表
3. **qc_report.html** - 质控报告
4. **report.html** - 完整分析报告
5. **各种 PDF 图表** - UMAP、聚类、注释可视化

---

## 常见问题

### Q1: 如何选择合适的参数？

使用 Agent 获取智能推荐：
```bash
python agent/plant_sc_agent.py --analyze data.h5ad
```

### Q2: 内存不足怎么办？

1. 减少 HVG 数量: `--normalize.n_hvg 2000`
2. 减少 PCA 维度: `--cluster.n_pcs 30`
3. 使用 backed 模式读取大文件

### Q3: 如何添加自定义 Marker 基因？

创建 CSV 文件，格式如下：
```csv
gene_symbol,cell_type,confidence,reference
VND7,vessel,high,PMID:12345678
SHR,endodermis,high,PMID:87654321
```

### Q4: 如何在 HPC 集群上运行？

使用 SLURM profile:
```bash
nextflow run workflows/main.nf \
    --sample_sheet samples.csv \
    --outdir results \
    -profile slurm
```

### Q5: 如何跳过某些步骤？

```bash
# 跳过批次整合
--integration.run false

# 跳过下游分析
--downstream.deg.run false
```

### Q6: 支持哪些物种？

目前内置支持：
- 拟南芥 (Arabidopsis thaliana)
- 水稻 (Oryza sativa) - 部分支持
- 玉米 (Zea mays) - 部分支持

可以通过添加 Marker 基因库扩展到其他物种。

### Q7: 如何可视化结果？

使用 Python:
```python
import scanpy as sc

# 加载结果
adata = sc.read_h5ad('results/05_annotate/annotated.h5ad')

# 可视化
sc.pl.umap(adata, color='cell_type')
sc.pl.umap(adata, color=['VND7', 'SHR'])
```

---

## 更多资源

- **GitHub**: https://github.com/liruirui321/plantsc-analyzer
- **文档**: https://github.com/liruirui321/plantsc-analyzer/tree/main/docs
- **示例**: https://github.com/liruirui321/plantsc-analyzer/tree/main/examples
- **问题反馈**: https://github.com/liruirui321/plantsc-analyzer/issues

---

## 引用

如果使用 PlantSC-Analyzer，请引用：

```
PlantSC-Analyzer: A comprehensive pipeline for plant single-cell RNA-seq analysis
GitHub: https://github.com/liruirui321/plantsc-analyzer
```
