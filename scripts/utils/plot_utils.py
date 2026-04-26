#!/usr/bin/env python3
"""
Plotting Utilities

Common plotting functions for visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Tuple
import scanpy as sc
import anndata as ad


def setup_plot_style():
    """Setup consistent plotting style"""
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['legend.fontsize'] = 9


def save_figure(fig, output_path: str, dpi: int = 300):
    """Save figure with consistent settings"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"[INFO] Saved plot: {output_path}")


def plot_qc_violin(adata: ad.AnnData, keys: List[str],
                   output_path: Optional[str] = None) -> plt.Figure:
    """Plot QC metrics as violin plots"""
    n_keys = len(keys)
    fig, axes = plt.subplots(1, n_keys, figsize=(4*n_keys, 4))
    if n_keys == 1:
        axes = [axes]

    for ax, key in zip(axes, keys):
        sc.pl.violin(adata, keys=key, ax=ax, show=False)

    plt.tight_layout()

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_qc_scatter(adata: ad.AnnData, x: str, y: str,
                    color: Optional[str] = None,
                    output_path: Optional[str] = None) -> plt.Figure:
    """Plot QC scatter plot"""
    fig, ax = plt.subplots(figsize=(6, 5))

    if color:
        sc.pl.scatter(adata, x=x, y=y, color=color, ax=ax, show=False)
    else:
        sc.pl.scatter(adata, x=x, y=y, ax=ax, show=False)

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_highly_variable_genes(adata: ad.AnnData,
                               output_path: Optional[str] = None) -> plt.Figure:
    """Plot highly variable genes"""
    fig = sc.pl.highly_variable_genes(adata, show=False)

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_pca_variance(adata: ad.AnnData, n_pcs: int = 50,
                     output_path: Optional[str] = None) -> plt.Figure:
    """Plot PCA variance ratio (elbow plot)"""
    fig, ax = plt.subplots(figsize=(8, 5))

    variance_ratio = adata.uns['pca']['variance_ratio'][:n_pcs]
    cumsum = np.cumsum(variance_ratio)

    ax.plot(range(1, len(variance_ratio)+1), variance_ratio, 'o-', label='Individual')
    ax.plot(range(1, len(cumsum)+1), cumsum, 's-', label='Cumulative')

    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Variance Ratio')
    ax.set_title('PCA Variance Explained')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_umap_grid(adata: ad.AnnData, color_keys: List[str],
                   ncols: int = 3, size: int = 5,
                   output_path: Optional[str] = None) -> plt.Figure:
    """Plot UMAP grid with multiple colorings"""
    nrows = (len(color_keys) + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(size*ncols, size*nrows))
    axes = axes.flatten() if nrows > 1 else [axes]

    for i, key in enumerate(color_keys):
        if key in adata.obs.columns or key in adata.var_names:
            sc.pl.umap(adata, color=key, ax=axes[i], show=False)
        else:
            axes[i].text(0.5, 0.5, f'Key not found:\n{key}',
                        ha='center', va='center', transform=axes[i].transAxes)
            axes[i].axis('off')

    # Hide unused subplots
    for i in range(len(color_keys), len(axes)):
        axes[i].axis('off')

    plt.tight_layout()

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_marker_heatmap(adata: ad.AnnData, markers: List[str],
                       groupby: str = 'cluster',
                       output_path: Optional[str] = None) -> plt.Figure:
    """Plot marker gene heatmap"""
    # Filter markers that exist in data
    available_markers = [m for m in markers if m in adata.var_names]

    if len(available_markers) == 0:
        print("[WARNING] No markers found in data")
        return None

    fig = sc.pl.heatmap(
        adata,
        var_names=available_markers,
        groupby=groupby,
        cmap='viridis',
        dendrogram=True,
        show=False
    )

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_dotplot(adata: ad.AnnData, markers: List[str],
                groupby: str = 'cluster',
                output_path: Optional[str] = None) -> plt.Figure:
    """Plot marker gene dot plot"""
    available_markers = [m for m in markers if m in adata.var_names]

    if len(available_markers) == 0:
        print("[WARNING] No markers found in data")
        return None

    fig = sc.pl.dotplot(
        adata,
        var_names=available_markers,
        groupby=groupby,
        show=False
    )

    if output_path:
        save_figure(fig, output_path)

    return fig


def plot_cluster_composition(adata: ad.AnnData, cluster_key: str = 'cluster',
                            batch_key: Optional[str] = None,
                            output_path: Optional[str] = None) -> plt.Figure:
    """Plot cluster composition"""
    if batch_key and batch_key in adata.obs.columns:
        # Stacked bar plot by batch
        counts = pd.crosstab(adata.obs[cluster_key], adata.obs[batch_key])
        fig, ax = plt.subplots(figsize=(10, 6))
        counts.plot(kind='bar', stacked=True, ax=ax)
        ax.set_xlabel('Cluster')
        ax.set_ylabel('Number of Cells')
        ax.set_title('Cluster Composition by Batch')
        ax.legend(title=batch_key)
        plt.xticks(rotation=0)
    else:
        # Simple bar plot
        counts = adata.obs[cluster_key].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        counts.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_xlabel('Cluster')
        ax.set_ylabel('Number of Cells')
        ax.set_title('Cluster Sizes')
        plt.xticks(rotation=0)

    plt.tight_layout()

    if output_path:
        save_figure(fig, output_path)

    return fig


# Initialize style on import
setup_plot_style()
