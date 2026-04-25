#!/usr/bin/env python3
"""
Merge Multiple Samples

Merges normalized samples into a single AnnData object.
"""

import argparse
import sys
from pathlib import Path
import scanpy as sc
import anndata as ad


def merge_samples(adata_files: list, batch_key: str = 'sample_id') -> ad.AnnData:
    """
    Merge multiple AnnData objects

    Args:
        adata_files: List of h5ad file paths
        batch_key: Key to use for batch information

    Returns:
        Merged AnnData object
    """
    print(f"[INFO] Merging {len(adata_files)} samples")

    adatas = []
    for f in adata_files:
        print(f"[INFO] Loading {f}")
        adata = sc.read_h5ad(f)
        adatas.append(adata)

    # Merge
    print(f"[INFO] Concatenating samples")
    merged = ad.concat(adatas, join='outer', merge='same', label=batch_key)

    # Recalculate basic metrics
    merged.obs['n_genes'] = (merged.X > 0).sum(axis=1).A1
    merged.obs['n_counts'] = merged.X.sum(axis=1).A1

    print(f"[INFO] Merged: {merged.n_obs} cells, {merged.n_vars} genes")

    return merged


def main():
    parser = argparse.ArgumentParser(description='Merge normalized samples')
    parser.add_argument('--inputs', nargs='+', required=True, help='Input h5ad files')
    parser.add_argument('--output', required=True, help='Output merged h5ad file')
    parser.add_argument('--batch_key', default='sample_id', help='Batch key')

    args = parser.parse_args()

    try:
        merged = merge_samples(args.inputs, args.batch_key)
        merged.write_h5ad(args.output, compression='gzip')
        print(f"[INFO] Merged data saved to {args.output}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
