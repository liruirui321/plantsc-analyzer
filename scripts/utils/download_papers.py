#!/usr/bin/env python3
"""
Literature Downloader

Downloads papers from Sci-Hub based on PMID or DOI.
"""

import argparse
import requests
import time
from pathlib import Path
import re


# Sci-Hub mirrors (update if needed)
SCIHUB_MIRRORS = [
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ru',
]


def download_paper(identifier, output_dir, scihub_url=None):
    """
    Download a paper from Sci-Hub

    Args:
        identifier: PMID or DOI
        output_dir: Output directory
        scihub_url: Sci-Hub mirror URL (optional)

    Returns:
        tuple of (success, filepath, error_message)
    """
    if scihub_url is None:
        scihub_url = SCIHUB_MIRRORS[0]

    # Construct Sci-Hub URL
    if identifier.startswith('10.'):
        # DOI
        url = f"{scihub_url}/{identifier}"
    else:
        # PMID
        url = f"{scihub_url}/{identifier}"

    print(f"[INFO] Downloading from: {url}")

    try:
        # Get the page
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Find PDF link
        pdf_match = re.search(r'(https?://[^"]+\.pdf)', response.text)
        if not pdf_match:
            return False, None, "PDF link not found"

        pdf_url = pdf_match.group(1)
        print(f"[INFO] Found PDF: {pdf_url}")

        # Download PDF
        pdf_response = requests.get(pdf_url, timeout=60)
        pdf_response.raise_for_status()

        # Save PDF
        output_path = Path(output_dir) / f"{identifier.replace('/', '_')}.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(pdf_response.content)

        print(f"[SUCCESS] Saved to: {output_path}")
        return True, str(output_path), None

    except requests.exceptions.RequestException as e:
        return False, None, str(e)


def download_from_list(list_file, output_dir, delay=5):
    """
    Download papers from a list file

    Args:
        list_file: File containing PMIDs or DOIs (one per line)
        output_dir: Output directory
        delay: Delay between downloads (seconds)
    """
    with open(list_file, 'r') as f:
        identifiers = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Found {len(identifiers)} papers to download")
    print(f"[INFO] Output directory: {output_dir}")
    print()

    results = {
        'success': [],
        'failed': []
    }

    for i, identifier in enumerate(identifiers, 1):
        print(f"[{i}/{len(identifiers)}] Processing: {identifier}")

        success, filepath, error = download_paper(identifier, output_dir)

        if success:
            results['success'].append((identifier, filepath))
        else:
            results['failed'].append((identifier, error))
            print(f"[ERROR] {error}")

        # Delay to avoid rate limiting
        if i < len(identifiers):
            print(f"[INFO] Waiting {delay} seconds...")
            time.sleep(delay)

        print()

    # Summary
    print("=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"Total: {len(identifiers)}")
    print(f"Success: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    print()

    if results['failed']:
        print("Failed downloads:")
        for identifier, error in results['failed']:
            print(f"  {identifier}: {error}")


def main():
    parser = argparse.ArgumentParser(
        description='Download papers from Sci-Hub',
        epilog='Note: Use responsibly and respect copyright laws.'
    )
    parser.add_argument('--pmid', help='PMID to download')
    parser.add_argument('--doi', help='DOI to download')
    parser.add_argument('--list', help='File with PMIDs/DOIs (one per line)')
    parser.add_argument('--output', default='./papers', help='Output directory')
    parser.add_argument('--delay', type=int, default=5, help='Delay between downloads (seconds)')
    parser.add_argument('--mirror', help='Sci-Hub mirror URL')

    args = parser.parse_args()

    if args.list:
        download_from_list(args.list, args.output, args.delay)
    elif args.pmid or args.doi:
        identifier = args.pmid or args.doi
        success, filepath, error = download_paper(
            identifier,
            args.output,
            args.mirror
        )
        if not success:
            print(f"[ERROR] {error}")
            exit(1)
    else:
        parser.print_help()
        exit(1)


if __name__ == '__main__':
    main()
