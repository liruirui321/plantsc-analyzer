#!/usr/bin/env python3
"""
Cross-Species Analysis Module

Enables integration and comparison of single-cell data across plant species.
Includes ortholog mapping, cell type matching, and evolutionary analysis.

Based on: Benchmarking cross-species single-cell RNA-seq data integration methods
NAR, 2024. DOI: 10.1093/nar/gkae1316
"""

import argparse
import sys
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

try:
    import scanpy as sc
    import anndata as ad
except ImportError:
    print("[ERROR] scanpy/anndata not installed. Run: pip install scanpy anndata")
    sys.exit(1)


class CrossSpeciesAnalyzer:
    """Cross-species single-cell analysis"""

    # Common ortholog databases
    ORTHOLOG_SOURCES = {
        'ensembl': 'Ensembl Plants',
        'phytozome': 'Phytozome',
        'plaza': 'PLAZA'
    }

    # Species codes
    SPECIES_CODES = {
        'arabidopsis': 'AT',
        'rice': 'OS',
        'maize': 'ZM',
        'tomato': 'SL',
        'soybean': 'GM',
        'poplar': 'PT'
    }

    def __init__(self, ortholog_db: Optional[str] = None):
        """
        Initialize cross-species analyzer

        Args:
            ortholog_db: Path to ortholog database file
        """
        self.ortholog_db = ortholog_db
        self.ortholog_map = None

        if ortholog_db:
            self.load_ortholog_db(ortholog_db)

    def load_ortholog_db(self, db_path: str):
        """
        Load ortholog database

        Expected format:
        species1,gene1,species2,gene2,confidence
        arabidopsis,AT1G01010,rice,OS01G0100100,0.95
        """
        print(f"[INFO] Loading ortholog database: {db_path}")
        self.ortholog_map = pd.read_csv(db_path)
        print(f"[INFO] Loaded {len(self.ortholog_map)} ortholog pairs")

    def map_orthologs(
        self,
        genes: List[str],
        source_species: str,
        target_species: str,
        min_confidence: float = 0.8
    ) -> Dict[str, str]:
        """
        Map genes to orthologs in target species

        Args:
            genes: List of gene IDs
            source_species: Source species
            target_species: Target species
            min_confidence: Minimum ortholog confidence

        Returns:
            Dict mapping source genes to target orthologs
        """
        if self.ortholog_map is None:
            print("[WARNING] No ortholog database loaded. Using gene name matching.")
            return self._map_by_gene_name(genes, source_species, target_species)

        ortholog_dict = {}

        for gene in genes:
            # Query ortholog database
            matches = self.ortholog_map[
                (self.ortholog_map['species1'] == source_species) &
                (self.ortholog_map['gene1'] == gene) &
                (self.ortholog_map['species2'] == target_species) &
                (self.ortholog_map['confidence'] >= min_confidence)
            ]

            if len(matches) > 0:
                # Take highest confidence match
                best_match = matches.loc[matches['confidence'].idxmax()]
                ortholog_dict[gene] = best_match['gene2']

        print(f"[INFO] Mapped {len(ortholog_dict)}/{len(genes)} genes to {target_species}")

        return ortholog_dict

    def _map_by_gene_name(
        self,
        genes: List[str],
        source_species: str,
        target_species: str
    ) -> Dict[str, str]:
        """
        Fallback: Map by gene name similarity

        Removes species prefix and matches by gene family name
        """
        source_prefix = self.SPECIES_CODES.get(source_species, '')
        target_prefix = self.SPECIES_CODES.get(target_species, '')

        ortholog_dict = {}

        for gene in genes:
            # Remove species prefix
            if source_prefix and gene.startswith(source_prefix):
                gene_name = gene[len(source_prefix):]
                # Add target prefix
                target_gene = target_prefix + gene_name
                ortholog_dict[gene] = target_gene

        return ortholog_dict

    def integrate_species(
        self,
        adata_list: List[ad.AnnData],
        species_list: List[str],
        reference_species: str = 'arabidopsis',
        method: str = 'scvi',
        batch_key: str = 'species'
    ) -> ad.AnnData:
        """
        Integrate multiple species datasets

        Args:
            adata_list: List of AnnData objects
            species_list: List of species names
            reference_species: Reference species for ortholog mapping
            method: Integration method (scvi, harmony, scanorama)
            batch_key: Key for batch information

        Returns:
            Integrated AnnData object
        """
        print(f"[INFO] Integrating {len(adata_list)} species datasets...")

        # Map all genes to reference species
        mapped_adatas = []

        for adata, species in zip(adata_list, species_list):
            print(f"[INFO] Processing {species}...")

            if species == reference_species:
                # No mapping needed
                adata.obs[batch_key] = species
                mapped_adatas.append(adata)
            else:
                # Map to reference species
                mapped_adata = self._map_adata_to_reference(
                    adata,
                    species,
                    reference_species
                )
                mapped_adata.obs[batch_key] = species
                mapped_adatas.append(mapped_adata)

        # Find common genes
        common_genes = set(mapped_adatas[0].var_names)
        for adata in mapped_adatas[1:]:
            common_genes &= set(adata.var_names)

        print(f"[INFO] Found {len(common_genes)} common genes")

        # Subset to common genes
        for i in range(len(mapped_adatas)):
            mapped_adatas[i] = mapped_adatas[i][:, list(common_genes)].copy()

        # Concatenate
        integrated = ad.concat(mapped_adatas, label=batch_key, keys=species_list)

        # Batch correction
        print(f"[INFO] Applying batch correction ({method})...")

        if method == 'harmony':
            import harmonypy as hm
            sc.pp.pca(integrated)
            ho = hm.run_harmony(
                integrated.obsm['X_pca'],
                integrated.obs,
                batch_key
            )
            integrated.obsm['X_pca_harmony'] = ho.Z_corr.T

        elif method == 'scvi':
            try:
                import scvi
                scvi.model.SCVI.setup_anndata(integrated, batch_key=batch_key)
                model = scvi.model.SCVI(integrated)
                model.train()
                integrated.obsm['X_scvi'] = model.get_latent_representation()
            except ImportError:
                print("[WARNING] scvi-tools not installed. Skipping scVI integration.")

        elif method == 'scanorama':
            import scanorama
            # Split by batch
            adatas = [integrated[integrated.obs[batch_key] == sp] for sp in species_list]
            # Integrate
            integrated_data = scanorama.integrate_scanpy(adatas, dimred=50)
            # Merge back
            integrated = ad.concat(integrated_data)

        print("[SUCCESS] Integration complete")

        return integrated

    def _map_adata_to_reference(
        self,
        adata: ad.AnnData,
        source_species: str,
        target_species: str
    ) -> ad.AnnData:
        """Map AnnData genes to reference species"""

        genes = list(adata.var_names)
        ortholog_map = self.map_orthologs(genes, source_species, target_species)

        # Filter to mapped genes
        mapped_genes = [g for g in genes if g in ortholog_map]
        adata_mapped = adata[:, mapped_genes].copy()

        # Rename genes
        adata_mapped.var_names = [ortholog_map[g] for g in mapped_genes]

        return adata_mapped

    def compare_cell_types(
        self,
        adata: ad.AnnData,
        species1: str,
        species2: str,
        cell_type_key: str = 'cell_type',
        species_key: str = 'species'
    ) -> pd.DataFrame:
        """
        Compare cell types between two species

        Args:
            adata: Integrated AnnData
            species1: First species
            species2: Second species
            cell_type_key: Key for cell type labels
            species_key: Key for species labels

        Returns:
            DataFrame with cell type comparison
        """
        print(f"[INFO] Comparing cell types: {species1} vs {species2}")

        # Subset to two species
        adata_sub = adata[adata.obs[species_key].isin([species1, species2])].copy()

        # Get cell types
        ct1 = set(adata_sub[adata_sub.obs[species_key] == species1].obs[cell_type_key].unique())
        ct2 = set(adata_sub[adata_sub.obs[species_key] == species2].obs[cell_type_key].unique())

        # Find common and unique
        common = ct1 & ct2
        unique1 = ct1 - ct2
        unique2 = ct2 - ct1

        comparison = pd.DataFrame({
            'cell_type': list(common) + list(unique1) + list(unique2),
            species1: [True]*len(common) + [True]*len(unique1) + [False]*len(unique2),
            species2: [True]*len(common) + [False]*len(unique1) + [True]*len(unique2),
            'status': ['Common']*len(common) + [f'{species1}-specific']*len(unique1) + [f'{species2}-specific']*len(unique2)
        })

        return comparison

    def evolutionary_analysis(
        self,
        adata: ad.AnnData,
        cell_type: str,
        species_key: str = 'species',
        cell_type_key: str = 'cell_type'
    ) -> Dict:
        """
        Analyze evolutionary conservation of a cell type

        Args:
            adata: Integrated AnnData
            cell_type: Cell type to analyze
            species_key: Key for species labels
            cell_type_key: Key for cell type labels

        Returns:
            Dict with evolutionary analysis results
        """
        print(f"[INFO] Evolutionary analysis for: {cell_type}")

        # Subset to cell type
        adata_ct = adata[adata.obs[cell_type_key] == cell_type].copy()

        # Count cells per species
        species_counts = adata_ct.obs[species_key].value_counts()

        # Find conserved marker genes
        sc.tl.rank_genes_groups(adata_ct, species_key, method='wilcoxon')

        # Get top genes per species
        top_genes_per_species = {}
        for species in adata_ct.obs[species_key].unique():
            genes = []
            for i in range(20):
                gene = adata_ct.uns['rank_genes_groups']['names'][i][species]
                genes.append(gene)
            top_genes_per_species[species] = genes

        # Find conserved genes (present in all species)
        all_species = list(top_genes_per_species.keys())
        conserved_genes = set(top_genes_per_species[all_species[0]])
        for species in all_species[1:]:
            conserved_genes &= set(top_genes_per_species[species])

        return {
            'cell_type': cell_type,
            'n_species': len(species_counts),
            'species_counts': species_counts.to_dict(),
            'conserved_genes': list(conserved_genes),
            'n_conserved': len(conserved_genes),
            'top_genes_per_species': top_genes_per_species
        }


def main():
    parser = argparse.ArgumentParser(description='Cross-Species Analysis')
    parser.add_argument('--inputs', nargs='+', required=True, help='Input h5ad files')
    parser.add_argument('--species', nargs='+', required=True, help='Species names')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    parser.add_argument('--reference', default='arabidopsis', help='Reference species')
    parser.add_argument('--method', default='scvi', choices=['scvi', 'harmony', 'scanorama'],
                       help='Integration method')
    parser.add_argument('--ortholog_db', help='Ortholog database file')
    parser.add_argument('--compare', action='store_true', help='Compare cell types')

    args = parser.parse_args()

    # Load data
    print(f"[INFO] Loading {len(args.inputs)} datasets...")
    adata_list = [sc.read_h5ad(f) for f in args.inputs]

    # Initialize analyzer
    analyzer = CrossSpeciesAnalyzer(ortholog_db=args.ortholog_db)

    # Integrate
    integrated = analyzer.integrate_species(
        adata_list,
        args.species,
        reference_species=args.reference,
        method=args.method
    )

    # Save
    integrated.write_h5ad(args.output)
    print(f"[SUCCESS] Saved integrated data to {args.output}")

    # Compare cell types
    if args.compare and len(args.species) >= 2:
        comparison = analyzer.compare_cell_types(
            integrated,
            args.species[0],
            args.species[1]
        )
        comparison_file = args.output.replace('.h5ad', '_comparison.csv')
        comparison.to_csv(comparison_file, index=False)
        print(f"[SUCCESS] Saved comparison to {comparison_file}")


if __name__ == '__main__':
    main()
