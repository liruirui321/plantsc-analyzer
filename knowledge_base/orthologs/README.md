# 同源基因数据库

## 概述

本目录包含植物物种间的同源基因映射数据，用于跨物种单细胞数据整合和比较分析。

---

## 数据来源

### 1. Ensembl Plants
- **网站**: http://plants.ensembl.org/
- **覆盖**: 拟南芥、水稻、玉米等主要作物
- **置信度**: 基于序列相似性和系统发育分析

### 2. Phytozome
- **网站**: https://phytozome-next.jgi.doe.gov/
- **覆盖**: 100+ 植物基因组
- **置信度**: 基于 OrthoFinder 和 InParanoid

### 3. PLAZA
- **网站**: https://bioinformatics.psb.ugent.be/plaza/
- **覆盖**: 植物比较基因组学平台
- **置信度**: 整合多种方法

---

## 文件格式

### plant_orthologs.csv

| 列名 | 说明 | 示例 |
|------|------|------|
| species1 | 源物种 | arabidopsis |
| gene1 | 源基因 ID | AT1G01010 |
| species2 | 目标物种 | rice |
| gene2 | 目标基因 ID | LOC_Os01g01010 |
| confidence | 置信度 (0-1) | 0.95 |
| source | 数据来源 | Ensembl |

---

## 支持的物种

| 物种 | 基因 ID 前缀 | 示例 |
|------|-------------|------|
| Arabidopsis | AT | AT1G01010 |
| Rice | LOC_Os | LOC_Os01g01010 |
| Maize | Zm | Zm00001d027230 |
| Tomato | Solyc | Solyc01g005000 |
| Soybean | Glyma | Glyma.01G000100 |
| Poplar | Potri | Potri.001G000100 |

---

## 使用方法

### 1. 加载同源基因数据库

```python
from scripts.utils.cross_species import CrossSpeciesAnalyzer

analyzer = CrossSpeciesAnalyzer(
    ortholog_db='knowledge_base/orthologs/plant_orthologs.csv'
)
```

### 2. 映射基因

```python
# 拟南芥基因映射到水稻
genes = ['AT1G01010', 'AT5G44030', 'AT5G15230']
orthologs = analyzer.map_orthologs(
    genes,
    source_species='arabidopsis',
    target_species='rice',
    min_confidence=0.8
)

print(orthologs)
# {'AT1G01010': 'LOC_Os01g01010', 'AT5G44030': 'LOC_Os03g13170', ...}
```

### 3. 跨物种整合

```python
import scanpy as sc

# 加载数据
adata_arab = sc.read_h5ad('arabidopsis_root.h5ad')
adata_rice = sc.read_h5ad('rice_root.h5ad')

# 整合
integrated = analyzer.integrate_species(
    [adata_arab, adata_rice],
    ['arabidopsis', 'rice'],
    reference_species='arabidopsis',
    method='scvi'
)
```

---

## 扩展数据库

### 从 Ensembl 下载

```bash
# 使用 BioMart
# 1. 访问 http://plants.ensembl.org/biomart/
# 2. 选择 Database: Ensembl Plants Genes
# 3. 选择 Dataset: Arabidopsis genes
# 4. Attributes: Gene stable ID, Rice ortholog gene ID
# 5. Export as CSV
```

### 从 Phytozome 下载

```bash
# 需要注册账号
# 1. 访问 https://phytozome-next.jgi.doe.gov/
# 2. 下载 Orthologs 数据
# 3. 转换为标准格式
```

### 使用 OrthoFinder

```bash
# 从头计算同源基因
orthofinder -f protein_sequences/ -t 8

# 解析结果
python scripts/utils/parse_orthofinder.py \
    OrthoFinder/Results_*/Orthogroups/Orthogroups.tsv \
    --output knowledge_base/orthologs/custom_orthologs.csv
```

---

## 置信度阈值

| 阈值 | 说明 | 推荐用途 |
|------|------|---------|
| ≥ 0.95 | 高置信度 | 关键基因分析 |
| 0.80-0.94 | 中等置信度 | 一般分析 |
| 0.70-0.79 | 低置信度 | 探索性分析 |
| < 0.70 | 不推荐 | 需要人工验证 |

---

## 常见问题

### Q1: 为什么有些基因没有同源基因？

**A**: 可能原因：
1. 物种特异基因（进化中获得或丢失）
2. 数据库未收录
3. 置信度低于阈值

### Q2: 一对多的同源关系如何处理？

**A**: 
- 默认选择置信度最高的
- 可以保留所有同源基因（设置 `keep_all=True`）

### Q3: 如何验证同源基因映射？

**A**:
1. 检查基因功能注释
2. 比较表达模式
3. 查看系统发育树

---

## 参考文献

1. **Ensembl Plants**: Bolser et al. (2016) Nucleic Acids Res.
2. **Phytozome**: Goodstein et al. (2012) Nucleic Acids Res.
3. **PLAZA**: Van Bel et al. (2018) Nucleic Acids Res.
4. **OrthoFinder**: Emms & Kelly (2019) Genome Biology

---

## 更新日志

- 2026-04-27: 初始版本，包含 24 个同源基因对
- 待添加: 更多物种和基因

---

## 贡献

欢迎贡献更多同源基因数据！

提交格式：
```csv
species1,gene1,species2,gene2,confidence,source
```

请确保：
1. 置信度 ≥ 0.8
2. 提供数据来源
3. 验证基因 ID 正确性
