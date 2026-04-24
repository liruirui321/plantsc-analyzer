#!/usr/bin/env python3
"""
Convert 10X or BGI matrix to AnnData h5ad format

Supports:
- 10X CellRanger output (filtered_feature_bc_matrix/)
- BGI dnbc4tools output (filter_matrix/)
"""

import argparse
import sys
from pathlib import Path
import scanpy as sc
import anndata as ad
import pandas as pd


def load_10x_matrix(matrix_dir: str) -> ad.AnnData:
    """Load 10X CellRanger matrix"""
    print(f"[INFO] Loading 10X matrix from {matrix_dir}")
    adata = sc.read_10x_mtx(matrix_dir, var_names='gene_symbols', cache=True)
    return adata


def load_bgi_matrix(matrix_dir: str) -> ad.AnnData:
    """Load BGI dnbc4tools matrix"""
    print(f"[INFO] Loading BGI matrix from {matrix_dir}")

    matrix_path = Path(matrix_dir)

    # BGI output structure: matrix.mtx.gz, barcodes.tsv.gz, features.tsv.gz
    mtx_file = matrix_path / 'matrix.mtx.gz'
    barcodes_file = matrix_path / 'barcodes.tsv.gz'
    features_file = matrix_path / 'features.tsv.gz'

    # Check if files exist
    if not mtx_file.exists():
        mtx_file = matrix_path / 'matrix.mtx'
    if not barcodes_file.exists():
        barcodes_file = matrix_path / 'barcodes.tsv'
    if not features_file.exists():
        features_file = matrix_path / 'features.tsv'

    # Load using scanpy
    adata = sc.read_10x_mtx(
        matrix_dir,
        var_names='gene_symbols',
        cache=True,
        gex_only=True
    )

    return adata


def add_metadata(adata: ad.AnnData, sample_id: str, batch: str, condition: str) -> ad.AnnData:
    """Add sample metadata to AnnData object"""
    adata.obs['sample_id'] = sample_id
    adata.obs['batch'] = batch
    adata.obs['condition'] = condition

    # Add basic QC metrics
    adata.obs['n_genes'] = (adata.X > 0).sum(axis=1).A1
    adata.obs['n_counts'] = adata.X.sum(axis=1).A1

    # Calculate mitochondrial percentage (if applicable)
    # Common plant mitochondrial prefixes: ATMG (Arabidopsis), OSMT (Rice)
    mito_genes = adata.var_names.str.startswith('ATMG') | \
                 adata.var_names.str.startswith('OSMT') | \
                 adata.var_names.str.startswith('MT-') | \
                 adata.var_names.str.startswith('mt-')

    if mito_genes.sum() > 0:
        adata.obs['pct_mito'] = (
            adata[:, mito_genes].X.sum(axis=1).A1 / adata.obs['n_counts'] * 100
        )
    else:
        adata.obs['pct_mito'] = 0.0

    return adata


def main():
    parser = argparse.ArgumentParser(description='Convert matrix to h5ad format')
    parser.add_argument('--matrix_dir', required=True, help='Path to matrix directory')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--batch', required=True, help='Batch ID')
    parser.add_argument('--condition', required=True, help='Condition/treatment')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--platform', default='auto', choices=['auto', '10x', 'bgi'],
                       help='Platform type (auto-detect if not specified)')

    args = parser.parse_args()

    try:
        # Auto-detect platform if needed
        if args.platform == 'auto':
            matrix_path = Path(args.matrix_dir)
            if (matrix_path / 'filtered_feature_bc_matrix').exists():
                platform = '10x'
            elif (matrix_path / 'matrix.mtx.gz').exists() or (matrix_path / 'matrix.mtx').exists():
                platform = 'bgi'
            else:
                raise ValueError(f"Cannot auto-detect platform from {args.matrix_dir}")
        else:
            platform = args.platform

        # Load matrix
        if platform == '10x':
            adata = load_10x_matrix(args.matrix_dir)
        else:  # bgi
            adata = load_bgi_matrix(args.matrix_dir)

        # Add metadata
        adata = add_metadata(adata, args.sample_id, args.batch, args.condition)

        # Save to h5ad
        print(f"[INFO] Saving to {args.output}")
        adata.write_h5ad(args.output, compression='gzip')

        # Print summary
        print(f"[INFO] Conversion complete:")
        print(f"  Cells: {adata.n_obs:,}")
        print(f"  Genes: {adata.n_vars:,}")
        print(f"  Median genes/cell: {adata.obs['n_genes'].median():.0f}")
        print(f"  Median UMIs/cell: {adata.obs['n_counts'].median():.0f}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
