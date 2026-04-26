#!/usr/bin/env python3
"""
Test Parameter Recommender

Unit tests for parameter_recommender.py
"""

import pytest
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from pathlib import Path
import sys

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'agent'))
from parameter_recommender import ParameterRecommender


@pytest.fixture
def small_adata():
    """Create a small dataset for testing"""
    np.random.seed(42)
    n_obs, n_vars = 1000, 500
    X = np.random.poisson(5, size=(n_obs, n_vars))

    obs = pd.DataFrame({
        'batch': ['batch1'] * n_obs
    })

    adata = ad.AnnData(X=X, obs=obs)
    return adata


@pytest.fixture
def medium_adata():
    """Create a medium dataset for testing"""
    np.random.seed(42)
    n_obs, n_vars = 10000, 2000
    X = np.random.poisson(5, size=(n_obs, n_vars))

    obs = pd.DataFrame({
        'batch': np.random.choice(['batch1', 'batch2'], n_obs)
    })

    adata = ad.AnnData(X=X, obs=obs)
    return adata


@pytest.fixture
def large_adata():
    """Create a large dataset for testing"""
    np.random.seed(42)
    n_obs, n_vars = 50000, 3000
    X = np.random.poisson(5, size=(n_obs, n_vars))

    obs = pd.DataFrame({
        'batch': np.random.choice(['batch1', 'batch2', 'batch3'], n_obs)
    })

    adata = ad.AnnData(X=X, obs=obs)
    return adata


def test_analyze_data_characteristics_small(small_adata):
    """Test data characteristics analysis for small dataset"""
    recommender = ParameterRecommender()
    chars = recommender.analyze_data_characteristics(small_adata)

    assert chars['n_cells'] == 1000
    assert chars['n_genes'] == 500
    assert chars['dataset_size'] == 'small'
    assert chars['n_batches'] == 1


def test_analyze_data_characteristics_medium(medium_adata):
    """Test data characteristics analysis for medium dataset"""
    recommender = ParameterRecommender()
    chars = recommender.analyze_data_characteristics(medium_adata)

    assert chars['n_cells'] == 10000
    assert chars['n_genes'] == 2000
    assert chars['dataset_size'] == 'medium'
    assert chars['n_batches'] == 2


def test_analyze_data_characteristics_large(large_adata):
    """Test data characteristics analysis for large dataset"""
    recommender = ParameterRecommender()
    chars = recommender.analyze_data_characteristics(large_adata)

    assert chars['n_cells'] == 50000
    assert chars['n_genes'] == 3000
    assert chars['dataset_size'] == 'large'
    assert chars['n_batches'] == 3


def test_recommend_qc_params(small_adata):
    """Test QC parameter recommendations"""
    recommender = ParameterRecommender()
    params = recommender.recommend_qc_params(small_adata)

    assert 'min_genes' in params
    assert 'max_genes' in params
    assert 'mito_threshold' in params
    assert 'run_scrublet' in params
    assert 'reasoning' in params

    # Small dataset should not run scrublet
    assert params['run_scrublet'] == False


def test_recommend_normalization_params_small(small_adata):
    """Test normalization parameter recommendations for small dataset"""
    recommender = ParameterRecommender()
    params = recommender.recommend_normalization_params(small_adata)

    assert params['n_hvg'] == 2000  # Small dataset
    assert params['hvg_flavor'] == 'seurat'  # Single batch
    assert params['hvg_batch_key'] is None


def test_recommend_normalization_params_medium(medium_adata):
    """Test normalization parameter recommendations for medium dataset"""
    recommender = ParameterRecommender()
    params = recommender.recommend_normalization_params(medium_adata)

    assert params['n_hvg'] == 3000  # Medium dataset
    assert params['hvg_flavor'] == 'seurat_v3'  # Multiple batches
    assert params['hvg_batch_key'] == 'batch'


def test_recommend_integration_params_single_batch(small_adata):
    """Test integration recommendations for single batch"""
    recommender = ParameterRecommender()
    params = recommender.recommend_integration_params(small_adata)

    assert params['run'] == False
    assert 'reasoning' in params


def test_recommend_integration_params_multi_batch(medium_adata):
    """Test integration recommendations for multiple batches"""
    recommender = ParameterRecommender()
    params = recommender.recommend_integration_params(medium_adata)

    assert params['run'] == True
    assert params['method'] in ['harmony', 'scvi']
    assert params['batch_key'] == 'batch'


def test_recommend_clustering_params_small(small_adata):
    """Test clustering parameter recommendations for small dataset"""
    recommender = ParameterRecommender()
    params = recommender.recommend_clustering_params(small_adata)

    assert params['n_neighbors'] == 10  # Small dataset
    assert params['algorithm'] == 'leiden'
    assert len(params['resolution']) == 3


def test_recommend_clustering_params_large(large_adata):
    """Test clustering parameter recommendations for large dataset"""
    recommender = ParameterRecommender()
    params = recommender.recommend_clustering_params(large_adata)

    assert params['n_neighbors'] == 30  # Large dataset
    assert len(params['resolution']) == 4


def test_recommend_all_params(medium_adata):
    """Test comprehensive parameter recommendations"""
    recommender = ParameterRecommender()
    all_params = recommender.recommend_all_params(medium_adata)

    assert 'data_characteristics' in all_params
    assert 'qc' in all_params
    assert 'normalization' in all_params
    assert 'integration' in all_params
    assert 'clustering' in all_params

    # Check data characteristics
    chars = all_params['data_characteristics']
    assert chars['n_cells'] == 10000
    assert chars['dataset_size'] == 'medium'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
