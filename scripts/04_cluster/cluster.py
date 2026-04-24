#!/usr/bin/env python3
"""
PCA, Clustering and UMAP Visualization

Performs:
- PCA dimensionality reduction
- KNN graph construction
- Leiden clustering at multiple resolutions
- UMAP visualization
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import matplotlib.pyplot as plt
import seaborn as sns


def run_pca(adata: ad.AnnData, n_pcs: int = 50, use_hvg: bool = True) -> ad.AnnData:
    """Run PCA on the data"""
    print(f"[INFO] Running PCA with {n_pcs} components")

    if use_hvg and 'highly_variable' in adata.var.columns:
        n_hvg = adata.var['highly_variable'].sum()
        print(f"[INFO] Using {n_hvg} highly variable genes")
        sc.tl.pca(adata, n_comps=min(n_pcs, n_hvg - 1), use_highly_variable=True)
    else:
        sc.tl.pca(adata, n_comps=n_pcs)

    return adata


def run_clustering(adata: ad.AnnData, n_neighbors: int = 15, n_pcs: int = 50,
                   resolutions: list = None, algorithm: str = 'leiden',
                   metric: str = 'euclidean') -> ad.AnnData:
    """
    Build KNN graph and run clustering at multiple resolutions

    Args:
        adata: AnnData object with PCA computed
        n_neighbors: Number of neighbors for KNN graph
        n_pcs: Number of PCs to use
        resolutions: List of resolution values
        algorithm: Clustering algorithm (leiden or louvain)
        metric: Distance metric
    """
    if resolutions is None:
        resolutions = [0.4, 0.6, 0.8, 1.0]

    # Build neighbor graph
    n_pcs_avail = adata.obsm['X_pca'].shape[1]
    n_pcs_use = min(n_pcs, n_pcs_avail)

    print(f"[INFO] Computing KNN graph: n_neighbors={n_neighbors}, n_pcs={n_pcs_use}")
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs_use, metric=metric)

    # UMAP
    print(f"[INFO] Computing UMAP")
    sc.tl.umap(adata)

    # Clustering at multiple resolutions
    for res in resolutions:
        key = f'{algorithm}_res{res}'
        print(f"[INFO] Clustering at resolution {res} -> {key}")

        if algorithm == 'leiden':
            sc.tl.leiden(adata, resolution=res, key_added=key)
        elif algorithm == 'louvain':
            sc.tl.louvain(adata, resolution=res, key_added=key)

        n_clusters = adata.obs[key].nunique()
        print(f"[INFO]   Found {n_clusters} clusters")

    # Set default clustering
    default_res = resolutions[len(resolutions) // 2]
    default_key = f'{algorithm}_res{default_res}'
    adata.obs['cluster'] = adata.obs[default_key]

    print(f"[INFO] Default clustering: {default_key} ({adata.obs['cluster'].nunique()} clusters)")

    return adata


def plot_clustering_results(adata: ad.AnnData, sample_id: str,
                           resolutions: list, algorithm: str,
                           output_dir: str):
    """Generate clustering result plots"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Elbow plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(1, len(adata.uns['pca']['variance_ratio']) + 1),
            adata.uns['pca']['variance_ratio'], 'o-')
    ax.set_xlabel('PC')
    ax.set_ylabel('Variance Ratio')
    ax.set_title(f'{sample_id} - PCA Elbow Plot')
    ax.set_xlim(0, 51)
    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_pca_elbow.pdf', dpi=300)
    plt.close()

    # 2. UMAP at multiple resolutions
    n_res = len(resolutions)
    n_cols = min(3, n_res)
    n_rows = (n_res + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))
    if n_res == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for i, res in enumerate(resolutions):
        key = f'{algorithm}_res{res}'
        n_clusters = adata.obs[key].nunique()

        sc.pl.umap(adata, color=key, ax=axes[i], show=False,
                  title=f'Resolution {res} ({n_clusters} clusters)',
                  legend_loc='on data', legend_fontsize=8)

    # Hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_umap_resolutions.pdf', dpi=300)
    plt.close()

    # 3. UMAP with QC metrics
    qc_cols = [c for c in ['n_genes_by_counts', 'total_counts', 'pct_counts_mt',
                            'doublet_score', 'sample_id', 'batch']
               if c in adata.obs.columns]

    if qc_cols:
        n_qc = len(qc_cols)
        n_cols_qc = min(3, n_qc)
        n_rows_qc = (n_qc + n_cols_qc - 1) // n_cols_qc

        fig, axes = plt.subplots(n_rows_qc, n_cols_qc,
                                figsize=(6 * n_cols_qc, 5 * n_rows_qc))
        if n_qc == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        for i, col in enumerate(qc_cols):
            sc.pl.umap(adata, color=col, ax=axes[i], show=False,
                      title=col)

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        plt.savefig(output_path / f'{sample_id}_umap_qc_metrics.pdf', dpi=300)
        plt.close()

    # 4. Cluster size bar plot
    default_key = f'{algorithm}_res{resolutions[len(resolutions)//2]}'
    cluster_counts = adata.obs[default_key].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    cluster_counts.plot(kind='bar', ax=ax, color='steelblue', alpha=0.8)
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Number of Cells')
    ax.set_title(f'{sample_id} - Cluster Sizes (res={resolutions[len(resolutions)//2]})')
    for i, v in enumerate(cluster_counts.values):
        ax.text(i, v + max(cluster_counts) * 0.02, str(v),
               ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_cluster_sizes.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Clustering plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='PCA, clustering and UMAP')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--n_pcs', type=int, default=50, help='Number of PCs')
    parser.add_argument('--n_neighbors', type=int, default=15, help='Number of neighbors')
    parser.add_argument('--resolution', type=float, nargs='+', default=[0.4, 0.6, 0.8, 1.0],
                       help='Clustering resolution(s)')
    parser.add_argument('--algorithm', default='leiden', choices=['leiden', 'louvain'],
                       help='Clustering algorithm')
    parser.add_argument('--metric', default='euclidean', choices=['euclidean', 'cosine'],
                       help='Distance metric')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--clusters_csv', default=None, help='Output cluster assignments CSV')
    parser.add_argument('--plot_dir', default=None, help='Directory for plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # PCA
        adata = run_pca(adata, n_pcs=args.n_pcs)

        # Clustering
        adata = run_clustering(
            adata,
            n_neighbors=args.n_neighbors,
            n_pcs=args.n_pcs,
            resolutions=args.resolution,
            algorithm=args.algorithm,
            metric=args.metric
        )

        # Save cluster assignments
        if args.clusters_csv:
            cluster_cols = [c for c in adata.obs.columns if c.startswith(f'{args.algorithm}_res')]
            cluster_df = adata.obs[['cluster'] + cluster_cols].copy()
            cluster_df['barcode'] = cluster_df.index
            cluster_df.to_csv(args.clusters_csv, index=False)
            print(f"[INFO] Cluster assignments saved to {args.clusters_csv}")

        # Generate plots
        if args.plot_dir:
            plot_clustering_results(
                adata, args.sample_id, args.resolution,
                args.algorithm, args.plot_dir
            )

        # Save output
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Clustered data saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("CLUSTERING SUMMARY")
        print("="*60)
        print(f"Sample ID: {args.sample_id}")
        print(f"Cells: {adata.n_obs}")
        print(f"PCs used: {min(args.n_pcs, adata.obsm['X_pca'].shape[1])}")
        print(f"Algorithm: {args.algorithm}")
        print(f"Resolutions tested: {args.resolution}")
        for res in args.resolution:
            key = f'{args.algorithm}_res{res}'
            n_clusters = adata.obs[key].nunique()
            print(f"  res={res}: {n_clusters} clusters")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
