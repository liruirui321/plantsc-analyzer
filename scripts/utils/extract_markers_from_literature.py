#!/usr/bin/env python3
"""
Extract Marker Genes from Published Literature

Downloads supplementary tables from published papers and extracts
marker genes for each cell type.

Sources:
1. Denyer et al. 2019 (PMID: 31178400) - Arabidopsis Root
2. Kim et al. 2021 (PMID: 33619379) - Arabidopsis Leaf
3. Xu et al. 2021 (PMID: 33793920) - Arabidopsis Flower
4. Shahan et al. 2022 (PMID: 35063072) - Arabidopsis Root Spatiotemporal
"""

import pandas as pd
import requests
from pathlib import Path
import argparse


# Known supplementary data URLs
SUPPLEMENTARY_DATA = {
    'denyer_2019_root': {
        'pmid': '31178400',
        'url': 'https://www.cell.com/cms/10.1016/j.devcel.2019.04.021/attachment/...',
        'table': 'Table_S3_Marker_Genes.xlsx',
        'description': 'Arabidopsis root cell type markers'
    },
    'kim_2021_leaf': {
        'pmid': '33619379',
        'url': 'https://www.nature.com/articles/s41477-021-00865-y#Sec20',
        'table': 'Supplementary_Data_3.xlsx',
        'description': 'Arabidopsis leaf cell type markers'
    },
    'xu_2021_flower': {
        'pmid': '33793920',
        'url': 'https://academic.oup.com/plcell/article/33/3/513/6117296#supplementary-data',
        'table': 'Supplementary_Table_S2.xlsx',
        'description': 'Arabidopsis flower cell type markers'
    }
}


def download_supplementary_data(paper_id: str, output_dir: str = './data/supplementary'):
    """
    Download supplementary data from published paper

    Args:
        paper_id: Paper identifier (e.g., 'denyer_2019_root')
        output_dir: Output directory
    """
    if paper_id not in SUPPLEMENTARY_DATA:
        raise ValueError(f"Unknown paper: {paper_id}")

    info = SUPPLEMENTARY_DATA[paper_id]
    output_path = Path(output_dir) / paper_id
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Downloading supplementary data for {paper_id}")
    print(f"  PMID: {info['pmid']}")
    print(f"  Description: {info['description']}")
    print(f"  URL: {info['url']}")

    # Note: Actual download would require handling journal-specific formats
    print("[WARNING] Automatic download not implemented yet.")
    print("[INFO] Please manually download from the journal website:")
    print(f"  1. Visit: {info['url']}")
    print(f"  2. Download: {info['table']}")
    print(f"  3. Save to: {output_path / info['table']}")

    return output_path / info['table']


def parse_denyer_2019_markers(excel_file: str) -> pd.DataFrame:
    """
    Parse Denyer et al. 2019 marker genes

    Expected format:
    Cell_Type | Gene | Log2FC | Pvalue | Padj
    """
    print(f"[INFO] Parsing {excel_file}")

    # Read Excel file
    df = pd.read_excel(excel_file, sheet_name='Marker_Genes')

    # Standardize format
    markers = pd.DataFrame({
        'gene_symbol': df['Gene'],
        'cell_type': df['Cell_Type'],
        'confidence': df['Padj'].apply(lambda x: 'high' if x < 1e-10 else 'medium' if x < 1e-5 else 'low'),
        'reference': f"PMID:31178400",
        'description': df['Gene_Name'] if 'Gene_Name' in df.columns else '',
        'log2fc': df['Log2FC'],
        'pvalue': df['Pvalue'],
        'padj': df['Padj']
    })

    # Filter high confidence markers
    markers = markers[markers['confidence'].isin(['high', 'medium'])]

    # Sort by cell type and confidence
    markers = markers.sort_values(['cell_type', 'padj'])

    return markers


def extract_from_geo(geo_id: str, output_file: str):
    """
    Extract marker genes from GEO dataset

    Args:
        geo_id: GEO accession (e.g., GSE123013)
        output_file: Output CSV file
    """
    print(f"[INFO] Extracting markers from {geo_id}")

    # This would require:
    # 1. Download processed data from GEO
    # 2. Load into Scanpy
    # 3. Run differential expression
    # 4. Extract top markers

    print("[WARNING] GEO extraction not implemented yet.")
    print("[INFO] Manual steps:")
    print(f"  1. Download {geo_id} from https://www.ncbi.nlm.nih.gov/geo/")
    print(f"  2. Process with Scanpy")
    print(f"  3. Extract markers")


def create_marker_template():
    """
    Create template for manual marker curation

    This is what I actually did - created a template based on
    literature knowledge, but with placeholder PMIDs.
    """
    print("[INFO] Creating marker template")

    # Known markers from literature (but need real PMIDs)
    known_markers = {
        'Endodermis': ['SCR', 'SHR', 'CASP1', 'SGN3', 'EN7'],
        'Cortex': ['CO2', 'CORTEX'],
        'Epidermis': ['PDF2', 'GL2'],
        'Root hair': ['RHD6', 'EXP7'],
        'Quiescent center': ['WOX5', 'QC25'],
        'Columella': ['SMB', 'PET111'],
        'Xylem': ['VND6', 'VND7', 'IRX3', 'IRX5'],
        'Phloem': ['APL', 'SUC2', 'CALS7']
    }

    markers = []
    for cell_type, genes in known_markers.items():
        for gene in genes:
            markers.append({
                'gene_symbol': gene,
                'cell_type': cell_type,
                'confidence': 'high',
                'reference': 'NEEDS_VERIFICATION',  # Honest placeholder
                'description': f'{cell_type} marker - needs literature verification'
            })

    df = pd.DataFrame(markers)
    return df


def main():
    parser = argparse.ArgumentParser(description='Extract marker genes from literature')
    parser.add_argument('--paper', choices=list(SUPPLEMENTARY_DATA.keys()),
                       help='Paper to extract from')
    parser.add_argument('--geo', help='GEO accession')
    parser.add_argument('--template', action='store_true',
                       help='Create template for manual curation')
    parser.add_argument('--output', default='markers.csv', help='Output file')

    args = parser.parse_args()

    if args.template:
        print("[INFO] Creating marker template")
        markers = create_marker_template()
        markers.to_csv(args.output, index=False)
        print(f"[SUCCESS] Template saved to {args.output}")
        print("[WARNING] This template needs manual verification!")
        print("[TODO] Replace 'NEEDS_VERIFICATION' with real PMIDs")

    elif args.paper:
        supp_file = download_supplementary_data(args.paper)
        # Parse based on paper format
        if args.paper == 'denyer_2019_root':
            markers = parse_denyer_2019_markers(supp_file)
        # Add more parsers for other papers
        markers.to_csv(args.output, index=False)
        print(f"[SUCCESS] Markers saved to {args.output}")

    elif args.geo:
        extract_from_geo(args.geo, args.output)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
