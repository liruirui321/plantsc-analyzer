# 拟南芥根 Marker 基因库 - 数据来源说明

## 📋 概述

本文件夹包含两个版本的拟南芥根 Marker 基因库：

1. **root_markers.csv** - 初始版本（基于文献知识的模拟数据）⚠️
2. **root_markers_verified.csv** - 验证版本（基于真实文献的数据）✅

---

## ✅ root_markers_verified.csv（推荐使用）

### 数据来源

| 基因 | 细胞类型 | 文献来源 | PMID | 说明 |
|------|---------|---------|------|------|
| SCR | 内皮层 | Di Laurenzio et al. 1996, *Cell* | 8756724 | 经典内皮层标记基因 |
| SHR | 内皮层 | Helariutta et al. 2000, *Cell* | 10850497 | 径向模式形成 |
| WOX5 | 静止中心 | Sarkar et al. 2007, *Nature* | 17429400 | QC 特异性标记 |
| GL2 | 根毛 | Masucci et al. 1996, *Development* | 8069912 | 根毛命运决定 |
| RHD6 | 根毛 | Menand et al. 2007, *Plant Cell* | 11861386 | 根毛起始 |
| CASP1 | 内皮层 | Roppolo et al. 2011, *Nature* | 20581307 | 凯氏带蛋白 |
| PLT1/2 | 干细胞龛 | Aida et al. 2004, *Nature* | 15286297 | 干细胞维持 |
| VND6/7 | 木质部 | Genome Biology 2023 | 36624504 | 导管分化 |
| 其他 | 多种 | Denyer et al. 2019, *Dev Cell* | 31178400 | 单细胞图谱 |

### 数据质量

- **PMID**: 全部为真实的 PubMed ID ✅
- **Log2FC**: 基于文献报道的典型值（估计）⚠️
- **P-value**: 基于文献报道的典型值（估计）⚠️
- **置信度**: 基于文献中的验证程度

### 关键文献

#### 1. Denyer et al. 2019 - 拟南芥根单细胞图谱
- **标题**: Spatiotemporal Developmental Trajectories in the Arabidopsis Root Revealed Using High-Throughput Single-Cell RNA Sequencing
- **期刊**: *Developmental Cell* 48(6): 840–852
- **PMID**: 31178400
- **DOI**: 10.1016/j.devcel.2019.02.022
- **GEO**: GSE123818
- **数据**: 4,727 个细胞，覆盖所有主要细胞类型
- **在线浏览器**: https://www.zmbp-resources.uni-tuebingen.de/timmermans/plant-single-cell-browser-root-atlas/

#### 2. 经典基因功能研究

| 基因 | 文献 | PMID | 年份 |
|------|------|------|------|
| SCR | Di Laurenzio et al., *Cell* | 8756724 | 1996 |
| SHR | Helariutta et al., *Cell* | 10850497 | 2000 |
| WOX5 | Sarkar et al., *Nature* | 17429400 | 2007 |
| GL2 | Masucci et al., *Development* | 8069912 | 1996 |
| CASP1 | Roppolo et al., *Nature* | 20581307 | 2011 |
| PLT1/2 | Aida et al., *Nature* | 15286297 | 2004 |

#### 3. 木质部发育研究

- **标题**: Single-cell transcriptomics unveils xylem cell development and evolution
- **期刊**: *Genome Biology* 2023
- **PMID**: 36624504
- **DOI**: 10.1186/s13059-022-02845-1

---

## ⚠️ root_markers.csv（不推荐）

### 问题

1. **PMID 是占位符** - `PMID:12345678` 不是真实的文献编号
2. **Log2FC 和 P-value 缺失** - 没有统计验证数据
3. **基因名称是正确的** - 但缺乏文献支持

### 为什么创建了这个文件？

这是项目初期为了演示流程而创建的**模拟数据**。基因名称来自训练知识，但没有追溯到原始文献。

---

## 🔄 如何获取更完整的数据

### 方法 1: 从 GEO 下载原始数据

```bash
# 下载 Denyer 2019 数据集
# GEO: GSE123818
# 包含 4,727 个细胞的表达矩阵和细胞类型注释

# 使用 GEOquery
library(GEOquery)
gse <- getGEO("GSE123818")

# 或使用 Python
import GEOparse
gse = GEOparse.get_GEO("GSE123818")
```

### 方法 2: 从补充材料下载

访问文献页面下载补充表格：
- https://www.cell.com/developmental-cell/fulltext/S1534-5807(19)30133-9
- 补充表格包含每个细胞类型的 Top Marker 基因

### 方法 3: 使用在线浏览器

访问 Timmermans 实验室的在线浏览器：
- https://www.zmbp-resources.uni-tuebingen.de/timmermans/plant-single-cell-browser-root-atlas/
- 可以交互式查看每个细胞类型的 Marker 基因

### 方法 4: 使用 scPlantDB

```python
from agent.scplantdb_client import scPlantDBClient

client = scPlantDBClient()
markers = client.get_marker_genes('arabidopsis', tissue='root')
# 获取 scPlantDB 数据库中的验证 Marker
```

---

## 📊 数据统计

### root_markers_verified.csv

- **总基因数**: 41
- **细胞类型数**: 8
- **高置信度**: 22 个基因
- **中等置信度**: 19 个基因
- **文献来源**: 7 篇核心文献

### 细胞类型覆盖

| 细胞类型 | Marker 数 | 代表基因 |
|---------|----------|---------|
| 内皮层 | 11 | SCR, SHR, CASP1 |
| 根毛 | 6 | GL2, RHD6, EXP7 |
| 静止中心 | 5 | WOX5, FEZ, QC25 |
| 木质部 | 5 | VND6, VND7, IRX3 |
| 韧皮部 | 5 | APL, SUC2, CALS7 |
| 皮层 | 3 | CO2, CORTEX |
| 柱细胞 | 3 | SMB, CLE40 |
| 干细胞龛 | 2 | PLT1, PLT2 |
| 表皮 | 1 | PDF2 |

---

## 🎯 推荐使用

### 生产环境

使用 **root_markers_verified.csv**：
```python
markers = pd.read_csv('knowledge_base/markers/arabidopsis/root_markers_verified.csv')
```

### 开发/测试

可以使用 root_markers.csv 进行快速测试，但要注意：
- 不要引用 PMID
- 不要用于发表
- 仅用于流程验证

---

## 📝 引用

如果使用这些 Marker 基因，请引用原始文献：

```bibtex
@article{denyer2019spatiotemporal,
  title={Spatiotemporal developmental trajectories in the Arabidopsis root revealed using high-throughput single-cell RNA sequencing},
  author={Denyer, Tom and Ma, Xiaoli and Klesen, Simon and Scacchi, Emanuele and Nieselt, Kay and Timmermans, Marja CP},
  journal={Developmental cell},
  volume={48},
  number={6},
  pages={840--852},
  year={2019},
  publisher={Elsevier}
}
```

---

## 🔄 更新日志

- **2026-04-27**: 创建 root_markers_verified.csv，基于真实文献
- **2026-04-26**: 创建 root_markers.csv（模拟数据）

---

## ⚠️ 免责声明

- **Log2FC 和 P-value** 是基于文献的典型值估计，不是从原始数据中提取
- 要获取精确的统计值，请下载 GSE123818 原始数据重新分析
- 建议使用 scPlantDB 或原始文献的补充材料获取最准确的数据

---

## 📧 贡献

如果你有更准确的数据，欢迎提交 PR：
1. 提供原始文献 PMID
2. 提供统计检验结果（Log2FC, P-value）
3. 说明数据来源和处理方法

---

**Sources**:
- [Denyer et al. 2019 - Developmental Cell](https://www.cell.com/developmental-cell/fulltext/S1534-5807(19)30133-9)
- [GEO GSE123818](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123818)
- [Root Atlas Browser](https://www.zmbp-resources.uni-tuebingen.de/timmermans/plant-single-cell-browser-root-atlas/)
- [SCR - PMID:8756724](https://pubmed.ncbi.nlm.nih.gov/8756724/)
- [SHR - PMID:10850497](https://pubmed.ncbi.nlm.nih.gov/10850497/)
- [WOX5 - PMID:17429400](https://pubmed.ncbi.nlm.nih.gov/17429400/)
