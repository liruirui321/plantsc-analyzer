#!/usr/bin/env python3
"""
I/O Utilities

Common input/output functions for all analysis scripts.
"""

import sys
from pathlib import Path
from typing import Optional, Union
import scanpy as sc
import anndata as ad
import pandas as pd
import numpy as np
from scipy.sparse import issparse


def load_h5ad(path: str, backed: bool = False) -> ad.AnnData:
    """
    Load AnnData from h5ad file with validation

    Args:
        path: Path to h5ad file
        backed: Load in backed mode for large files

    Returns:
        AnnData object
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if backed:
        adata = sc.read_h5ad(path, backed='r')
    else:
        adata = sc.read_h5ad(path)

    print(f"[INFO] Loaded {path.name}: {adata.n_obs} cells, {adata.n_vars} genes")

    return adata


def save_h5ad(adata: ad.AnnData, path: str, compression: str = 'gzip'):
    """Save AnnData to h5ad file"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(path, compression=compression)
    print(f"[INFO] Saved to {path}")


def load_matrix_10x(matrix_dir: str, var_names: str = 'gene_symbols') -> ad.AnnData:
    """Load 10X-format matrix directory"""
    return sc.read_10x_mtx(matrix_dir, var_names=var_names, cache=True)


def ensure_counts_layer(adata: ad.AnnData) -> ad.AnnData:
    """Ensure raw counts are stored in counts layer"""
    if 'counts' not in adata.layers:
        if issparse(adata.X):
            max_val = adata.X.max()
        else:
            max_val = np.max(adata.X)

        if max_val > 100:
            adata.layers['counts'] = adata.X.copy()
        else:
            print("[WARNING] X appears to be normalized, not raw counts")
            adata.layers['counts'] = adata.X.copy()

    return adata


def validate_obs_column(adata: ad.AnnData, column: str, raise_error: bool = True) -> bool:
    """Check if column exists in obs"""
    if column not in adata.obs.columns:
        if raise_error:
            raise ValueError(f"Column '{column}' not found in obs. Available: {list(adata.obs.columns)}")
        return False
    return True


def get_mito_genes(adata: ad.AnnData, prefixes: list = None) -> np.ndarray:
    """
    Get mitochondrial gene mask

    Args:
        adata: AnnData object
        prefixes: List of mitochondrial gene prefixes

    Returns:
        Boolean array of mitochondrial genes
    """
    if prefixes is None:
        prefixes = ['ATMG', 'OSMT', 'MT-', 'mt-', 'Zm-mt', 'LOC_Os-mt']

    mito_mask = np.zeros(adata.n_vars, dtype=bool)
    for prefix in prefixes:
        mito_mask |= adata.var_names.str.startswith(prefix)

    return mito_mask


def get_chloroplast_genes(adata: ad.AnnData, prefixes: list = None) -> np.ndarray:
    """
    Get chloroplast gene mask (plant-specific)

    Args:
        adata: AnnData object
        prefixes: List of chloroplast gene prefixes

    Returns:
        Boolean array of chloroplast genes
    """
    if prefixes is None:
        prefixes = ['ATCG', 'OSCP', 'Zm-cp', 'LOC_Os-cp']

    cp_mask = np.zeros(adata.n_vars, dtype=bool)
    for prefix in prefixes:
        cp_mask |= adata.var_names.str.startswith(prefix)

    return cp_mask
