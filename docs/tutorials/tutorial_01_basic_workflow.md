# Tutorial 1: Basic Analysis Workflow

## Overview

This tutorial walks through a complete single-cell RNA-seq analysis using PlantSC-Analyzer with a small Arabidopsis root dataset.

**Time**: ~30 minutes  
**Level**: Beginner  
**Dataset**: Arabidopsis root (5,000 cells)

---

## Prerequisites

- PlantSC-Analyzer installed
- Basic command-line knowledge
- ~8GB RAM available

---

## Step 1: Prepare Your Data

### Download Example Data

```bash
# Create working directory
mkdir -p ~/plantsc_tutorial
cd ~/plantsc_tutorial

# Download example data (placeholder - replace with actual data)
# wget https://example.com/arabidopsis_root_sample.h5ad
```

### Create Sample Sheet

Create `samples.csv`:

```csv
sample_id,matrix_path,batch,condition
root_ctrl,./data/root_ctrl.h5ad,batch1,control
root_treat,./data/root_treat.h5ad,batch1,treatment
```

---

## Step 2: Quick Data Inspection

```python
import scanpy as sc

# Load data
adata = sc.read_h5ad('data/root_ctrl.h5ad')

# Basic info
print(f"Cells: {adata.n_obs}")
print(f"Genes: {adata.n_vars}")

# Quick QC
sc.pp.calculate_qc_metrics(adata, inplace=True)
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts'])
```

---

## Step 3: Get Parameter Recommendations

Use the Agent to get intelligent parameter recommendations:

```bash
python agent/plant_sc_agent.py --analyze data/root_ctrl.h5ad
```

**Output**:
```
[INFO] Dataset characteristics:
  Cells: 5000
  Genes: 20000
  Dataset size: small
  Batches: 1

PARAMETER RECOMMENDATIONS
==========================

QC:
  min_genes: 200
  max_genes: 5500
  mito_threshold: 5.0
  
  Reasoning:
    - Based on 5th percentile of gene counts (200)
    - Based on 95th percentile of gene counts (5500)
    
NORMALIZATION:
  n_hvg: 2000
  hvg_flavor: seurat
  
  Reasoning:
    - Recommended 2000 HVGs for small dataset
```

---

## Step 4: Run Complete Analysis

### Option A: Using Nextflow (Recommended)

```bash
nextflow run workflows/main.nf \
    --sample_sheet samples.csv \
    --species arabidopsis \
    --tissue root \
    --qc.min_genes 200 \
    --qc.max_genes 5500 \
    --normalize.n_hvg 2000 \
    --cluster.resolution 0.4,0.6,0.8 \
    --outdir results \
    -profile standard
```

### Option B: Step-by-Step with Python

```python
import scanpy as sc
import pandas as pd

# Load data
adata = sc.read_h5ad('data/root_ctrl.h5ad')

# Step 1: QC
sc.pp.calculate_qc_metrics(adata, inplace=True)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, max_genes=5500)
sc.pp.filter_genes(adata, min_cells=3)

print(f"After QC: {adata.n_obs} cells, {adata.n_vars} genes")

# Step 2: Normalization
adata.layers['counts'] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# Step 3: PCA
sc.tl.pca(adata, n_comps=50)
sc.pl.pca_variance_ratio(adata, n_pcs=50)

# Step 4: Clustering
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.6)
sc.tl.umap(adata)

# Visualize
sc.pl.umap(adata, color='leiden')

# Step 5: Find marker genes
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10)

# Save
adata.write_h5ad('results/analyzed.h5ad')
```

---

## Step 5: Explore Results

### View HTML Report

```bash
open results/report.html
```

### Load Results in Python

```python
import scanpy as sc

# Load annotated data
adata = sc.read_h5ad('results/05_annotate/annotated.h5ad')

# View cell types
print(adata.obs['cell_type'].value_counts())

# Visualize
sc.pl.umap(adata, color='cell_type', legend_loc='on data')

# Check specific markers
sc.pl.umap(adata, color=['VND7', 'SHR', 'SCR'])
```

### Export Results

```python
# Export cell type annotations
adata.obs[['cell_type', 'leiden']].to_csv('cell_annotations.csv')

# Export marker genes
markers = sc.get.rank_genes_groups_df(adata, group='0')
markers.to_csv('cluster0_markers.csv')
```

---

## Step 6: Cell Type Annotation

### Query Known Markers

```bash
python agent/plant_sc_agent.py --query_markers arabidopsis
```

### Manual Annotation

```python
# Define cell types based on markers
cell_type_map = {
    '0': 'Xylem',
    '1': 'Phloem',
    '2': 'Epidermis',
    '3': 'Endodermis',
    '4': 'Cortex'
}

adata.obs['cell_type'] = adata.obs['leiden'].map(cell_type_map)

# Visualize
sc.pl.umap(adata, color='cell_type')
```

---

## Step 7: Downstream Analysis

### Differential Expression

```python
# Compare conditions
sc.tl.rank_genes_groups(adata, 'condition', method='wilcoxon')

# Get DEGs
degs = sc.get.rank_genes_groups_df(adata, group='treatment')
degs_sig = degs[degs['pvals_adj'] < 0.05]

print(f"Found {len(degs_sig)} DEGs")
```

### Trajectory Analysis

```python
# Run PAGA
sc.tl.paga(adata, groups='cell_type')
sc.pl.paga(adata)

# Compute pseudotime
sc.tl.diffmap(adata)
adata.uns['iroot'] = 0  # Set root cell
sc.tl.dpt(adata)

# Visualize
sc.pl.umap(adata, color='dpt_pseudotime', cmap='viridis')
```

---

## Expected Results

After completing this tutorial, you should have:

1. ✅ Filtered dataset (~4,500 cells)
2. ✅ 5-8 cell clusters
3. ✅ Cell type annotations
4. ✅ Marker genes for each cluster
5. ✅ UMAP visualization
6. ✅ HTML analysis report

---

## Troubleshooting

### Issue: Too many/few clusters

**Solution**: Adjust resolution parameter
```bash
--cluster.resolution 0.3,0.5,0.7  # Lower for fewer clusters
--cluster.resolution 0.8,1.0,1.2  # Higher for more clusters
```

### Issue: Poor cell type separation

**Solution**: 
1. Increase HVG number: `--normalize.n_hvg 3000`
2. Use more PCs: `--cluster.n_pcs 50`
3. Check batch effects

### Issue: Memory error

**Solution**:
1. Reduce HVG: `--normalize.n_hvg 1500`
2. Reduce PCs: `--cluster.n_pcs 30`
3. Process samples separately

---

## Next Steps

- **Tutorial 2**: Multi-sample integration
- **Tutorial 3**: Custom marker genes
- **Tutorial 4**: Advanced visualization

---

## Summary

In this tutorial, you learned:
- ✅ How to prepare input data
- ✅ How to get parameter recommendations
- ✅ How to run complete analysis
- ✅ How to explore and visualize results
- ✅ How to annotate cell types
- ✅ How to perform downstream analysis

**Congratulations!** You've completed your first PlantSC analysis! 🎉
