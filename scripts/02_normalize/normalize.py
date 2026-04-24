#!/usr/bin/env python3
"""
Normalization and Preprocessing

Performs normalization, log transformation, and highly variable gene selection.

Methods:
- Library size normalization (log1p)
- SCTransform (optional)
- Highly variable gene selection (Seurat, Cell Ranger, Seurat v3)
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


def normalize_total(adata: ad.AnnData, target_sum: float = 1e4,
                    exclude_highly_expressed: bool = True) -> ad.AnnData:
    """
    Library size normalization

    Args:
        adata: AnnData object
        target_sum: Target sum for normalization
        exclude_highly_expressed: Exclude highly expressed genes from normalization

    Returns:
        Normalized AnnData
    """
    print(f"[INFO] Normalizing to target sum: {target_sum}")

    # Store raw counts
    adata.layers['counts'] = adata.X.copy()

    # Normalize
    sc.pp.normalize_total(
        adata,
        target_sum=target_sum,
        exclude_highly_expressed=exclude_highly_expressed
    )

    # Log transform
    sc.pp.log1p(adata)

    # Store normalized data
    adata.layers['log1p_norm'] = adata.X.copy()

    print(f"[INFO] Normalization complete")

    return adata


def select_highly_variable_genes(adata: ad.AnnData, n_top_genes: int = 3000,
                                 flavor: str = 'seurat', batch_key: str = None) -> ad.AnnData:
    """
    Select highly variable genes

    Args:
        adata: AnnData object
        n_top_genes: Number of highly variable genes to select
        flavor: Method for HVG selection (seurat, cell_ranger, seurat_v3)
        batch_key: Batch key for batch-aware HVG selection

    Returns:
        AnnData with HVG information
    """
    print(f"[INFO] Selecting {n_top_genes} highly variable genes using {flavor} method")

    if batch_key and batch_key in adata.obs.columns:
        print(f"[INFO] Using batch-aware HVG selection with key: {batch_key}")
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=n_top_genes,
            flavor=flavor,
            batch_key=batch_key,
            subset=False
        )
    else:
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=n_top_genes,
            flavor=flavor,
            subset=False
        )

    n_hvg = adata.var['highly_variable'].sum()
    print(f"[INFO] Selected {n_hvg} highly variable genes")

    return adata


def scale_data(adata: ad.AnnData, max_value: float = 10.0,
               zero_center: bool = True) -> ad.AnnData:
    """
    Scale data to unit variance and zero mean

    Args:
        adata: AnnData object
        max_value: Maximum value after scaling
        zero_center: Zero center the data

    Returns:
        Scaled AnnData
    """
    print(f"[INFO] Scaling data (max_value={max_value})")

    # Scale only HVGs if available
    if 'highly_variable' in adata.var.columns:
        hvg_genes = adata.var_names[adata.var['highly_variable']]
        print(f"[INFO] Scaling {len(hvg_genes)} highly variable genes")
        sc.pp.scale(adata, max_value=max_value, zero_center=zero_center)
    else:
        print(f"[INFO] Scaling all {adata.n_vars} genes")
        sc.pp.scale(adata, max_value=max_value, zero_center=zero_center)

    return adata


def plot_normalization_qc(adata: ad.AnnData, sample_id: str, output_dir: str):
    """
    Generate normalization QC plots

    Args:
        adata: AnnData object
        sample_id: Sample identifier
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'{sample_id} - Normalization QC', fontsize=16)

    # 1. Library size distribution (before normalization)
    if 'counts' in adata.layers:
        lib_sizes = np.array(adata.layers['counts'].sum(axis=1)).flatten()
        axes[0, 0].hist(lib_sizes, bins=100, color='skyblue', edgecolor='black')
        axes[0, 0].set_xlabel('Library Size (UMI counts)')
        axes[0, 0].set_ylabel('Number of Cells')
        axes[0, 0].set_title('Library Size Distribution (Raw)')
        axes[0, 0].set_yscale('log')

    # 2. Library size after normalization
    if 'log1p_norm' in adata.layers:
        norm_lib_sizes = np.array(np.exp(adata.layers['log1p_norm']) - 1).sum(axis=1).flatten()
        axes[0, 1].hist(norm_lib_sizes, bins=100, color='lightgreen', edgecolor='black')
        axes[0, 1].set_xlabel('Library Size (Normalized)')
        axes[0, 1].set_ylabel('Number of Cells')
        axes[0, 1].set_title('Library Size Distribution (Normalized)')
        axes[0, 1].set_yscale('log')

    # 3. Mean-variance relationship
    if 'highly_variable' in adata.var.columns:
        mean_expr = adata.var['means']
        var_expr = adata.var['variances']
        hvg_mask = adata.var['highly_variable']

        axes[0, 2].scatter(mean_expr[~hvg_mask], var_expr[~hvg_mask],
                          s=1, alpha=0.3, c='gray', label='Non-HVG')
        axes[0, 2].scatter(mean_expr[hvg_mask], var_expr[hvg_mask],
                          s=1, alpha=0.5, c='red', label='HVG')
        axes[0, 2].set_xlabel('Mean Expression')
        axes[0, 2].set_ylabel('Variance')
        axes[0, 2].set_xscale('log')
        axes[0, 2].set_yscale('log')
        axes[0, 2].set_title('Mean-Variance Relationship')
        axes[0, 2].legend()

    # 4. HVG dispersion
    if 'dispersions_norm' in adata.var.columns:
        disp = adata.var['dispersions_norm']
        hvg_mask = adata.var['highly_variable']

        axes[1, 0].scatter(mean_expr[~hvg_mask], disp[~hvg_mask],
                          s=1, alpha=0.3, c='gray', label='Non-HVG')
        axes[1, 0].scatter(mean_expr[hvg_mask], disp[hvg_mask],
                          s=1, alpha=0.5, c='red', label='HVG')
        axes[1, 0].set_xlabel('Mean Expression')
        axes[1, 0].set_ylabel('Normalized Dispersion')
        axes[1, 0].set_xscale('log')
        axes[1, 0].set_title('Dispersion vs Mean')
        axes[1, 0].legend()

    # 5. Top HVGs
    if 'highly_variable' in adata.var.columns:
        top_hvg = adata.var[adata.var['highly_variable']].sort_values(
            'dispersions_norm', ascending=False
        ).head(20)

        axes[1, 1].barh(range(len(top_hvg)), top_hvg['dispersions_norm'])
        axes[1, 1].set_yticks(range(len(top_hvg)))
        axes[1, 1].set_yticklabels(top_hvg.index, fontsize=8)
        axes[1, 1].set_xlabel('Normalized Dispersion')
        axes[1, 1].set_title('Top 20 Highly Variable Genes')
        axes[1, 1].invert_yaxis()

    # 6. Expression distribution before/after
    if 'counts' in adata.layers and 'log1p_norm' in adata.layers:
        # Sample 1000 cells for visualization
        n_sample = min(1000, adata.n_obs)
        sample_idx = np.random.choice(adata.n_obs, n_sample, replace=False)

        raw_expr = np.array(adata.layers['counts'][sample_idx, :].mean(axis=0)).flatten()
        norm_expr = np.array(adata.layers['log1p_norm'][sample_idx, :].mean(axis=0)).flatten()

        axes[1, 2].scatter(raw_expr, norm_expr, s=1, alpha=0.3)
        axes[1, 2].set_xlabel('Mean Raw Expression')
        axes[1, 2].set_ylabel('Mean Normalized Expression')
        axes[1, 2].set_xscale('log')
        axes[1, 2].set_title('Raw vs Normalized Expression')

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_normalization_qc.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Normalization QC plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Normalize and preprocess single-cell data')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--method', default='log1p', choices=['log1p', 'sctransform'],
                       help='Normalization method')
    parser.add_argument('--target_sum', type=float, default=1e4,
                       help='Target sum for library size normalization')
    parser.add_argument('--n_top_genes', type=int, default=3000,
                       help='Number of highly variable genes')
    parser.add_argument('--hvg_flavor', default='seurat',
                       choices=['seurat', 'cell_ranger', 'seurat_v3'],
                       help='Method for HVG selection')
    parser.add_argument('--batch_key', default=None,
                       help='Batch key for batch-aware HVG selection')
    parser.add_argument('--scale', action='store_true',
                       help='Scale data after normalization')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--hvg_list', default=None, help='Output HVG list CSV')
    parser.add_argument('--plot_dir', default=None, help='Directory for QC plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Normalize
        if args.method == 'log1p':
            adata = normalize_total(adata, target_sum=args.target_sum)
        elif args.method == 'sctransform':
            print("[WARNING] SCTransform not yet implemented, using log1p")
            adata = normalize_total(adata, target_sum=args.target_sum)

        # Select highly variable genes
        adata = select_highly_variable_genes(
            adata,
            n_top_genes=args.n_top_genes,
            flavor=args.hvg_flavor,
            batch_key=args.batch_key
        )

        # Save HVG list
        if args.hvg_list:
            hvg_df = adata.var[adata.var['highly_variable']].copy()
            hvg_df['gene'] = hvg_df.index
            hvg_df = hvg_df[['gene', 'means', 'dispersions', 'dispersions_norm']]
            hvg_df = hvg_df.sort_values('dispersions_norm', ascending=False)
            hvg_df.to_csv(args.hvg_list, index=False)
            print(f"[INFO] HVG list saved to {args.hvg_list}")

        # Scale data
        if args.scale:
            adata = scale_data(adata)

        # Generate QC plots
        if args.plot_dir:
            plot_normalization_qc(adata, args.sample_id, args.plot_dir)

        # Save output
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Normalized data saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("NORMALIZATION SUMMARY")
        print("="*60)
        print(f"Sample ID: {args.sample_id}")
        print(f"Method: {args.method}")
        print(f"Cells: {adata.n_obs}")
        print(f"Genes: {adata.n_vars}")
        print(f"Highly variable genes: {adata.var['highly_variable'].sum()}")
        print(f"Scaled: {args.scale}")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
