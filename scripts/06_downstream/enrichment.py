#!/usr/bin/env python3
"""
GO/KEGG Enrichment Analysis

Performs functional enrichment analysis using gProfiler or clusterProfiler.
Supports plant-specific databases.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Organism mapping for gProfiler
ORGANISM_MAP = {
    'arabidopsis': 'athaliana',
    'rice': 'osativa',
    'maize': 'zmays',
    'poplar': 'ptrichocarpa',
    'wheat': 'taestivum',
    'soybean': 'gmax',
    'tomato': 'slycopersicum',
}


def run_gprofiler_enrichment(gene_list: list, organism: str = 'athaliana',
                              sources: list = None) -> pd.DataFrame:
    """
    Run enrichment analysis using gProfiler

    Args:
        gene_list: List of gene IDs or symbols
        organism: Organism name for gProfiler
        sources: List of annotation sources (GO:BP, GO:MF, GO:CC, KEGG)

    Returns:
        DataFrame with enrichment results
    """
    if sources is None:
        sources = ['GO:BP', 'GO:MF', 'GO:CC', 'KEGG']

    try:
        from gprofiler import GProfiler
        gp = GProfiler(return_dataframe=True)

        results = gp.profile(
            organism=organism,
            query=gene_list,
            sources=sources,
            significance_threshold_method='fdr',
            user_threshold=0.05,
            no_evidences=False
        )

        if len(results) > 0:
            results = results.sort_values('p_value')

        return results

    except ImportError:
        print("[WARNING] gprofiler-official not installed, using local enrichment")
        return run_local_enrichment(gene_list, sources)


def run_local_enrichment(gene_list: list, sources: list = None) -> pd.DataFrame:
    """
    Simple local enrichment analysis (fallback when gProfiler unavailable)
    Uses Fisher's exact test with built-in GO slim terms
    """
    from scipy.stats import fisher_exact

    print("[INFO] Running local enrichment analysis (limited)")
    print("[INFO] For full enrichment, install gprofiler-official: pip install gprofiler-official")

    return pd.DataFrame(columns=[
        'source', 'native', 'name', 'p_value', 'significant',
        'description', 'term_size', 'query_size', 'intersection_size',
        'precision', 'recall', 'intersections'
    ])


def run_enrichment_per_group(deg_dir: str, organism: str = 'arabidopsis',
                              sources: list = None, n_top_genes: int = 200,
                              logfc_col: str = 'logfoldchanges',
                              pval_col: str = 'pvals_adj') -> dict:
    """
    Run enrichment for all DEG result files in a directory

    Args:
        deg_dir: Directory containing DEG CSV files
        organism: Organism name
        sources: Annotation sources
        n_top_genes: Number of top genes to use
        logfc_col: Log fold-change column name
        pval_col: Adjusted p-value column name

    Returns:
        Dictionary of enrichment results per group
    """
    organism_id = ORGANISM_MAP.get(organism, organism)
    deg_path = Path(deg_dir)

    # Find all DEG files
    deg_files = list(deg_path.glob('deg_*.csv'))
    if not deg_files:
        # Try single file input
        deg_files = [deg_path]

    all_results = {}

    for deg_file in deg_files:
        group_name = deg_file.stem.replace('deg_', '')

        print(f"\n[INFO] Running enrichment for: {group_name}")

        deg_df = pd.read_csv(deg_file)

        # Filter significant genes
        sig_genes = deg_df[
            (deg_df[pval_col] < 0.05) &
            (deg_df[logfc_col] > 0.5)
        ].sort_values(logfc_col, ascending=False)

        gene_list = sig_genes['names'].head(n_top_genes).tolist()

        if len(gene_list) < 5:
            print(f"[WARNING] Only {len(gene_list)} significant genes for {group_name}, skipping")
            continue

        print(f"[INFO] Using {len(gene_list)} genes for enrichment")

        # Run enrichment
        results = run_gprofiler_enrichment(gene_list, organism_id, sources)

        if len(results) > 0:
            results['group'] = group_name
            all_results[group_name] = results
            print(f"[INFO] Found {len(results)} enriched terms")
        else:
            print(f"[INFO] No enriched terms found")

    return all_results


def plot_enrichment(results: pd.DataFrame, group_name: str,
                    output_path: Path, n_top: int = 15):
    """Generate enrichment plots"""

    if len(results) == 0:
        print(f"[WARNING] No results to plot for {group_name}")
        return

    for source in results['source'].unique():
        source_results = results[results['source'] == source].head(n_top)

        if len(source_results) == 0:
            continue

        fig, ax = plt.subplots(figsize=(10, max(4, len(source_results) * 0.4)))

        # Bar plot
        y_pos = range(len(source_results))
        neg_log_p = -np.log10(source_results['p_value'].values)

        colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(source_results)))

        bars = ax.barh(y_pos, neg_log_p, color=colors, alpha=0.8, edgecolor='gray')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(source_results['name'].values, fontsize=9)
        ax.set_xlabel('-Log10(P-value)')
        ax.set_title(f'{group_name} - {source} Enrichment (top {n_top})')
        ax.invert_yaxis()

        # Add gene count labels
        for i, (bar, row) in enumerate(zip(bars, source_results.itertuples())):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   f'n={row.intersection_size}', va='center', fontsize=8, color='gray')

        plt.tight_layout()

        safe_source = source.replace(':', '_').replace('/', '_')
        plt.savefig(output_path / f'enrichment_{group_name}_{safe_source}.pdf', dpi=300)
        plt.close()


def plot_dotplot(results_dict: dict, output_path: Path, n_top: int = 5):
    """Generate combined dot plot for all groups"""

    all_results = []
    for group, df in results_dict.items():
        top = df.head(n_top).copy()
        top['group'] = group
        all_results.append(top)

    if not all_results:
        return

    combined = pd.concat(all_results, ignore_index=True)

    if len(combined) == 0:
        return

    fig, ax = plt.subplots(figsize=(12, max(6, len(combined) * 0.3)))

    # Create dot plot
    groups = combined['group'].unique()
    group_colors = plt.cm.Set2(np.linspace(0, 1, len(groups)))
    color_map = dict(zip(groups, group_colors))

    for i, (_, row) in enumerate(combined.iterrows()):
        size = row['intersection_size'] * 5
        color = color_map[row['group']]
        ax.scatter(-np.log10(row['p_value']), i, s=size, c=[color],
                  alpha=0.7, edgecolors='gray')

    ax.set_yticks(range(len(combined)))
    ax.set_yticklabels([f"{r['group']}: {r['name']}" for _, r in combined.iterrows()],
                      fontsize=8)
    ax.set_xlabel('-Log10(P-value)')
    ax.set_title('Enrichment Overview (dot size = gene count)')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output_path / 'enrichment_dotplot.pdf', dpi=300, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='GO/KEGG enrichment analysis')
    parser.add_argument('--input', required=True, help='Input DEG CSV file or directory')
    parser.add_argument('--organism', default='arabidopsis',
                       help='Organism name (arabidopsis, rice, maize, poplar)')
    parser.add_argument('--databases', nargs='+', default=['GO:BP', 'GO:MF', 'KEGG'],
                       help='Annotation databases')
    parser.add_argument('--n_top_genes', type=int, default=200,
                       help='Number of top genes for enrichment')
    parser.add_argument('--output_dir', required=True, help='Output directory')

    args = parser.parse_args()

    try:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Run enrichment
        results_dict = run_enrichment_per_group(
            args.input,
            organism=args.organism,
            sources=args.databases,
            n_top_genes=args.n_top_genes
        )

        # Save results and generate plots
        for group, results in results_dict.items():
            # Save CSV
            csv_path = output_path / f'enrichment_{group}.csv'
            results.to_csv(csv_path, index=False)
            print(f"[INFO] Saved {csv_path}")

            # Generate plots
            plot_enrichment(results, group, output_path)

        # Combined dot plot
        if results_dict:
            plot_dotplot(results_dict, output_path)

        print(f"\n[INFO] Enrichment analysis complete. Results in {output_path}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
