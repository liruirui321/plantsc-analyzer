#!/usr/bin/env python3
"""
Scrublet Doublet Detection

Detects doublets (two cells captured in one droplet) using Scrublet algorithm.

Reference: Wolock et al. (2019) Cell Systems
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import scrublet as scr
import matplotlib.pyplot as plt
import seaborn as sns


def run_scrublet(adata: ad.AnnData, expected_doublet_rate: float = 0.06,
                 threshold: float = None, min_counts: int = 2,
                 min_cells: int = 3, min_gene_variability_pctl: float = 85) -> tuple:
    """
    Run Scrublet doublet detection

    Args:
        adata: AnnData object
        expected_doublet_rate: Expected doublet rate (default 6%)
        threshold: Doublet score threshold (None = auto)
        min_counts: Minimum counts per gene
        min_cells: Minimum cells per gene
        min_gene_variability_pctl: Percentile for highly variable genes

    Returns:
        tuple of (doublet_scores, predicted_doublets, threshold)
    """
    print(f"[INFO] Running Scrublet on {adata.n_obs} cells")

    # Initialize Scrublet
    scrub = scr.Scrublet(
        adata.X,
        expected_doublet_rate=expected_doublet_rate
    )

    # Run doublet detection
    doublet_scores, predicted_doublets = scrub.scrub_doublets(
        min_counts=min_counts,
        min_cells=min_cells,
        min_gene_variability_pctl=min_gene_variability_pctl,
        n_prin_comps=30
    )

    # Get threshold
    if threshold is None:
        threshold = scrub.threshold_
        print(f"[INFO] Auto-detected threshold: {threshold:.3f}")
    else:
        predicted_doublets = doublet_scores > threshold
        print(f"[INFO] Using manual threshold: {threshold:.3f}")

    # Statistics
    n_doublets = predicted_doublets.sum()
    doublet_rate = n_doublets / len(predicted_doublets) * 100

    print(f"[INFO] Detected doublets: {n_doublets} ({doublet_rate:.2f}%)")
    print(f"[INFO] Doublet score range: [{doublet_scores.min():.3f}, {doublet_scores.max():.3f}]")

    return doublet_scores, predicted_doublets, threshold, scrub


def plot_scrublet_results(scrub, doublet_scores: np.ndarray,
                          predicted_doublets: np.ndarray,
                          sample_id: str, output_dir: str):
    """
    Generate Scrublet diagnostic plots

    Args:
        scrub: Scrublet object
        doublet_scores: Array of doublet scores
        predicted_doublets: Boolean array of predictions
        sample_id: Sample identifier
        output_dir: Output directory for plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Plot 1: Doublet score histogram
    fig, ax = plt.subplots(figsize=(8, 5))
    scrub.plot_histogram()
    plt.title(f'{sample_id} - Doublet Score Distribution')
    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_scrublet_histogram.pdf', dpi=300)
    plt.close()

    # Plot 2: UMAP with doublet scores
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        scrub.set_embedding('UMAP', scr.get_umap(scrub.manifold_obs_, 10, min_dist=0.3))
        scrub.plot_embedding('UMAP', order_points=True)
        plt.title(f'{sample_id} - UMAP colored by Doublet Score')
        plt.tight_layout()
        plt.savefig(output_path / f'{sample_id}_scrublet_umap.pdf', dpi=300)
        plt.close()
    except Exception as e:
        print(f"[WARNING] Could not generate UMAP plot: {e}")

    # Plot 3: Summary statistics
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Score distribution by prediction
    axes[0].hist(doublet_scores[~predicted_doublets], bins=50, alpha=0.7,
                label='Singlets', color='blue')
    axes[0].hist(doublet_scores[predicted_doublets], bins=50, alpha=0.7,
                label='Doublets', color='red')
    axes[0].axvline(scrub.threshold_, color='black', linestyle='--',
                   label=f'Threshold ({scrub.threshold_:.3f})')
    axes[0].set_xlabel('Doublet Score')
    axes[0].set_ylabel('Number of Cells')
    axes[0].set_title('Doublet Score Distribution')
    axes[0].legend()

    # Summary bar plot
    counts = [
        (~predicted_doublets).sum(),
        predicted_doublets.sum()
    ]
    axes[1].bar(['Singlets', 'Doublets'], counts, color=['blue', 'red'], alpha=0.7)
    axes[1].set_ylabel('Number of Cells')
    axes[1].set_title('Cell Classification')
    for i, v in enumerate(counts):
        axes[1].text(i, v + max(counts)*0.02, str(v), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path / f'{sample_id}_scrublet_summary.pdf', dpi=300)
    plt.close()

    print(f"[INFO] Plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Scrublet doublet detection')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--expected_doublet_rate', type=float, default=0.06,
                       help='Expected doublet rate (default: 0.06)')
    parser.add_argument('--threshold', type=float, default=None,
                       help='Doublet score threshold (None = auto)')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--scores', required=True, help='Output scores CSV file')
    parser.add_argument('--plot_dir', default=None, help='Directory for plots')
    parser.add_argument('--remove_doublets', action='store_true',
                       help='Remove doublets from output (default: keep but flag)')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading data: {args.input}")
        adata = sc.read_h5ad(args.input)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Run Scrublet
        doublet_scores, predicted_doublets, threshold, scrub = run_scrublet(
            adata,
            expected_doublet_rate=args.expected_doublet_rate,
            threshold=args.threshold
        )

        # Add results to AnnData
        adata.obs['doublet_score'] = doublet_scores
        adata.obs['predicted_doublet'] = predicted_doublets

        # Save scores to CSV
        scores_df = pd.DataFrame({
            'barcode': adata.obs_names,
            'doublet_score': doublet_scores,
            'predicted_doublet': predicted_doublets
        })
        scores_df.to_csv(args.scores, index=False)
        print(f"[INFO] Scores saved to {args.scores}")

        # Generate plots
        if args.plot_dir:
            plot_scrublet_results(
                scrub, doublet_scores, predicted_doublets,
                args.sample_id, args.plot_dir
            )

        # Filter doublets if requested
        if args.remove_doublets:
            n_before = adata.n_obs
            adata = adata[~predicted_doublets, :].copy()
            n_after = adata.n_obs
            print(f"[INFO] Removed {n_before - n_after} doublets")
            print(f"[INFO] Remaining: {n_after} cells")
        else:
            print(f"[INFO] Keeping all cells (doublets flagged in obs)")

        # Save output
        adata.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Output saved to {args.output}")

        # Print summary
        print("\n" + "="*60)
        print("SCRUBLET SUMMARY")
        print("="*60)
        print(f"Sample ID: {args.sample_id}")
        print(f"Total cells: {len(doublet_scores)}")
        print(f"Detected doublets: {predicted_doublets.sum()} ({predicted_doublets.sum()/len(predicted_doublets)*100:.2f}%)")
        print(f"Threshold: {threshold:.3f}")
        print(f"Score range: [{doublet_scores.min():.3f}, {doublet_scores.max():.3f}]")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
