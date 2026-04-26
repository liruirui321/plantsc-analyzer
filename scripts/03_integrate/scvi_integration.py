#!/usr/bin/env python3
"""
scVI Batch Integration

Integrates multiple samples using scVI (single-cell Variational Inference)
deep learning model to remove batch effects.

Reference: Lopez et al. (2018) Nature Methods
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import matplotlib.pyplot as plt


def run_scvi(adata: ad.AnnData, batch_key: str = 'batch',
             n_latent: int = 30, n_layers: int = 2,
             n_epochs: int = 400, use_gpu: bool = False) -> ad.AnnData:
    """
    Run scVI integration

    Args:
        adata: AnnData object
        batch_key: Column name for batch information
        n_latent: Number of latent dimensions
        n_layers: Number of hidden layers
        n_epochs: Number of training epochs
        use_gpu: Use GPU for training

    Returns:
        AnnData with corrected embeddings
    """
    print(f"[INFO] Running scVI integration")
    print(f"[INFO] Batch key: {batch_key}")
    print(f"[INFO] Batches: {adata.obs[batch_key].nunique()}")
    for batch, count in adata.obs[batch_key].value_counts().items():
        print(f"  {batch}: {count} cells")

    try:
        import scvi

        # Setup AnnData for scVI
        scvi.model.SCVI.setup_anndata(
            adata,
            layer='counts',
            batch_key=batch_key
        )

        # Create and train model
        print(f"[INFO] Training scVI model (n_latent={n_latent}, n_layers={n_layers}, n_epochs={n_epochs})")
        model = scvi.model.SCVI(
            adata,
            n_latent=n_latent,
            n_layers=n_layers,
            gene_likelihood='nb'
        )

        model.train(
            max_epochs=n_epochs,
            use_gpu=use_gpu,
            early_stopping=True,
            early_stopping_patience=20
        )

        # Get latent representation
        print(f"[INFO] Extracting latent representation")
        adata.obsm['X_scvi'] = model.get_latent_representation()

        # Get normalized expression
        adata.layers['scvi_normalized'] = model.get_normalized_expression()

        print(f"[INFO] scVI integration complete")

    except ImportError:
        print("[ERROR] scvi-tools not installed. Install with: pip install scvi-tools")
        raise

    # Recompute neighbors and UMAP using scVI latent space
    print(f"[INFO] Recomputing neighbors and UMAP with scVI embeddings")
    sc.pp.neighbors(adata, use_rep='X_scvi')
    sc.tl.umap(adata)

    return adata


def plot_integration_results(adata: ad.AnnData, batch_key: str,
                              sample_id: str, output_dir: str):
    """Generate integration QC plots"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # UMAP colored by batch
    sc.pl.umap(adata, color=batch_key, ax=axes[0, 0], show=False,
              title='UMAP colored by Batch')

    # UMAP colored by cluster
    if 'cluster' in adata.obs:
        sc.pl.umap(adata, color='cluster', ax=axes[0, 1], show=False,
                  title='UMAP colored by Cluster')

    # UMAP colored by n_genes
    sc.pl.umap(adata, color='n_genes_by_counts', ax=axes[1, 0], show=False,
              title='UMAP colored by Gene Count')

    # UMAP colored by total_counts
    sc.pl.umap(adata, color='total_counts', ax=axes[1, 1], show=False,
              title='UMAP colored by UMI Count')

    plt.tight_layout()
    plt.savefig(output_path / f'scvi_integration_report.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Integration plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='scVI batch integration')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--batch_key', default='batch', help='Batch column name')
    parser.add_argument('--n_latent', type=int, default=30, help='Number of latent dimensions')
    parser.add_argument('--n_layers', type=int, default=2, help='Number of hidden layers')
    parser.add_argument('--n_epochs', type=int, default=400, help='Number of training epochs')
    parser.add_argument('--use_gpu', action='store_true', help='Use GPU for training')
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

        # Check if counts layer exists
        if 'counts' not in adata.layers:
            print("[WARNING] 'counts' layer not found, using X as counts")
            adata.layers['counts'] = adata.X.copy()

        # Run scVI
        adata = run_scvi(
            adata,
            batch_key=args.batch_key,
            n_latent=args.n_latent,
            n_layers=args.n_layers,
            n_epochs=args.n_epochs,
            use_gpu=args.use_gpu
        )

        # Generate plots
        if args.plot_dir:
            plot_integration_results(adata, args.batch_key, 'scvi', args.plot_dir)

        # Save
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Integrated data saved to {args.output}")

        print("\n" + "="*60)
        print("scVI INTEGRATION SUMMARY")
        print("="*60)
        print(f"Cells: {adata.n_obs}")
        print(f"Genes: {adata.n_vars}")
        print(f"Batches: {adata.obs[args.batch_key].nunique()}")
        print(f"Latent dimensions: {args.n_latent}")
        print(f"Training epochs: {args.n_epochs}")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
