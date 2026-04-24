#!/usr/bin/env python3
"""
Platform Detection Script

Automatically detect sequencing platform (BGI or 10X) based on FASTQ file patterns.
"""

import os
import sys
import argparse
from pathlib import Path
import re


def detect_platform(fastq_dir: str) -> dict:
    """
    Detect sequencing platform from FASTQ directory

    Args:
        fastq_dir: Directory containing FASTQ files

    Returns:
        dict with keys: platform, kit_version, files
    """
    fastq_path = Path(fastq_dir)
    files = list(fastq_path.glob('*.fq.gz')) + list(fastq_path.glob('*.fastq.gz'))

    if not files:
        raise ValueError(f"No FASTQ files found in {fastq_dir}")

    filenames = [f.name for f in files]

    # Detection logic
    result = {
        'platform': None,
        'kit_version': None,
        'files': {},
        'confidence': 0.0
    }

    # BGI patterns
    bgi_patterns = {
        'cdna_r1': re.compile(r'.*[_-]1\.f(ast)?q\.gz$'),
        'cdna_r2': re.compile(r'.*[_-]2\.f(ast)?q\.gz$'),
        'oligo_r1': re.compile(r'.*oligo.*[_-]1\.f(ast)?q\.gz$', re.IGNORECASE),
        'oligo_r2': re.compile(r'.*oligo.*[_-]2\.f(ast)?q\.gz$', re.IGNORECASE)
    }

    # 10X patterns
    tenx_patterns = {
        'r1': re.compile(r'.*_S\d+_L\d+_R1_\d+\.fastq\.gz$'),
        'r2': re.compile(r'.*_S\d+_L\d+_R2_\d+\.fastq\.gz$'),
        'i1': re.compile(r'.*_S\d+_L\d+_I1_\d+\.fastq\.gz$')
    }

    # Check for BGI
    bgi_score = 0
    for pattern_name, pattern in bgi_patterns.items():
        matches = [f for f in filenames if pattern.match(f)]
        if matches:
            result['files'][pattern_name] = matches[0]
            bgi_score += 1

    # Check for 10X
    tenx_score = 0
    for pattern_name, pattern in tenx_patterns.items():
        matches = [f for f in filenames if pattern.match(f)]
        if matches:
            result['files'][pattern_name] = matches[0]
            tenx_score += 1

    # Determine platform
    if bgi_score >= 2:  # At least cDNA R1 and R2
        result['platform'] = 'BGI'
        result['confidence'] = bgi_score / 4.0

        # Detect BGI kit version
        if 'oligo_r1' in result['files'] and 'oligo_r2' in result['files']:
            # Check oligo read length to infer version
            # This is a heuristic - may need adjustment
            result['kit_version'] = 'V2.0'  # Default, will be refined
        else:
            result['kit_version'] = 'V3.0'

    elif tenx_score >= 2:  # At least R1 and R2
        result['platform'] = '10X'
        result['confidence'] = tenx_score / 3.0
        result['kit_version'] = 'v3'  # 10X chemistry version

    else:
        raise ValueError(
            f"Cannot determine platform. Found files: {filenames}\n"
            f"BGI score: {bgi_score}, 10X score: {tenx_score}"
        )

    return result


def main():
    parser = argparse.ArgumentParser(description='Detect sequencing platform')
    parser.add_argument('--fastq_dir', required=True, help='Directory containing FASTQ files')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--output', required=True, help='Output file for platform info')

    args = parser.parse_args()

    try:
        result = detect_platform(args.fastq_dir)

        # Write result
        with open(args.output, 'w') as f:
            f.write(f"{result['platform']}\n")

        # Print detailed info to stderr
        print(f"[INFO] Platform Detection Results:", file=sys.stderr)
        print(f"  Sample: {args.sample_id}", file=sys.stderr)
        print(f"  Platform: {result['platform']}", file=sys.stderr)
        print(f"  Kit Version: {result['kit_version']}", file=sys.stderr)
        print(f"  Confidence: {result['confidence']:.2f}", file=sys.stderr)
        print(f"  Files detected:", file=sys.stderr)
        for key, val in result['files'].items():
            print(f"    {key}: {val}", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
