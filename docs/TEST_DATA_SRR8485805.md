# 测试数据准备指南 - SRR8485805

## 📊 数据集信息

### 基本信息

- **SRA ID**: SRR8485805
- **物种**: *Arabidopsis thaliana* (Col-0)
- **组织**: 根（root tip, 0.5 cm from tip）
- **平台**: 10X Genomics
- **测序**: Illumina NovaSeq
- **细胞数**: 7,695 cells (过滤后)
- **基因数**: 23,161 genes

### 文献来源

**Zhang et al. 2019 - Molecular Plant**
- **标题**: A Single-Cell RNA Sequencing Profiles the Developmental Landscape of Arabidopsis Root
- **期刊**: *Molecular Plant* 12(5): 648-660
- **PMID**: 31004836
- **DOI**: 10.1016/j.molp.2019.04.004
- **发表日期**: 2019年5月

### 研究亮点

- 24 个细胞簇（cell clusters）
- 识别了簇特异性 Marker 基因
- 重建了根发育的连续分化轨迹
- 分析了离子吸收和激素响应模式

---

## 💾 数据下载

### 方法 1: 使用 SRA Toolkit（推荐）

```bash
# 安装 SRA Toolkit
conda install -c bioconda sra-tools

# 下载 FASTQ 文件
fastq-dump --split-files --gzip SRR8485805

# 或使用更快的 fasterq-dump
fasterq-dump SRR8485805
gzip SRR8485805*.fastq
```

### 方法 2: 使用 prefetch + fasterq-dump

```bash
# 先下载 SRA 文件
prefetch SRR8485805

# 转换为 FASTQ
fasterq-dump --split-files SRR8485805
gzip SRR8485805*.fastq
```

### 方法 3: 直接下载处理好的数据

```bash
# 从 GEO 下载处理好的矩阵
# GEO: GSE123013 (Zhang et al. 2019)

# 使用 GEOquery (R)
library(GEOquery)
gse <- getGEO("GSE123013")

# 或使用 Python
import GEOparse
gse = GEOparse.get_GEO("GSE123013")
```

---

## 🔧 数据处理流程

### Step 0: 生成表达矩阵

如果从 FASTQ 开始：

```bash
# 使用 Cell Ranger (10X Genomics)
cellranger count \
    --id=arabidopsis_root \
    --transcriptome=/path/to/TAIR10_reference \
    --fastqs=/path/to/fastqs \
    --sample=SRR8485805 \
    --localcores=8 \
    --localmem=32
```

或使用我们的流程：

```bash
# 使用 PlantSC-Analyzer
nextflow run workflows/main.nf \
    --platform 10x \
    --fastq_dir ./data/SRR8485805 \
    --genome TAIR10 \
    --outdir ./results/SRR8485805
```

### Step 1-6: 完整分析流程

```bash
# 运行完整流程
nextflow run workflows/main.nf \
    --input results/SRR8485805/matrix_generation/filtered_feature_bc_matrix.h5 \
    --species "Arabidopsis thaliana" \
    --tissue root \
    --project_name SRR8485805_test \
    --outdir ./results/SRR8485805_analysis
```

---

## 📋 预期结果

### 细胞类型（基于 Zhang et al. 2019）

| 细胞类型 | 预期细胞数 | 代表 Marker |
|---------|-----------|------------|
| 表皮 | ~1,000 | PDF2, GL2 |
| 皮层 | ~1,200 | CO2, CORTEX |
| 内皮层 | ~800 | SCR, SHR, CASP1 |
| 中柱 | ~1,500 | - |
| 木质部 | ~600 | VND6, VND7 |
| 韧皮部 | ~500 | APL, SUC2 |
| 静止中心 | ~50 | WOX5 |
| 分生区 | ~2,000 | PLT1, PLT2 |

### QC 指标

| 指标 | 预期值 |
|------|--------|
| 细胞数（过滤前） | ~15,000 |
| 细胞数（过滤后） | ~7,695 |
| 中位基因数/细胞 | ~2,000 |
| 中位 UMI 数/细胞 | ~5,000 |
| 线粒体比例 | < 5% |

---

## 🧪 测试检查点

### 1. 数据加载

```python
import scanpy as sc

# 加载数据
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')

# 检查
print(f"Cells: {adata.n_obs}")
print(f"Genes: {adata.n_vars}")

# 预期: Cells ~7,695, Genes ~23,161
```

### 2. QC 过滤

```python
# QC 指标
sc.pp.calculate_qc_metrics(adata, inplace=True)

# 检查分布
import matplotlib.pyplot as plt
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'])

# 预期: 大部分细胞 n_genes 在 1,000-4,000 之间
```

### 3. 聚类

```python
# 预处理
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# 降维和聚类
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)

# 检查
print(f"Clusters: {adata.obs['leiden'].nunique()}")
# 预期: 15-25 个 clusters
```

### 4. Marker 基因验证

```python
# 检查已知 Marker
markers = ['SCR', 'SHR', 'WOX5', 'GL2', 'VND6', 'APL']

sc.pl.umap(adata, color=markers, ncols=3)

# 预期: 每个 Marker 在特定 cluster 高表达
```

---

## 💻 系统要求

### 最低配置

- **CPU**: 4 cores
- **内存**: 16 GB RAM
- **存储**: 50 GB
- **时间**: ~2-3 小时（完整流程）

### 推荐配置

- **CPU**: 8+ cores
- **内存**: 32 GB RAM
- **存储**: 100 GB
- **时间**: ~1 小时（完整流程）

### 存储空间估算

| 文件 | 大小 |
|------|------|
| FASTQ (原始) | ~10 GB |
| BAM (比对) | ~15 GB |
| 表达矩阵 | ~500 MB |
| 分析结果 | ~2 GB |
| **总计** | **~30 GB** |

---

## 🐛 常见问题

### Q1: 下载速度慢

```bash
# 使用 aspera 加速下载
prefetch --max-size 50G --transport ascp SRR8485805
```

### Q2: 内存不足

```bash
# 减少线程数
cellranger count --localcores=4 --localmem=16

# 或使用我们的流程（自动优化）
nextflow run workflows/main.nf -profile low_memory
```

### Q3: Cell Ranger 需要 TAIR10 参考基因组

```bash
# 下载 TAIR10
wget https://www.arabidopsis.org/download_files/Genes/TAIR10_genome_release/TAIR10_chromosome_files/TAIR10_chr_all.fas

# 构建 Cell Ranger 索引
cellranger mkref \
    --genome=TAIR10 \
    --fasta=TAIR10_chr_all.fas \
    --genes=TAIR10_GFF3_genes.gff
```

---

## 📊 预期输出

### 目录结构

```
results/SRR8485805_analysis/
├── 00_matrix_generation/
│   ├── filtered_feature_bc_matrix.h5
│   └── metrics_summary.csv
├── 01_qc/
│   ├── qc_filtered.h5ad
│   ├── qc_report.html
│   └── qc_plots/
├── 02_normalize/
│   ├── normalized.h5ad
│   └── hvg_plot.pdf
├── 03_integrate/
│   └── (跳过，单样本)
├── 04_cluster/
│   ├── clustered.h5ad
│   ├── umap.pdf
│   └── cluster_markers.csv
├── 05_annotate/
│   ├── annotated.h5ad
│   ├── cell_type_annotation.csv
│   └── annotation_umap.pdf
└── 06_downstream/
    ├── deg_results.csv
    ├── trajectory_analysis/
    └── final_report.html
```

### 关键文件

1. **annotated.h5ad** - 最终注释的 AnnData 对象
2. **cell_type_annotation.csv** - 细胞类型注释表
3. **final_report.html** - 完整分析报告

---

## ✅ 验证标准

### 成功标准

- [ ] 细胞数 > 5,000
- [ ] 识别出 15-25 个 clusters
- [ ] 主要细胞类型都存在（表皮、皮层、内皮层、木质部、韧皮部）
- [ ] Marker 基因表达符合预期
- [ ] UMAP 图显示清晰的细胞类型分离

### 与文献对比

| 指标 | Zhang 2019 | 我们的流程 | 状态 |
|------|-----------|-----------|------|
| 细胞数 | 7,695 | ? | 待测试 |
| Clusters | 24 | ? | 待测试 |
| 主要细胞类型 | 8 | ? | 待测试 |

---

## 📝 测试清单

下周测试时请检查：

- [ ] 数据下载成功
- [ ] 表达矩阵生成正确
- [ ] QC 过滤合理
- [ ] 聚类结果清晰
- [ ] Marker 基因表达正确
- [ ] 细胞类型注释准确
- [ ] 与文献结果一致
- [ ] 流程运行时间可接受
- [ ] 内存使用在预期范围

---

## 📧 问题反馈

测试过程中遇到问题，请记录：

1. 错误信息
2. 运行环境（CPU、内存、系统）
3. 输入数据大小
4. 失败的步骤

---

**准备就绪！期待下周的测试结果！** 🚀

**Sources**:
- [Zhang et al. 2019 - Molecular Plant](https://www.cell.com/molecular-plant/fulltext/S1674-2052(19)30133-9)
- [PMID: 31004836](https://pubmed.ncbi.nlm.nih.gov/31004836/)
- [SRA: SRR8485805](https://trace.ncbi.nlm.nih.gov/Traces/index.html?run=SRR8485805)
- [GEO: GSE123013](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123013)
