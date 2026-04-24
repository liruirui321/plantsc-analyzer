#!/usr/bin/env python3
"""
Cell Type Annotation using Marker Genes

Annotates cell clusters based on marker gene expression.
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
from scipy.stats import ranksums


def load_marker_database(marker_file: str) -> pd.DataFrame:
    """Load marker gene database"""
    print(f"[INFO] Loading marker database: {marker_file}")
    markers = pd.read_csv(marker_file)

    required_cols = ['gene_symbol', 'cell_type']
    if not all(col in markers.columns for col in required_cols):
        raise ValueError(f"Marker file must contain columns: {required_cols}")

    print(f"[INFO] Loaded {len(markers)} markers for {markers['cell_type'].nunique()} cell types")

    return markers


def calculate_marker_scores(adata: ad.AnnData, markers: pd.DataFrame,
                            cluster_key: str = 'cluster') -> pd.DataFrame:
    """
    Calculate marker gene expression scores for each cluster

    Args:
        adata: AnnData object
        markers: Marker gene dataframe
        cluster_key: Column name for cluster assignments

    Returns:
        DataFrame with scores for each cluster-celltype pair
    """
    print(f"[INFO] Calculating marker scores for {adata.obs[cluster_key].nunique()} clusters")

    # Get unique cell types
    cell_types = markers['cell_type'].unique()
    clusters = adata.obs[cluster_key].unique()

    results = []

    for cluster in clusters:
        cluster_cells = adata.obs[cluster_key] == cluster
        n_cells = cluster_cells.sum()

        for cell_type in cell_types:
            # Get markers for this cell type
            ct_markers = markers[markers['cell_type'] == cell_type]['gene_symbol'].values

            # Find markers present in data
            available_markers = [g for g in ct_markers if g in adata.var_names]

            if len(available_markers) == 0:
                continue

            # Calculate mean expression in cluster
            cluster_expr = adata[cluster_cells, available_markers].X.mean(axis=0)
            if hasattr(cluster_expr, 'A1'):
                cluster_expr = cluster_expr.A1

            # Calculate mean expression in other cells
            other_expr = adata[~cluster_cells, available_markers].X.mean(axis=0)
            if hasattr(other_expr, 'A1'):
                other_expr = other_expr.A1

            # Calculate scores
            mean_score = np.mean(cluster_expr)
            fold_change = np.mean(cluster_expr) / (np.mean(other_expr) + 1e-10)

            # Percentage of cells expressing markers
            pct_in_cluster = (adata[cluster_cells, available_markers].X > 0).mean()
            pct_out_cluster = (adata[~cluster_cells, available_markers].X > 0).mean()

            # Statistical test
            try:
                _, pval = ranksums(
                    adata[cluster_cells, available_markers].X.toarray().flatten(),
                    adata[~cluster_cells, available_markers].X.toarray().flatten()
                )
            except:
                pval = 1.0

            results.append({
                'cluster': cluster,
                'cell_type': cell_type,
                'n_markers_total': len(ct_markers),
                'n_markers_available': len(available_markers),
                'mean_expression': mean_score,
                'fold_change': fold_change,
                'pct_in_cluster': pct_in_cluster,
                'pct_out_cluster': pct_out_cluster,
                'pvalue': pval,
                'markers_used': ','.join(available_markers)
            })

    results_df = pd.DataFrame(results)

    # Calculate composite score
    results_df['score'] = (
        results_df['mean_expression'] *
        np.log2(results_df['fold_change'] + 1) *
        results_df['pct_in_cluster']
    )

    return results_df


def assign_cell_types(scores_df: pd.DataFrame, confidence_threshold: float = 0.7) -> pd.DataFrame:
    """
    Assign cell types to clusters based on marker scores

    Args:
        scores_df: DataFrame with marker scores
        confidence_threshold: Minimum confidence for assignment

    Returns:
        DataFrame with cluster annotations
    """
    print(f"[INFO] Assigning cell types (confidence threshold: {confidence_threshold})")

    annotations = []

    for cluster in scores_df['cluster'].unique():
        cluster_scores = scores_df[scores_df['cluster'] == cluster].copy()
        cluster_scores = cluster_scores.sort_values('score', ascending=False)

        if len(cluster_scores) == 0:
            annotations.append({
                'cluster': cluster,
                'cell_type': 'Unknown',
                'confidence': 0.0,
                'top_markers': ''
            })
            continue

        # Get top cell type
        top_row = cluster_scores.iloc[0]
        second_score = cluster_scores.iloc[1]['score'] if len(cluster_scores) > 1 else 0

        # Calculate confidence (ratio of top score to second score)
        if second_score > 0:
            confidence = 1 - (second_score / top_row['score'])
        else:
            confidence = 1.0

        # Assign cell type
        if confidence >= confidence_threshold and top_row['score'] > 0:
            cell_type = top_row['cell_type']
        else:
            cell_type = 'Unknown'

        annotations.append({
            'cluster': cluster,
            'cell_type': cell_type,
            'confidence': confidence,
            'score': top_row['score'],
            'fold_change': top_row['fold_change'],
            'pct_in_cluster': top_row['pct_in_cluster'],
            'top_markers': top_row['markers_used']
        })

    annotations_df = pd.DataFrame(annotations)
    annotations_df = annotations_df.sort_values('cluster')

    return annotations_df


def plot_annotation_results(adata: ad.AnnData, annotations: pd.DataFrame,
                            markers: pd.DataFrame, sample_id: str,
                            cluster_key: str, output_dir: str):
    """Generate annotation result plots"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Add cell type to adata
    cluster_to_celltype = dict(zip(annotations['cluster'], annotations['cell_type']))
    adata.obs['cell_type'] = adata.obs[cluster_key].map(cluster_to_celltype)

    # 1. UMAP with cell types
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sc.pl.umap(adata, color=cluster_key, ax=axes[0], show=False,
              title=f'{sample_id} - Clusters', legend_loc='on data')
    sc.pl.umap(adata, color='cell_type', ax=axes[1], show=False,
              title=f'{sample_id} - Cell Types', legend_loc='right margin')

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_annotation_umap.pdf', dpi=300)
    plt.close()

    # 2. Marker gene heatmap
    cell_types = annotations['cell_type'].unique()
    cell_types = [ct for ct in cell_types if ct != 'Unknown']

    if len(cell_types) > 0:
        # Get top markers for each cell type
        top_markers = []
        for ct in cell_types:
            ct_markers = markers[markers['cell_type'] == ct]['gene_symbol'].values
            available = [g for g in ct_markers if g in adata.var_names]
            top_markers.extend(available[:5])  # Top 5 per cell type

        top_markers = list(set(top_markers))

        if len(top_markers) > 0:
            sc.pl.heatmap(
                adata,
                var_names=top_markers,
                groupby='cell_type',
                cmap='viridis',
                dendrogram=False,
                show=False,
                save=f'_{sample_id}_marker_heatmap.pdf'
            )

    # 3. Annotation confidence plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(annotations)), annotations['confidence'],
                  color=['green' if c >= 0.7 else 'orange' for c in annotations['confidence']],
                  alpha=0.7)
    ax.axhline(y=0.7, color='red', linestyle='--', label='Threshold (0.7)')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Confidence')
    ax.set_title(f'{sample_id} - Annotation Confidence')
    ax.set_xticks(range(len(annotations)))
    ax.set_xticklabels(annotations['cluster'])
    ax.legend()

    # Add cell type labels
    for i, (cluster, ct, conf) in enumerate(zip(annotations['cluster'],
                                                 annotations['cell_type'],
                                                 annotations['confidence'])):
        ax.text(i, conf + 0.02, ct, ha='center', va='bottom',
               fontsize=8, rotation=45)

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_annotation_confidence.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Annotation plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Annotate cell types using marker genes')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--markers', required=True, help='Marker gene database CSV')
    parser.add_argument('--cluster_key', default='cluster', help='Cluster column name')
    parser.add_argument('--confidence_threshold', type=float, default=0.7,
                       help='Minimum confidence for cell type assignment')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--annotation_csv', required=True, help='Output annotation CSV')
    parser.add_argument('--plot_dir', default=None, help='Directory for plots')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")
        print(f"[INFO] Clusters: {adata.obs[args.cluster_key].nunique()}")

        # Load markers
        markers = load_marker_database(args.markers)

        # Calculate scores
        scores_df = calculate_marker_scores(adata, markers, args.cluster_key)

        # Assign cell types
        annotations = assign_cell_types(scores_df, args.confidence_threshold)

        # Save annotations
        annotations.to_csv(args.annotation_csv, index=False)
        print(f"[INFO] Annotations saved to {args.annotation_csv}")

        # Add to adata
        cluster_to_celltype = dict(zip(annotations['cluster'], annotations['cell_type']))
        adata.obs['cell_type'] = adata.obs[args.cluster_key].map(cluster_to_celltype)
        adata.obs['cell_type_confidence'] = adata.obs[args.cluster_key].map(
            dict(zip(annotations['cluster'], annotations['confidence']))
        )

        # Generate plots
        if args.plot_dir:
            plot_annotation_results(
                adata, annotations, markers, args.sample_id,
                args.cluster_key, args.plot_dir
            )

        # Save output
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Annotated data saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("ANNOTATION SUMMARY")
        print("="*60)
        print(f"Sample ID: {args.sample_id}")
        print(f"Total clusters: {len(annotations)}")
        print(f"Annotated: {(annotations['cell_type'] != 'Unknown').sum()}")
        print(f"Unknown: {(annotations['cell_type'] == 'Unknown').sum()}")
        print("\nCell Type Distribution:")
        for _, row in annotations.iterrows():
            n_cells = (adata.obs[args.cluster_key] == row['cluster']).sum()
            print(f"  Cluster {row['cluster']}: {row['cell_type']} "
                  f"(confidence={row['confidence']:.2f}, n={n_cells})")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
