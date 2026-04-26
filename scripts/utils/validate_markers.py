#!/usr/bin/env python3
"""
Validate Marker Gene CSV Files

Checks format, required fields, and data consistency.
"""

import argparse
import sys
import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = ['gene_symbol', 'cell_type', 'confidence']
VALID_CONFIDENCE = ['high', 'medium', 'low']


def validate_marker_file(filepath: str) -> tuple:
    """
    Validate a marker gene CSV file

    Returns:
        tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    path = Path(filepath)
    if not path.exists():
        return False, [f"File not found: {filepath}"], []

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return False, [f"Cannot read CSV: {e}"], []

    # Check required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return False, errors, warnings

    # Check for empty values
    for col in REQUIRED_COLUMNS:
        n_empty = df[col].isna().sum()
        if n_empty > 0:
            errors.append(f"Column '{col}' has {n_empty} empty values")

    # Check confidence values
    if 'confidence' in df.columns:
        invalid_conf = df[~df['confidence'].isin(VALID_CONFIDENCE)]
        if len(invalid_conf) > 0:
            errors.append(f"Invalid confidence values: {invalid_conf['confidence'].unique().tolist()}")

    # Check for duplicates
    if 'gene_symbol' in df.columns and 'cell_type' in df.columns:
        duplicates = df.duplicated(subset=['gene_symbol', 'cell_type'], keep=False)
        if duplicates.any():
            dup_genes = df[duplicates]['gene_symbol'].unique().tolist()
            warnings.append(f"Duplicate gene-celltype pairs: {dup_genes[:5]}")

    # Check gene count
    n_genes = len(df)
    if n_genes < 5:
        warnings.append(f"Only {n_genes} markers - consider adding more")

    # Check cell type diversity
    if 'cell_type' in df.columns:
        n_types = df['cell_type'].nunique()
        if n_types < 2:
            warnings.append(f"Only {n_types} cell type(s) - consider adding more diversity")

    is_valid = len(errors) == 0

    return is_valid, errors, warnings


def validate_all_markers(markers_dir: str) -> dict:
    """Validate all marker files in a directory"""
    results = {}

    for csv_file in Path(markers_dir).rglob('*.csv'):
        is_valid, errors, warnings = validate_marker_file(str(csv_file))
        results[str(csv_file)] = {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'n_markers': len(pd.read_csv(csv_file)) if is_valid else 0
        }

    return results


def main():
    parser = argparse.ArgumentParser(description='Validate marker gene CSV files')
    parser.add_argument('input', help='CSV file or directory to validate')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')

    args = parser.parse_args()

    path = Path(args.input)

    if path.is_file():
        is_valid, errors, warnings = validate_marker_file(args.input)

        print(f"\n{'='*60}")
        print(f"Validating: {args.input}")
        print(f"{'='*60}")

        if is_valid:
            df = pd.read_csv(args.input)
            print(f"✅ VALID - {len(df)} markers, {df['cell_type'].nunique()} cell types")
        else:
            print(f"❌ INVALID")

        if errors:
            print(f"\nErrors ({len(errors)}):")
            for e in errors:
                print(f"  ❌ {e}")

        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠️  {w}")

        if args.strict and warnings:
            sys.exit(1)

        sys.exit(0 if is_valid else 1)

    elif path.is_dir():
        results = validate_all_markers(args.input)

        print(f"\n{'='*60}")
        print(f"Validating directory: {args.input}")
        print(f"{'='*60}\n")

        total_markers = 0
        all_valid = True

        for filepath, result in results.items():
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {filepath}: {result['n_markers']} markers")

            if result['errors']:
                for e in result['errors']:
                    print(f"    ❌ {e}")
                all_valid = False

            if result['warnings']:
                for w in result['warnings']:
                    print(f"    ⚠️  {w}")

            total_markers += result['n_markers']

        print(f"\n{'='*60}")
        print(f"Total: {len(results)} files, {total_markers} markers")
        print(f"Status: {'✅ ALL VALID' if all_valid else '❌ SOME INVALID'}")
        print(f"{'='*60}")

        sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
