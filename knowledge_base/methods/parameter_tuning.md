# 参数调优指南

## 概览

单细胞分析中最常见的问题是**参数选择不当**。本指南提供系统的参数调优方法。

## 参数调优流程图

```
开始分析
    ↓
[1] 数据特征分析
    ├─ 细胞数：小(<5K) / 中(5-20K) / 大(>20K)
    ├─ 批次数：单批次 / 多批次
    └─ 组织类型：根/叶/花/茎
    ↓
[2] QC 参数调优
    ├─ 查看 QC metrics 分布
    ├─ 确定过滤阈值
    └─ 评估过滤效果
    ↓
[3] 标准化参数调优
    ├─ HVG 数量选择
    ├─ HVG 方法选择
    └─ 是否需要 scaling
    ↓
[4] 批次整合参数调优（如果多批次）
    ├─ 方法选择：Harmony vs scVI
    ├─ 参数调整
    └─ 评估整合效果
    ↓
[5] 聚类参数调优
    ├─ n_neighbors 选择
    ├─ n_pcs 选择
    ├─ resolution 扫描
    └─ 评估聚类质量
    ↓
[6] 注释参数调优
    ├─ Marker 基因选择
    ├─ 置信度阈值
    └─ 手动校正
    ↓
最终结果
```

## 各步骤参数详解

### 1. QC 参数

#### min_genes

**决策树**:
```
查看 violin plot
    ↓
下尾有明显分离? 
    ├─ 是 → 在分离点设置阈值
    └─ 否 → 使用默认值
        ├─ 根组织：200
        ├─ 叶组织：300
        └─ 花组织：250
```

**调优方法**:
```python
import scanpy as sc
import matplotlib.pyplot as plt

# 1. 查看分布
sc.pl.violin(adata, 'n_genes_by_counts')

# 2. 查看百分位数
print(adata.obs['n_genes_by_counts'].quantile([0.01, 0.05, 0.1]))

# 3. 测试不同阈值
for threshold in [100, 200, 300]:
    n_cells = (adata.obs['n_genes_by_counts'] > threshold).sum()
    print(f"Threshold {threshold}: {n_cells} cells retained")
```

#### max_genes

**推荐公式**:
```
max_genes = min(
    95th_percentile,
    median * 3
)
```

**调优方法**:
```python
# 计算推荐值
p95 = adata.obs['n_genes_by_counts'].quantile(0.95)
median = adata.obs['n_genes_by_counts'].median()
recommended = min(p95, median * 3)

print(f"Recommended max_genes: {recommended:.0f}")
```

#### mito_threshold

**植物特异阈值**:
| 组织 | 推荐阈值 | 原因 |
|------|---------|------|
| 根 | 5-10% | 代谢活跃 |
| 叶 | 10-20% | 叶绿体基因多 |
| 茎 | 5-10% | 中等代谢 |
| 花 | 5-10% | 中等代谢 |

### 2. 标准化参数

#### n_hvg (高变基因数量)

**决策表**:
| 数据集大小 | 推荐 HVG 数 | 原因 |
|-----------|------------|------|
| < 5,000 细胞 | 2,000 | 避免过拟合 |
| 5,000-20,000 | 3,000 | 平衡 |
| > 20,000 | 4,000 | 捕获更多变异 |

**调优方法**:
```python
# 测试不同 HVG 数量
for n_hvg in [2000, 3000, 4000]:
    adata_test = adata.copy()
    sc.pp.highly_variable_genes(adata_test, n_top_genes=n_hvg)
    
    # 查看 HVG 分布
    sc.pl.highly_variable_genes(adata_test)
```

#### hvg_flavor (HVG 选择方法)

**方法对比**:
| 方法 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| seurat | 单批次 | 快速，经典 | 不考虑批次 |
| seurat_v3 | 多批次 | 批次感知 | 稍慢 |
| cell_ranger | 10X 数据 | 10X 优化 | 仅适用 10X |

**决策规则**:
```python
if n_batches == 1:
    hvg_flavor = 'seurat'
else:
    hvg_flavor = 'seurat_v3'
```

### 3. 批次整合参数

#### 方法选择

**决策树**:
```
有多个批次?
    ├─ 否 → 跳过整合
    └─ 是 → 
        数据集大小?
        ├─ 大 (>20K) → Harmony (快速)
        └─ 中/小 → scVI (准确)
            有 GPU?
            ├─ 是 → scVI
            └─ 否 → Harmony
```

#### Harmony 参数

| 参数 | 推荐值 | 调优范围 |
|------|--------|---------|
| theta | 2.0 | 1.0-4.0 |
| n_pcs | 50 | 30-100 |
| max_iter | 10 | 10-20 |

**theta 调优**:
- theta 越大，整合越强
- theta 太大会过度整合，丢失生物学差异
- 推荐：先用 2.0，如果批次效应仍明显，增加到 3.0-4.0

#### scVI 参数

| 参数 | 推荐值 | 调优范围 |
|------|--------|---------|
| n_latent | 30 | 10-50 |
| n_layers | 2 | 1-3 |
| n_epochs | 400 | 200-500 |

### 4. 聚类参数

#### n_neighbors

**决策表**:
| 数据集大小 | 推荐值 | 原因 |
|-----------|--------|------|
| < 5,000 | 10 | 小数据集需要小邻域 |
| 5,000-20,000 | 15 | 平衡 |
| > 20,000 | 30 | 大数据集需要大邻域 |

**调优方法**:
```python
# 测试不同 n_neighbors
for n_neighbors in [10, 15, 20, 30]:
    adata_test = adata.copy()
    sc.pp.neighbors(adata_test, n_neighbors=n_neighbors)
    sc.tl.leiden(adata_test, resolution=0.6)
    
    n_clusters = adata_test.obs['leiden'].nunique()
    print(f"n_neighbors={n_neighbors}: {n_clusters} clusters")
```

#### n_pcs

**推荐方法**:
1. 查看 elbow plot
2. 选择 elbow 点之后的 PC 数
3. 通常 30-50 个 PC 足够

```python
# 查看 PCA variance
sc.pl.pca_variance_ratio(adata, n_pcs=50)

# 计算累积方差
import numpy as np
cumsum = np.cumsum(adata.uns['pca']['variance_ratio'])
n_pcs = np.where(cumsum > 0.9)[0][0] + 1
print(f"Recommended n_pcs: {n_pcs}")
```

#### resolution

**扫描策略**:
```python
# 多个 resolution 扫描
resolutions = [0.3, 0.5, 0.7, 0.9, 1.1]

for res in resolutions:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_{res}')
    n_clusters = adata.obs[f'leiden_{res}'].nunique()
    print(f"Resolution {res}: {n_clusters} clusters")

# 可视化所有 resolution
sc.pl.umap(adata, color=[f'leiden_{res}' for res in resolutions])
```

**选择标准**:
1. 生物学合理性 - 是否符合已知细胞类型数量
2. Silhouette score - 聚类质量
3. Modularity - 模块化程度

```python
from sklearn.metrics import silhouette_score

for res in resolutions:
    score = silhouette_score(
        adata.obsm['X_pca'][:, :30],
        adata.obs[f'leiden_{res}']
    )
    print(f"Resolution {res}: silhouette={score:.3f}")
```

### 5. 注释参数

#### confidence_threshold

**推荐阈值**:
| 置信度 | 阈值 | 使用场景 |
|--------|------|---------|
| 高 | 0.8 | 已知组织，Marker 充足 |
| 中 | 0.6 | 一般情况 |
| 低 | 0.4 | 新组织，Marker 不足 |

## 参数调优检查清单

### QC 阶段
- [ ] 查看 QC metrics violin plot
- [ ] 确认过滤阈值合理
- [ ] 检查过滤后细胞数（不应少于 50%）
- [ ] 查看 doublet 比例（应在 5-10%）

### 标准化阶段
- [ ] HVG plot 显示明显的高变基因
- [ ] HVG 数量合理（2000-4000）
- [ ] 如果多批次，使用 batch-aware HVG

### 整合阶段（如果适用）
- [ ] UMAP 上批次混合良好
- [ ] 生物学信号未被过度整合
- [ ] 已知细胞类型仍然分离

### 聚类阶段
- [ ] Elbow plot 确认 PC 数量
- [ ] 测试多个 resolution
- [ ] 聚类数量生物学合理
- [ ] UMAP 显示清晰的细胞群

### 注释阶段
- [ ] Marker 基因在对应 cluster 高表达
- [ ] 置信度分数合理
- [ ] 手动检查可疑注释

## 常见问题

### Q: 如何判断参数是否合适？
**A**: 看下游结果
- 聚类是否生物学合理
- Marker 基因是否特异表达
- 已知细胞类型是否正确分离

### Q: 参数调优需要多久？
**A**: 取决于数据集大小
- 小数据集（<5K）：1-2 小时
- 中数据集（5-20K）：2-4 小时
- 大数据集（>20K）：4-8 小时

### Q: 可以跳过参数调优吗？
**A**: 不推荐
- 使用 Agent 获取推荐参数
- 至少测试 2-3 个 resolution
- 检查关键参数（min_genes, n_hvg, resolution）

## 参考文献

1. Luecken MD, Theis FJ. Current best practices in single-cell RNA-seq analysis: a tutorial. Mol Syst Biol. 2019.
2. Hie B, et al. Efficient integration of heterogeneous single-cell transcriptomes using Scanorama. Nat Biotechnol. 2019.
3. Traag VA, et al. From Louvain to Leiden: guaranteeing well-connected communities. Sci Rep. 2019.
