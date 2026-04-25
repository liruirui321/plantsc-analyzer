#!/usr/bin/env python3
"""
Differential Expression Analysis per Cluster

Finds marker genes for each cluster using statistical tests.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad


def find_markers_per_cluster(adata: ad.AnnData, cluster_key: str = 'cluster',
                             method: str = 'wilcoxon', min_pct: float = 0.1,
                             logfc_threshold: float = 0.25) -> pd.DataFrame:
    """
    Find marker genes for each cluster

    Args:
        adata: AnnData object
        cluster_key: Column name for cluster assignments
        method: Statistical test method
        min_pct: Minimum percentage of cells expressing gene
        logfc_threshold: Minimum log fold-change

    Returns:
        DataFrame with marker genes
    """
    print(f"[INFO] Finding marker genes for {adata.obs[cluster_key].nunique()} clusters")

    # Run differential expression
    sc.tl.rank_genes_groups(
        adata,
        groupby=cluster_key,
        method=method,
        use_raw=False,
        pts=True
    )

    # Extract results
    results = []
    for cluster in adata.obs[cluster_key].unique():
        cluster_results = sc.get.rank_genes_groups_df(adata, group=cluster)
        cluster_results['cluster'] = cluster
        results.append(cluster_results)

    all_results = pd.concat(results, ignore_index=True)

    # Filter by thresholds
    filtered = all_results[
        (all_results['logfoldchanges'] > logfc_threshold) &
        (all_results['pct_nz_group'] > min_pct)
    ].copy()

    print(f"[INFO] Found {len(filtered)} significant markers")

    return filtered


def get_top_markers(deg_results: pd.DataFrame, n_top: int = 10) -> pd.DataFrame:
    """Get top N markers per cluster"""
    top_markers = []

    for cluster in deg_results['cluster'].unique():
        cluster_deg = deg_results[deg_results['cluster'] == cluster]
        cluster_deg = cluster_deg.sort_values('scores', ascending=False).head(n_top)
        top_markers.append(cluster_deg)

    return pd.concat(top_markers, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description='Find marker genes per cluster')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--cluster_key', default='cluster', help='Cluster column name')
    parser.add_argument('--method', default='wilcoxon',
                       choices=['wilcoxon', 't-test', 'logreg'],
                       help='Statistical test method')
    parser.add_argument('--min_pct', type=float, default=0.1,
                       help='Minimum percentage of cells expressing gene')
    parser.add_argument('--logfc_threshold', type=float, default=0.25,
                       help='Minimum log fold-change')
    parser.add_argument('--output', required=True, help='Output DEG results CSV')
    parser.add_argument('--top_markers', required=True, help='Output top markers CSV')
    parser.add_argument('--n_top', type=int, default=10, help='Number of top markers per cluster')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Find markers
        deg_results = find_markers_per_cluster(
            adata,
            cluster_key=args.cluster_key,
            method=args.method,
            min_pct=args.min_pct,
            logfc_threshold=args.logfc_threshold
        )

        # Save all results
        deg_results.to_csv(args.output, index=False)
        print(f"[INFO] DEG results saved to {args.output}")

        # Get top markers
        top_markers = get_top_markers(deg_results, n_top=args.n_top)
        top_markers.to_csv(args.top_markers, index=False)
        print(f"[INFO] Top markers saved to {args.top_markers}")

        # Print summary
        print("\n" + "="*60)
        print("DEG SUMMARY")
        print("="*60)
        for cluster in sorted(deg_results['cluster'].unique()):
            n_markers = (deg_results['cluster'] == cluster).sum()
            print(f"Cluster {cluster}: {n_markers} marker genes")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
