#!/usr/bin/env python3
"""
Test I/O Utilities

Unit tests for io_utils.py
"""

import pytest
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from pathlib import Path
import tempfile
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts' / 'utils'))
from io_utils import (
    load_h5ad, save_h5ad, ensure_counts_layer,
    validate_obs_column, get_mito_genes, get_chloroplast_genes
)


@pytest.fixture
def sample_adata():
    """Create a sample AnnData object for testing"""
    np.random.seed(42)
    n_obs, n_vars = 100, 50
    X = np.random.poisson(5, size=(n_obs, n_vars))

    obs = pd.DataFrame({
        'cell_id': [f'cell_{i}' for i in range(n_obs)],
        'batch': np.random.choice(['batch1', 'batch2'], n_obs)
    })

    var = pd.DataFrame({
        'gene_id': [f'gene_{i}' for i in range(n_vars)],
        'gene_name': [f'GENE{i}' for i in range(n_vars)]
    })

    # Add some mitochondrial genes
    var.loc[0:4, 'gene_name'] = ['ATMG001', 'ATMG002', 'OSMT001', 'MT-CO1', 'GENE5']

    # Add some chloroplast genes
    var.loc[5:7, 'gene_name'] = ['ATCG001', 'OSCP001', 'GENE8']

    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.var_names = adata.var['gene_name']

    return adata


def test_save_and_load_h5ad(sample_adata):
    """Test saving and loading h5ad files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test.h5ad'

        # Save
        save_h5ad(sample_adata, str(output_path))
        assert output_path.exists()

        # Load
        loaded = load_h5ad(str(output_path))
        assert loaded.n_obs == sample_adata.n_obs
        assert loaded.n_vars == sample_adata.n_vars
        assert np.array_equal(loaded.X, sample_adata.X)


def test_ensure_counts_layer(sample_adata):
    """Test ensuring counts layer exists"""
    # Test with raw counts
    adata = ensure_counts_layer(sample_adata.copy())
    assert 'counts' in adata.layers
    assert np.array_equal(adata.layers['counts'], sample_adata.X)

    # Test with existing counts layer
    sample_adata.layers['counts'] = sample_adata.X.copy()
    adata = ensure_counts_layer(sample_adata.copy())
    assert 'counts' in adata.layers


def test_validate_obs_column(sample_adata):
    """Test validating obs columns"""
    # Test existing column
    assert validate_obs_column(sample_adata, 'batch', raise_error=False)

    # Test non-existing column
    assert not validate_obs_column(sample_adata, 'nonexistent', raise_error=False)

    # Test with raise_error
    with pytest.raises(ValueError):
        validate_obs_column(sample_adata, 'nonexistent', raise_error=True)


def test_get_mito_genes(sample_adata):
    """Test mitochondrial gene detection"""
    mito_mask = get_mito_genes(sample_adata)

    assert isinstance(mito_mask, np.ndarray)
    assert mito_mask.dtype == bool
    assert len(mito_mask) == sample_adata.n_vars

    # Check that known mito genes are detected
    mito_genes = sample_adata.var_names[mito_mask]
    assert 'ATMG001' in mito_genes
    assert 'ATMG002' in mito_genes
    assert 'OSMT001' in mito_genes
    assert 'MT-CO1' in mito_genes


def test_get_chloroplast_genes(sample_adata):
    """Test chloroplast gene detection"""
    cp_mask = get_chloroplast_genes(sample_adata)

    assert isinstance(cp_mask, np.ndarray)
    assert cp_mask.dtype == bool
    assert len(cp_mask) == sample_adata.n_vars

    # Check that known chloroplast genes are detected
    cp_genes = sample_adata.var_names[cp_mask]
    assert 'ATCG001' in cp_genes
    assert 'OSCP001' in cp_genes


def test_load_nonexistent_file():
    """Test loading non-existent file"""
    with pytest.raises(FileNotFoundError):
        load_h5ad('nonexistent.h5ad')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
