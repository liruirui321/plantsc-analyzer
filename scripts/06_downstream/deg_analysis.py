#!/usr/bin/env python3
"""
Differential Expression Analysis

Performs differential expression analysis between cell types or conditions.
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


def run_deg_analysis(adata: ad.AnnData, group_key: str = 'cell_type',
                     method: str = 'wilcoxon', min_pct: float = 0.1,
                     logfc_threshold: float = 0.25) -> dict:
    """
    Run differential expression analysis for all groups

    Args:
        adata: AnnData object
        group_key: Column name for grouping
        method: Statistical test method
        min_pct: Minimum percentage of cells expressing gene
        logfc_threshold: Minimum log fold-change

    Returns:
        Dictionary of DEG results per group
    """
    print(f"[INFO] Running DEG analysis for {adata.obs[group_key].nunique()} groups")

    # Run rank genes groups
    sc.tl.rank_genes_groups(
        adata,
        groupby=group_key,
        method=method,
        use_raw=False,
        pts=True
    )

    # Extract results for each group
    results = {}
    for group in adata.obs[group_key].unique():
        if group == 'Unknown':
            continue

        deg_df = sc.get.rank_genes_groups_df(adata, group=group)

        # Filter by thresholds
        deg_df = deg_df[
            (deg_df['logfoldchanges'] > logfc_threshold) &
            (deg_df['pct_nz_group'] > min_pct)
        ].copy()

        deg_df['group'] = group
        results[group] = deg_df

        print(f"[INFO] {group}: {len(deg_df)} DEGs")

    return results


def plot_volcano(deg_df: pd.DataFrame, group: str, output_path: Path):
    """Generate volcano plot"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Calculate -log10(pval)
    deg_df['neg_log10_pval'] = -np.log10(deg_df['pvals_adj'] + 1e-300)

    # Color by significance
    colors = []
    for _, row in deg_df.iterrows():
        if row['pvals_adj'] < 0.05 and abs(row['logfoldchanges']) > 0.5:
            colors.append('red')
        elif row['pvals_adj'] < 0.05:
            colors.append('orange')
        else:
            colors.append('gray')

    ax.scatter(deg_df['logfoldchanges'], deg_df['neg_log10_pval'],
              c=colors, s=10, alpha=0.6)

    # Add threshold lines
    ax.axhline(y=-np.log10(0.05), color='blue', linestyle='--', alpha=0.5)
    ax.axvline(x=0.5, color='blue', linestyle='--', alpha=0.5)
    ax.axvline(x=-0.5, color='blue', linestyle='--', alpha=0.5)

    # Label top genes
    top_genes = deg_df.nlargest(10, 'scores')
    for _, row in top_genes.iterrows():
        ax.text(row['logfoldchanges'], row['neg_log10_pval'],
               row['names'], fontsize=8, alpha=0.7)

    ax.set_xlabel('Log2 Fold Change')
    ax.set_ylabel('-Log10(Adjusted P-value)')
    ax.set_title(f'Volcano Plot: {group}')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Differential expression analysis')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--group_key', default='cell_type', help='Grouping column')
    parser.add_argument('--method', default='wilcoxon',
                       choices=['wilcoxon', 't-test', 'logreg'],
                       help='Statistical test method')
    parser.add_argument('--min_pct', type=float, default=0.1,
                       help='Minimum percentage of cells expressing gene')
    parser.add_argument('--logfc_threshold', type=float, default=0.25,
                       help='Minimum log fold-change')
    parser.add_argument('--output_dir', required=True, help='Output directory')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Check group key
        if args.group_key not in adata.obs.columns:
            raise ValueError(f"Group key '{args.group_key}' not found")

        # Run DEG analysis
        deg_results = run_deg_analysis(
            adata,
            group_key=args.group_key,
            method=args.method,
            min_pct=args.min_pct,
            logfc_threshold=args.logfc_threshold
        )

        # Save results and generate plots
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for group, deg_df in deg_results.items():
            # Save CSV
            csv_path = output_path / f"deg_{group}.csv"
            deg_df.to_csv(csv_path, index=False)
            print(f"[INFO] Saved {csv_path}")

            # Generate volcano plot
            plot_path = output_path / f"deg_volcano_{group}.pdf"
            plot_volcano(deg_df, group, plot_path)
            print(f"[INFO] Saved {plot_path}")

        print(f"[INFO] DEG analysis complete")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
