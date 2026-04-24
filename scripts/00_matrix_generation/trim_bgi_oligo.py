#!/usr/bin/env python3
"""
BGI Oligo FASTQ Trimming Script

For BGI V2.0/V2.5 kit compatibility with V3.1.5 pipeline.

V2.0/V2.5 oligo sequencing: 32+42+10
V3.0+ oligo sequencing: 47+100+10

This script trims V2.0/V2.5 oligo data to match V3.0+ format.
"""

import gzip
import os
import sys
import multiprocessing as mp
from pathlib import Path


def stream(in_path):
    """Stream FASTQ records from gzipped file"""
    with gzip.open(in_path, 'rt') as f:
        while True:
            h = f.readline().rstrip('\n\r')
            if not h:
                break
            s = f.readline().rstrip('\n\r')
            p = f.readline().rstrip('\n\r')
            q = f.readline().rstrip('\n\r')
            if not q:
                break
            yield h, s, p, q


def _trim(args):
    """
    Trim FASTQ sequences based on specified regions

    Args:
        args: tuple of (in_path, out_path, seqlen, regions)
            - in_path: input FASTQ.gz path
            - out_path: output FASTQ.gz path
            - seqlen: minimum sequence length required
            - regions: list of (start, end) tuples to extract

    Returns:
        tuple of (total_reads, skipped_reads)
    """
    in_path, out_path, seqlen, regions = args
    tot = skip = 0

    with gzip.open(out_path, 'wt') as out:
        for h, s, p, q in stream(in_path):
            tot += 1
            if len(s) < seqlen:
                skip += 1
                continue

            # Extract specified regions
            new_s = ''.join(s[start:end] for start, end in regions)
            new_q = ''.join(q[start:end] for start, end in regions)

            out.write(f'{h}\n{new_s}\n{p}\n{new_q}\n')

    return tot, skip


def main(r1_in, r2_in, out_dir):
    """
    Main trimming function

    Args:
        r1_in: oligo R1 input path
        r2_in: oligo R2 input path
        out_dir: output directory
    """
    # Create output directory
    os.makedirs(out_dir, exist_ok=True)

    # Generate output filenames
    r1_basename = Path(r1_in).name.replace('.fq.gz', '_trim.fastq.gz').replace('.fastq.gz', '_trim.fastq.gz')
    r2_basename = Path(r2_in).name.replace('.fq.gz', '_trim.fastq.gz').replace('.fastq.gz', '_trim.fastq.gz')

    r1_out = os.path.join(out_dir, r1_basename)
    r2_out = os.path.join(out_dir, r2_basename)

    # Trimming parameters
    # R1: keep first 20bp
    r1_job = (r1_in, r1_out, 20, [(0, 20)])

    # R2: extract 3 regions (0-10, 16-26, 32-42) from 32+42+10 format
    # This converts V2.0 format to V3.0 compatible format
    r2_job = (r2_in, r2_out, 42, [(0, 10), (16, 26), (32, 42)])

    # Run trimming in parallel
    with mp.Pool(2) as pool:
        (tot1, skip1), (tot2, skip2) = pool.map(_trim, [r1_job, r2_job])

    # Report statistics
    print(f'[INFO] Oligo Trimming Results:')
    print(f'  R1: total={tot1:,} skip={skip1:,} kept={tot1-skip1:,}')
    print(f'  R2: total={tot2:,} skip={skip2:,} kept={tot2-skip2:,}')
    print(f'  Final paired reads: {min(tot1-skip1, tot2-skip2):,}')
    print(f'[INFO] Output files:')
    print(f'  {r1_out}')
    print(f'  {r2_out}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: trim_bgi_oligo.py <oligo_R1.fq.gz> <oligo_R2.fq.gz> <output_dir>')
        print('')
        print('Example:')
        print('  python trim_bgi_oligo.py \\')
        print('    sample1_oligo_1.fq.gz \\')
        print('    sample1_oligo_2.fq.gz \\')
        print('    ./trimmed/')
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
