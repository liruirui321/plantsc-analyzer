#!/usr/bin/env python3
"""
SoupX Ambient RNA Removal

Removes ambient RNA contamination from single-cell data using SoupX algorithm.
Requires both raw and filtered matrices.

Reference: Young & Behjati (2020) Genome Biology
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from scipy.sparse import csr_matrix
import subprocess
import tempfile
import shutil


def run_soupx_r(raw_matrix_dir: str, filtered_matrix_dir: str,
                sample_id: str, output_dir: str, min_genes: int = 200) -> dict:
    """
    Run SoupX using R script

    Args:
        raw_matrix_dir: Path to raw matrix directory
        filtered_matrix_dir: Path to filtered matrix directory
        sample_id: Sample identifier
        output_dir: Output directory
        min_genes: Minimum genes per cell

    Returns:
        dict with contamination fraction (rho) and status
    """

    # Create R script
    r_script = f"""
    library(Seurat)
    library(SoupX)
    library(DropletUtils)

    # Load matrices
    toc <- Read10X('{filtered_matrix_dir}', gene.column=1)
    tod <- Read10X('{raw_matrix_dir}', gene.column=1)

    # Create Seurat object for clustering
    seu <- CreateSeuratObject(toc)
    seu <- subset(seu, subset = nFeature_RNA > {min_genes})
    seu <- NormalizeData(seu)
    seu <- FindVariableFeatures(seu, nfeatures = 3000)
    seu <- ScaleData(seu)
    seu <- RunPCA(seu, npcs = 40, verbose = FALSE)
    seu <- FindNeighbors(seu, dims = 1:30)
    seu <- FindClusters(seu, resolution = 0.5)
    seu <- RunUMAP(seu, dims = 1:30)

    # Get cluster assignments
    meta <- seu@meta.data
    toc_filtered <- GetAssayData(seu, layer = "counts", assay = "RNA")

    # Match raw matrix genes
    tod_matched <- tod[rownames(toc_filtered), ]

    # Create SoupChannel
    sc <- SoupChannel(tod_matched, toc_filtered)
    sc <- setClusters(sc, setNames(meta$seurat_clusters, rownames(meta)))

    # Estimate contamination
    sc <- autoEstCont(sc, tfidfMin = 1.0, forceAccept = TRUE, doPlot = FALSE)

    # Get rho value
    rho_value <- unique(sc$metaData$rho)

    # Adjust counts
    out <- adjustCounts(sc)

    # Write output
    DropletUtils::write10xCounts('{output_dir}/{sample_id}_soupx', out, version="3")

    # Write rho info
    write.table(
        data.frame(sample='{sample_id}', rho=rho_value,
                   status=ifelse(rho_value < 0.2, 'good', 'high_contamination')),
        file='{output_dir}/{sample_id}_soupx_rho.txt',
        row.names=FALSE, quote=FALSE, sep='\\t'
    )
    """

    # Write R script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
        f.write(r_script)
        r_script_path = f.name

    try:
        # Run R script
        result = subprocess.run(
            ['Rscript', r_script_path],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"SoupX R script failed:\n{result.stderr}")

        # Read rho info
        rho_file = Path(output_dir) / f"{sample_id}_soupx_rho.txt"
        if rho_file.exists():
            rho_df = pd.read_csv(rho_file, sep='\t')
            return {
                'rho': float(rho_df['rho'].iloc[0]),
                'status': rho_df['status'].iloc[0]
            }
        else:
            return {'rho': None, 'status': 'unknown'}

    finally:
        # Cleanup
        Path(r_script_path).unlink()


def convert_soupx_output_to_h5ad(soupx_dir: str, original_adata: ad.AnnData,
                                  sample_id: str, output_path: str):
    """
    Convert SoupX output to h5ad format

    Args:
        soupx_dir: SoupX output directory
        original_adata: Original AnnData object (for metadata)
        sample_id: Sample identifier
        output_path: Output h5ad path
    """
    # Read SoupX corrected matrix
    corrected = sc.read_10x_mtx(soupx_dir, var_names='gene_symbols', cache=True)

    # Transfer metadata from original
    common_cells = original_adata.obs_names.intersection(corrected.obs_names)
    corrected = corrected[common_cells, :]

    # Copy obs metadata
    for col in original_adata.obs.columns:
        if col in corrected.obs.columns:
            continue
        corrected.obs[col] = original_adata.obs.loc[common_cells, col]

    # Add SoupX flag
    corrected.obs['soupx_corrected'] = True

    # Save
    corrected.write_h5ad(output_path, compression='gzip')

    return corrected


def main():
    parser = argparse.ArgumentParser(description='SoupX ambient RNA removal')
    parser.add_argument('--sample_id', required=True, help='Sample ID')
    parser.add_argument('--matrix', required=True, help='Input h5ad file (filtered)')
    parser.add_argument('--raw_matrix', required=False, help='Raw matrix directory (if available)')
    parser.add_argument('--min_genes', type=int, default=200, help='Minimum genes per cell')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--report', required=True, help='Output report file')
    parser.add_argument('--skip_if_no_raw', action='store_true',
                       help='Skip SoupX if raw matrix not available')

    args = parser.parse_args()

    try:
        print(f"[INFO] Loading filtered matrix: {args.matrix}")
        adata = sc.read_h5ad(args.matrix)

        print(f"[INFO] Input: {adata.n_obs} cells, {adata.n_vars} genes")

        # Check if raw matrix is available
        if args.raw_matrix and Path(args.raw_matrix).exists():
            print(f"[INFO] Running SoupX with raw matrix: {args.raw_matrix}")

            # Create temp directory for SoupX output
            with tempfile.TemporaryDirectory() as tmpdir:
                # Export filtered matrix to 10X format
                filtered_dir = Path(tmpdir) / 'filtered'
                filtered_dir.mkdir()

                # Write 10X format (simplified - assumes matrix is already in correct format)
                # In practice, you'd need to export adata to 10X format here

                # Run SoupX
                result = run_soupx_r(
                    raw_matrix_dir=args.raw_matrix,
                    filtered_matrix_dir=str(filtered_dir),
                    sample_id=args.sample_id,
                    output_dir=tmpdir,
                    min_genes=args.min_genes
                )

                # Convert output to h5ad
                soupx_output_dir = Path(tmpdir) / f"{args.sample_id}_soupx"
                if soupx_output_dir.exists():
                    corrected_adata = convert_soupx_output_to_h5ad(
                        str(soupx_output_dir),
                        adata,
                        args.sample_id,
                        args.output
                    )

                    # Write report
                    with open(args.report, 'w') as f:
                        f.write(f"Sample: {args.sample_id}\n")
                        f.write(f"Contamination fraction (rho): {result['rho']:.4f}\n")
                        f.write(f"Status: {result['status']}\n")
                        f.write(f"Cells before: {adata.n_obs}\n")
                        f.write(f"Cells after: {corrected_adata.n_obs}\n")
                        f.write(f"Genes: {corrected_adata.n_vars}\n")

                    print(f"[INFO] SoupX completed. Rho = {result['rho']:.4f}")
                    print(f"[INFO] Output: {corrected_adata.n_obs} cells, {corrected_adata.n_vars} genes")
                else:
                    raise RuntimeError("SoupX output directory not found")

        else:
            # No raw matrix - skip SoupX
            if args.skip_if_no_raw:
                print("[WARNING] No raw matrix provided, skipping SoupX")
                adata.obs['soupx_corrected'] = False
                adata.write_h5ad(args.output, compression='gzip')

                with open(args.report, 'w') as f:
                    f.write(f"Sample: {args.sample_id}\n")
                    f.write(f"Status: SKIPPED (no raw matrix)\n")
                    f.write(f"Cells: {adata.n_obs}\n")
                    f.write(f"Genes: {adata.n_vars}\n")
            else:
                raise ValueError("Raw matrix required for SoupX. Use --skip_if_no_raw to bypass.")

        print(f"[INFO] Saved to {args.output}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
