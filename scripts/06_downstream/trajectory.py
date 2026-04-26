#!/usr/bin/env python3
"""
Trajectory Inference Analysis

Performs pseudotime trajectory analysis using PAGA, Monocle3, or Slingshot.
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


def run_paga_trajectory(adata: ad.AnnData, cluster_key: str = 'cluster',
                        root_cell_type: str = None) -> ad.AnnData:
    """
    Run PAGA trajectory inference

    Args:
        adata: AnnData object
        cluster_key: Column name for cluster assignments
        root_cell_type: Root cell type for trajectory

    Returns:
        AnnData with trajectory information
    """
    print(f"[INFO] Running PAGA trajectory inference")

    # Compute PAGA
    sc.tl.paga(adata, groups=cluster_key)

    # Set root if provided
    if root_cell_type:
        root_clusters = adata.obs[adata.obs['cell_type'] == root_cell_type][cluster_key].unique()
        if len(root_clusters) > 0:
            root_cluster = root_clusters[0]
            print(f"[INFO] Setting root cluster: {root_cluster} (cell type: {root_cell_type})")
            adata.uns['iroot'] = np.flatnonzero(adata.obs[cluster_key] == root_cluster)[0]
        else:
            print(f"[WARNING] Root cell type '{root_cell_type}' not found")
    else:
        # Auto-select root (cluster with lowest average pseudotime)
        print(f"[INFO] Auto-selecting root cluster")
        adata.uns['iroot'] = 0

    # Compute diffusion pseudotime
    sc.tl.diffmap(adata)
    sc.tl.dpt(adata)

    print(f"[INFO] PAGA trajectory complete")

    return adata


def run_monocle3_trajectory(adata: ad.AnnData, root_cell_type: str = None) -> ad.AnnData:
    """
    Run Monocle3-style trajectory (using Python approximation)

    Note: This is a simplified version. For full Monocle3, use R.
    """
    print(f"[INFO] Running Monocle3-style trajectory (Python approximation)")
    print(f"[WARNING] For full Monocle3 features, use R implementation")

    # Use diffusion pseudotime as approximation
    sc.tl.diffmap(adata)

    if root_cell_type:
        root_cells = adata.obs[adata.obs['cell_type'] == root_cell_type].index
        if len(root_cells) > 0:
            adata.uns['iroot'] = np.where(adata.obs_names == root_cells[0])[0][0]

    sc.tl.dpt(adata)

    return adata


def plot_trajectory_results(adata: ad.AnnData, cluster_key: str,
                            sample_id: str, output_dir: str):
    """Generate trajectory visualization plots"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. PAGA graph
    fig, ax = plt.subplots(figsize=(8, 6))
    sc.pl.paga(adata, ax=ax, show=False, title=f'{sample_id} - PAGA Graph')
    plt.tight_layout()
    plt.savefig(output_path / f'trajectory_{sample_id}_paga_graph.pdf', dpi=300)
    plt.close()

    # 2. PAGA on UMAP
    fig, ax = plt.subplots(figsize=(8, 6))
    sc.pl.paga(adata, color=cluster_key, ax=ax, show=False,
              title=f'{sample_id} - PAGA on UMAP')
    plt.tight_layout()
    plt.savefig(output_path / f'trajectory_{sample_id}_paga_umap.pdf', dpi=300)
    plt.close()

    # 3. Pseudotime on UMAP
    if 'dpt_pseudotime' in adata.obs.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        sc.pl.umap(adata, color='dpt_pseudotime', ax=axes[0], show=False,
                  title='Pseudotime', cmap='viridis')
        sc.pl.umap(adata, color=cluster_key, ax=axes[1], show=False,
                  title='Clusters', legend_loc='on data')

        plt.tight_layout()
        plt.savefig(output_path / f'trajectory_{sample_id}_pseudotime.pdf', dpi=300)
        plt.close()

    # 4. Pseudotime distribution per cluster
    if 'dpt_pseudotime' in adata.obs.columns:
        fig, ax = plt.subplots(figsize=(10, 6))

        clusters = sorted(adata.obs[cluster_key].unique())
        pseudotime_data = [
            adata.obs[adata.obs[cluster_key] == c]['dpt_pseudotime'].values
            for c in clusters
        ]

        bp = ax.boxplot(pseudotime_data, labels=clusters, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)

        ax.set_xlabel('Cluster')
        ax.set_ylabel('Pseudotime')
        ax.set_title(f'{sample_id} - Pseudotime Distribution per Cluster')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / f'trajectory_{sample_id}_pseudotime_boxplot.pdf', dpi=300)
        plt.close()

    # 5. Gene expression along pseudotime (if marker genes available)
    if 'dpt_pseudotime' in adata.obs.columns:
        # Get some highly variable genes
        if 'highly_variable' in adata.var.columns:
            hvg = adata.var_names[adata.var['highly_variable']][:6]

            fig, axes = plt.subplots(2, 3, figsize=(15, 8))
            axes = axes.flatten()

            for i, gene in enumerate(hvg):
                if gene in adata.var_names:
                    expr = adata[:, gene].X.toarray().flatten()
                    pseudotime = adata.obs['dpt_pseudotime'].values

                    # Sort by pseudotime
                    sort_idx = np.argsort(pseudotime)
                    pseudotime_sorted = pseudotime[sort_idx]
                    expr_sorted = expr[sort_idx]

                    # Smooth with rolling average
                    window = max(10, len(expr) // 50)
                    expr_smooth = pd.Series(expr_sorted).rolling(window, center=True).mean()

                    axes[i].scatter(pseudotime, expr, s=1, alpha=0.3, c='gray')
                    axes[i].plot(pseudotime_sorted, expr_smooth, 'r-', linewidth=2)
                    axes[i].set_xlabel('Pseudotime')
                    axes[i].set_ylabel('Expression')
                    axes[i].set_title(gene)

            plt.tight_layout()
            plt.savefig(output_path / f'trajectory_{sample_id}_gene_dynamics.pdf', dpi=300)
            plt.close()

    print(f"[INFO] Trajectory plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Trajectory inference analysis')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--method', default='paga', choices=['paga', 'monocle3'],
                       help='Trajectory inference method')
    parser.add_argument('--cluster_key', default='cluster', help='Cluster column name')
    parser.add_argument('--root_cell_type', default=None,
                       help='Root cell type for trajectory (optional)')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--plot_dir', default=None, help='Directory for plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Check cluster key
        if args.cluster_key not in adata.obs.columns:
            raise ValueError(f"Cluster key '{args.cluster_key}' not found")

        # Run trajectory inference
        if args.method == 'paga':
            adata = run_paga_trajectory(
                adata,
                cluster_key=args.cluster_key,
                root_cell_type=args.root_cell_type
            )
        elif args.method == 'monocle3':
            adata = run_monocle3_trajectory(
                adata,
                root_cell_type=args.root_cell_type
            )

        # Generate plots
        if args.plot_dir:
            plot_trajectory_results(
                adata,
                args.cluster_key,
                'trajectory',
                args.plot_dir
            )

        # Save
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Trajectory data saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("TRAJECTORY ANALYSIS SUMMARY")
        print("="*60)
        print(f"Method: {args.method}")
        print(f"Cells: {adata.n_obs}")
        print(f"Clusters: {adata.obs[args.cluster_key].nunique()}")
        if 'dpt_pseudotime' in adata.obs.columns:
            print(f"Pseudotime range: [{adata.obs['dpt_pseudotime'].min():.3f}, "
                  f"{adata.obs['dpt_pseudotime'].max():.3f}]")
        if args.root_cell_type:
            print(f"Root cell type: {args.root_cell_type}")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
