#!/usr/bin/env python3
"""
Cell and Gene Filtering

Filters cells and genes based on QC metrics:
- Minimum/maximum genes per cell
- Minimum cells per gene
- Mitochondrial content threshold
- Doublet filtering
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


def calculate_qc_metrics(adata: ad.AnnData, mito_prefix: str = 'ATMG') -> ad.AnnData:
    """
    Calculate QC metrics for cells and genes

    Args:
        adata: AnnData object
        mito_prefix: Prefix for mitochondrial genes

    Returns:
        AnnData with QC metrics added
    """
    print("[INFO] Calculating QC metrics...")

    # Identify mitochondrial genes
    adata.var['mt'] = adata.var_names.str.startswith(mito_prefix) | \
                      adata.var_names.str.startswith('MT-') | \
                      adata.var_names.str.startswith('mt-') | \
                      adata.var_names.str.startswith('OSMT')  # Rice

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars=['mt'],
        percent_top=None,
        log1p=False,
        inplace=True
    )

    print(f"[INFO] Mitochondrial genes detected: {adata.var['mt'].sum()}")

    return adata


def plot_qc_metrics(adata: ad.AnnData, sample_id: str, output_dir: str,
                   thresholds: dict = None):
    """
    Generate QC metric plots

    Args:
        adata: AnnData object with QC metrics
        sample_id: Sample identifier
        output_dir: Output directory
        thresholds: Dict of filtering thresholds
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'{sample_id} - QC Metrics', fontsize=16)

    # 1. Total counts distribution
    axes[0, 0].hist(adata.obs['total_counts'], bins=100, color='skyblue', edgecolor='black')
    axes[0, 0].set_xlabel('Total counts per cell')
    axes[0, 0].set_ylabel('Number of cells')
    axes[0, 0].set_yscale('log')
    axes[0, 0].set_title('Total Counts Distribution')

    # 2. Number of genes distribution
    axes[0, 1].hist(adata.obs['n_genes_by_counts'], bins=100, color='lightgreen', edgecolor='black')
    if thresholds:
        if 'min_genes' in thresholds:
            axes[0, 1].axvline(thresholds['min_genes'], color='red', linestyle='--',
                             label=f"min={thresholds['min_genes']}")
        if 'max_genes' in thresholds:
            axes[0, 1].axvline(thresholds['max_genes'], color='red', linestyle='--',
                             label=f"max={thresholds['max_genes']}")
    axes[0, 1].set_xlabel('Number of genes per cell')
    axes[0, 1].set_ylabel('Number of cells')
    axes[0, 1].set_yscale('log')
    axes[0, 1].set_title('Genes per Cell Distribution')
    axes[0, 1].legend()

    # 3. Mitochondrial percentage
    axes[0, 2].hist(adata.obs['pct_counts_mt'], bins=100, color='salmon', edgecolor='black')
    if thresholds and 'mito_threshold' in thresholds:
        axes[0, 2].axvline(thresholds['mito_threshold'], color='red', linestyle='--',
                         label=f"threshold={thresholds['mito_threshold']}%")
    axes[0, 2].set_xlabel('Mitochondrial %')
    axes[0, 2].set_ylabel('Number of cells')
    axes[0, 2].set_title('Mitochondrial Content')
    axes[0, 2].legend()

    # 4. Scatter: counts vs genes
    axes[1, 0].scatter(adata.obs['total_counts'], adata.obs['n_genes_by_counts'],
                      s=1, alpha=0.5, c='blue')
    axes[1, 0].set_xlabel('Total counts')
    axes[1, 0].set_ylabel('Number of genes')
    axes[1, 0].set_xscale('log')
    axes[1, 0].set_yscale('log')
    axes[1, 0].set_title('Counts vs Genes')

    # 5. Scatter: counts vs mito%
    axes[1, 1].scatter(adata.obs['total_counts'], adata.obs['pct_counts_mt'],
                      s=1, alpha=0.5, c='red')
    axes[1, 1].set_xlabel('Total counts')
    axes[1, 1].set_ylabel('Mitochondrial %')
    axes[1, 1].set_xscale('log')
    axes[1, 1].set_title('Counts vs Mitochondrial %')

    # 6. Violin plots
    data_to_plot = [
        adata.obs['n_genes_by_counts'],
        adata.obs['total_counts'],
        adata.obs['pct_counts_mt']
    ]
    axes[1, 2].violinplot(data_to_plot, positions=[1, 2, 3], showmeans=True)
    axes[1, 2].set_xticks([1, 2, 3])
    axes[1, 2].set_xticklabels(['Genes', 'Counts', 'Mito%'], rotation=45)
    axes[1, 2].set_ylabel('Value')
    axes[1, 2].set_title('QC Metrics Distribution')
    axes[1, 2].set_yscale('log')

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_qc_metrics.pdf', dpi=300)
    plt.close()

    print(f"[INFO] QC plots saved to {output_path}")


def filter_cells_and_genes(adata: ad.AnnData, min_genes: int = 200,
                           max_genes: int = 6000, min_cells: int = 3,
                           mito_threshold: float = 5.0,
                           filter_doublets: bool = True) -> ad.AnnData:
    """
    Filter cells and genes based on QC thresholds

    Args:
        adata: AnnData object
        min_genes: Minimum genes per cell
        max_genes: Maximum genes per cell
        min_cells: Minimum cells per gene
        mito_threshold: Maximum mitochondrial percentage
        filter_doublets: Remove predicted doublets

    Returns:
        Filtered AnnData object
    """
    n_cells_before = adata.n_obs
    n_genes_before = adata.n_vars

    print(f"[INFO] Before filtering: {n_cells_before} cells, {n_genes_before} genes")

    # Filter cells
    print(f"[INFO] Filtering cells with genes < {min_genes} or > {max_genes}")
    sc.pp.filter_cells(adata, min_genes=min_genes)

    # Additional max_genes filter
    adata = adata[adata.obs['n_genes_by_counts'] <= max_genes, :].copy()

    # Filter by mitochondrial content
    print(f"[INFO] Filtering cells with mitochondrial % > {mito_threshold}")
    adata = adata[adata.obs['pct_counts_mt'] <= mito_threshold, :].copy()

    # Filter doublets if flagged
    if filter_doublets and 'predicted_doublet' in adata.obs.columns:
        n_doublets = adata.obs['predicted_doublet'].sum()
        print(f"[INFO] Filtering {n_doublets} predicted doublets")
        adata = adata[~adata.obs['predicted_doublet'], :].copy()

    # Filter genes
    print(f"[INFO] Filtering genes expressed in < {min_cells} cells")
    sc.pp.filter_genes(adata, min_cells=min_cells)

    n_cells_after = adata.n_obs
    n_genes_after = adata.n_vars

    print(f"[INFO] After filtering: {n_cells_after} cells, {n_genes_after} genes")
    print(f"[INFO] Removed: {n_cells_before - n_cells_after} cells ({(n_cells_before - n_cells_after)/n_cells_before*100:.1f}%)")
    print(f"[INFO] Removed: {n_genes_before - n_genes_after} genes ({(n_genes_before - n_genes_after)/n_genes_before*100:.1f}%)")

    return adata


def main():
    parser = argparse.ArgumentParser(description='Filter cells and genes based on QC metrics')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--min_genes', type=int, default=200, help='Minimum genes per cell')
    parser.add_argument('--max_genes', type=int, default=6000, help='Maximum genes per cell')
    parser.add_argument('--min_cells', type=int, default=3, help='Minimum cells per gene')
    parser.add_argument('--mito_threshold', type=float, default=5.0,
                       help='Maximum mitochondrial percentage')
    parser.add_argument('--mito_prefix', default='ATMG',
                       help='Mitochondrial gene prefix (ATMG for Arabidopsis, OSMT for Rice)')
    parser.add_argument('--filter_doublets', action='store_true',
                       help='Remove predicted doublets')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--metrics', required=True, help='Output metrics CSV file')
    parser.add_argument('--plot_dir', default=None, help='Directory for QC plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Calculate QC metrics
        adata = calculate_qc_metrics(adata, mito_prefix=args.mito_prefix)

        # Generate plots before filtering
        if args.plot_dir:
            thresholds = {
                'min_genes': args.min_genes,
                'max_genes': args.max_genes,
                'mito_threshold': args.mito_threshold
            }
            plot_qc_metrics(adata, f"{args.sample_id}_before_filter",
                          args.plot_dir, thresholds)

        # Filter cells and genes
        adata_filtered = filter_cells_and_genes(
            adata,
            min_genes=args.min_genes,
            max_genes=args.max_genes,
            min_cells=args.min_cells,
            mito_threshold=args.mito_threshold,
            filter_doublets=args.filter_doublets
        )

        # Generate plots after filtering
        if args.plot_dir:
            plot_qc_metrics(adata_filtered, f"{args.sample_id}_after_filter",
                          args.plot_dir)

        # Save metrics
        metrics_df = pd.DataFrame({
            'sample_id': [args.sample_id],
            'cells_before': [adata.n_obs],
            'cells_after': [adata_filtered.n_obs],
            'cells_removed': [adata.n_obs - adata_filtered.n_obs],
            'genes_before': [adata.n_vars],
            'genes_after': [adata_filtered.n_vars],
            'genes_removed': [adata.n_vars - adata_filtered.n_vars],
            'median_genes_per_cell': [adata_filtered.obs['n_genes_by_counts'].median()],
            'median_counts_per_cell': [adata_filtered.obs['total_counts'].median()],
            'median_mito_pct': [adata_filtered.obs['pct_counts_mt'].median()]
        })
        metrics_df.to_csv(args.metrics, index=False)
        print(f"[INFO] Metrics saved to {args.metrics}")

        # Save filtered data
        adata_filtered.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Filtered data saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("FILTERING SUMMARY")
        print("="*60)
        print(f"Sample ID: {args.sample_id}")
        print(f"Cells: {adata.n_obs} → {adata_filtered.n_obs} ({adata_filtered.n_obs/adata.n_obs*100:.1f}% retained)")
        print(f"Genes: {adata.n_vars} → {adata_filtered.n_vars} ({adata_filtered.n_vars/adata.n_vars*100:.1f}% retained)")
        print(f"Median genes/cell: {adata_filtered.obs['n_genes_by_counts'].median():.0f}")
        print(f"Median UMIs/cell: {adata_filtered.obs['total_counts'].median():.0f}")
        print(f"Median mito%: {adata_filtered.obs['pct_counts_mt'].median():.2f}%")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
