#!/usr/bin/env python3
"""
Harmony Batch Integration

Integrates multiple samples using Harmony algorithm to remove batch effects.

Reference: Korsunsky et al. (2019) Nature Methods
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import matplotlib.pyplot as plt


def run_harmony(adata: ad.AnnData, batch_key: str = 'batch',
                n_pcs: int = 50, theta: float = 2.0) -> ad.AnnData:
    """
    Run Harmony integration

    Args:
        adata: AnnData object with PCA computed
        batch_key: Column name for batch information
        n_pcs: Number of PCs to use
        theta: Harmony theta parameter (diversity clustering penalty)

    Returns:
        AnnData with corrected embeddings
    """
    print(f"[INFO] Running Harmony integration")
    print(f"[INFO] Batch key: {batch_key}")
    print(f"[INFO] Batches: {adata.obs[batch_key].nunique()}")
    for batch, count in adata.obs[batch_key].value_counts().items():
        print(f"  {batch}: {count} cells")

    # Ensure PCA is computed
    if 'X_pca' not in adata.obsm:
        print(f"[INFO] Computing PCA with {n_pcs} components")
        sc.tl.pca(adata, n_comps=n_pcs)

    # Run Harmony
    try:
        import harmonypy as hm

        # Get PCA matrix
        pca_matrix = adata.obsm['X_pca'][:, :n_pcs]
        batch_labels = adata.obs[batch_key].values

        # Run harmony
        harmony_out = hm.run_harmony(
            pca_matrix,
            adata.obs,
            batch_key,
            theta=theta,
            max_iter_harmony=20,
            verbose=True
        )

        # Store corrected PCA
        adata.obsm['X_pca_harmony'] = harmony_out.Z_corr.T

        print(f"[INFO] Harmony integration complete")

    except ImportError:
        print("[WARNING] harmonypy not installed, falling back to scanpy integration")
        sc.external.pp.harmony_integrate(adata, key=batch_key, basis='X_pca',
                                          adjusted_basis='X_pca_harmony')

    # Recompute neighbors and UMAP using corrected PCA
    print(f"[INFO] Recomputing neighbors and UMAP with corrected embeddings")
    sc.pp.neighbors(adata, use_rep='X_pca_harmony', n_pcs=n_pcs)
    sc.tl.umap(adata)

    return adata


def plot_integration_results(adata: ad.AnnData, batch_key: str,
                              sample_id: str, output_dir: str):
    """Generate integration QC plots"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sc.pl.umap(adata, color=batch_key, ax=axes[0], show=False,
              title='UMAP colored by Batch')
    sc.pl.umap(adata, color='cluster' if 'cluster' in adata.obs else batch_key,
              ax=axes[1], show=False, title='UMAP colored by Cluster')

    plt.tight_layout()
    plt.savefig(output_path / f'harmony_integration_report.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Integration plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Harmony batch integration')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--batch_key', default='batch', help='Batch column name')
    parser.add_argument('--n_pcs', type=int, default=50, help='Number of PCs')
    parser.add_argument('--theta', type=float, default=2.0, help='Harmony theta')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--plot_dir', default=None, help='Directory for plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Check batch key exists
        if args.batch_key not in adata.obs.columns:
            raise ValueError(f"Batch key '{args.batch_key}' not found in obs. "
                           f"Available: {list(adata.obs.columns)}")

        # Run Harmony
        adata = run_harmony(adata, batch_key=args.batch_key,
                           n_pcs=args.n_pcs, theta=args.theta)

        # Generate plots
        if args.plot_dir:
            plot_integration_results(adata, args.batch_key, 'harmony', args.plot_dir)

        # Save
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Integrated data saved to {args.output}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
