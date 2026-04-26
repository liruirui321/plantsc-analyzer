#!/usr/bin/env python3
"""
Integration Test: End-to-End Pipeline

Tests the complete analysis pipeline with a small synthetic dataset.
"""

import pytest
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from pathlib import Path
import tempfile
import subprocess
import sys


@pytest.fixture
def synthetic_dataset():
    """Create a synthetic single-cell dataset"""
    np.random.seed(42)

    # Create 3 cell types with distinct expression patterns
    n_cells_per_type = 100
    n_genes = 200

    # Cell type 1: High expression of genes 0-50
    type1 = np.random.poisson(10, size=(n_cells_per_type, n_genes))
    type1[:, 0:50] *= 3

    # Cell type 2: High expression of genes 50-100
    type2 = np.random.poisson(10, size=(n_cells_per_type, n_genes))
    type2[:, 50:100] *= 3

    # Cell type 3: High expression of genes 100-150
    type3 = np.random.poisson(10, size=(n_cells_per_type, n_genes))
    type3[:, 100:150] *= 3

    X = np.vstack([type1, type2, type3])

    obs = pd.DataFrame({
        'cell_id': [f'cell_{i}' for i in range(n_cells_per_type * 3)],
        'batch': ['batch1'] * n_cells_per_type + ['batch2'] * n_cells_per_type + ['batch1'] * n_cells_per_type,
        'true_cell_type': ['type1'] * n_cells_per_type + ['type2'] * n_cells_per_type + ['type3'] * n_cells_per_type
    })

    var = pd.DataFrame({
        'gene_id': [f'gene_{i}' for i in range(n_genes)],
        'gene_name': [f'GENE{i}' for i in range(n_genes)]
    })

    # Add some mitochondrial genes
    var.loc[0:4, 'gene_name'] = ['ATMG001', 'ATMG002', 'ATMG003', 'ATMG004', 'ATMG005']

    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.var_names = adata.var['gene_name']

    return adata


def test_qc_filtering(synthetic_dataset):
    """Test QC and filtering step"""
    adata = synthetic_dataset.copy()

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(adata, inplace=True)

    # Filter cells
    n_cells_before = adata.n_obs
    sc.pp.filter_cells(adata, min_genes=50)
    sc.pp.filter_genes(adata, min_cells=3)

    assert adata.n_obs <= n_cells_before
    assert adata.n_vars > 0


def test_normalization(synthetic_dataset):
    """Test normalization step"""
    adata = synthetic_dataset.copy()

    # Normalize
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Check that data is normalized
    assert adata.X.max() < 20  # Log-normalized values should be small


def test_hvg_selection(synthetic_dataset):
    """Test highly variable gene selection"""
    adata = synthetic_dataset.copy()

    # Normalize first
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Select HVGs
    sc.pp.highly_variable_genes(adata, n_top_genes=100)

    assert 'highly_variable' in adata.var.columns
    assert adata.var['highly_variable'].sum() == 100


def test_pca(synthetic_dataset):
    """Test PCA dimensionality reduction"""
    adata = synthetic_dataset.copy()

    # Preprocess
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=100)

    # PCA
    sc.tl.pca(adata, n_comps=20)

    assert 'X_pca' in adata.obsm
    assert adata.obsm['X_pca'].shape == (adata.n_obs, 20)


def test_clustering(synthetic_dataset):
    """Test clustering"""
    adata = synthetic_dataset.copy()

    # Preprocess
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=100)
    sc.tl.pca(adata, n_comps=20)

    # Clustering
    sc.pp.neighbors(adata, n_neighbors=10)
    sc.tl.leiden(adata, resolution=0.5)

    assert 'leiden' in adata.obs.columns
    # Should find at least 2 clusters
    assert adata.obs['leiden'].nunique() >= 2


def test_umap(synthetic_dataset):
    """Test UMAP visualization"""
    adata = synthetic_dataset.copy()

    # Preprocess
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=100)
    sc.tl.pca(adata, n_comps=20)
    sc.pp.neighbors(adata, n_neighbors=10)

    # UMAP
    sc.tl.umap(adata)

    assert 'X_umap' in adata.obsm
    assert adata.obsm['X_umap'].shape == (adata.n_obs, 2)


def test_deg_analysis(synthetic_dataset):
    """Test differential expression analysis"""
    adata = synthetic_dataset.copy()

    # Preprocess and cluster
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=100)
    sc.tl.pca(adata, n_comps=20)
    sc.pp.neighbors(adata, n_neighbors=10)
    sc.tl.leiden(adata, resolution=0.5)

    # DEG analysis
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

    assert 'rank_genes_groups' in adata.uns
    # Should have results for each cluster
    assert len(adata.uns['rank_genes_groups']['names']) > 0


def test_full_pipeline(synthetic_dataset):
    """Test complete analysis pipeline"""
    adata = synthetic_dataset.copy()

    # Step 1: QC
    sc.pp.calculate_qc_metrics(adata, inplace=True)
    sc.pp.filter_cells(adata, min_genes=50)
    sc.pp.filter_genes(adata, min_cells=3)

    # Step 2: Normalization
    adata.layers['counts'] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Step 3: HVG selection
    sc.pp.highly_variable_genes(adata, n_top_genes=100)

    # Step 4: PCA
    sc.tl.pca(adata, n_comps=20)

    # Step 5: Clustering
    sc.pp.neighbors(adata, n_neighbors=10)
    sc.tl.leiden(adata, resolution=0.5)
    sc.tl.umap(adata)

    # Step 6: DEG analysis
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

    # Verify all steps completed
    assert 'highly_variable' in adata.var.columns
    assert 'X_pca' in adata.obsm
    assert 'leiden' in adata.obs.columns
    assert 'X_umap' in adata.obsm
    assert 'rank_genes_groups' in adata.uns

    # Should identify clusters close to true cell types
    n_clusters = adata.obs['leiden'].nunique()
    assert 2 <= n_clusters <= 5  # Should find 2-5 clusters


def test_save_and_load_pipeline_result(synthetic_dataset):
    """Test saving and loading pipeline results"""
    adata = synthetic_dataset.copy()

    # Run minimal pipeline
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.tl.pca(adata, n_comps=20)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'result.h5ad'

        # Save
        adata.write_h5ad(output_path)

        # Load
        loaded = sc.read_h5ad(output_path)

        assert loaded.n_obs == adata.n_obs
        assert loaded.n_vars == adata.n_vars
        assert 'X_pca' in loaded.obsm


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
