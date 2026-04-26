#!/usr/bin/env python3
"""
Parameter Recommender

Provides intelligent parameter recommendations based on data characteristics
and best practices from the knowledge base.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import scanpy as sc
import anndata as ad


class ParameterRecommender:
    """Intelligent parameter recommendation system"""

    def __init__(self):
        self.recommendations = {}

    def analyze_data_characteristics(self, adata: ad.AnnData) -> Dict[str, Any]:
        """
        Analyze data characteristics to inform parameter choices

        Args:
            adata: AnnData object

        Returns:
            Dictionary of data characteristics
        """
        n_cells = adata.n_obs
        n_genes = adata.n_vars

        # Calculate basic statistics
        counts_per_cell = np.array(adata.X.sum(axis=1)).flatten()
        genes_per_cell = np.array((adata.X > 0).sum(axis=1)).flatten()

        characteristics = {
            'n_cells': n_cells,
            'n_genes': n_genes,
            'median_counts': np.median(counts_per_cell),
            'median_genes': np.median(genes_per_cell),
            'mean_counts': np.mean(counts_per_cell),
            'mean_genes': np.mean(genes_per_cell),
            'dataset_size': 'small' if n_cells < 5000 else 'medium' if n_cells < 20000 else 'large'
        }

        # Check for mitochondrial genes
        if 'mt' in adata.var.columns:
            characteristics['has_mito'] = adata.var['mt'].sum() > 0
        else:
            characteristics['has_mito'] = False

        # Check for batch information
        if 'batch' in adata.obs.columns:
            characteristics['n_batches'] = adata.obs['batch'].nunique()
        else:
            characteristics['n_batches'] = 1

        return characteristics

    def recommend_qc_params(self, adata: ad.AnnData) -> Dict[str, Any]:
        """
        Recommend QC parameters based on data characteristics

        Args:
            adata: AnnData object

        Returns:
            Dictionary of recommended QC parameters
        """
        chars = self.analyze_data_characteristics(adata)

        # Calculate percentiles for adaptive thresholds
        genes_per_cell = np.array((adata.X > 0).sum(axis=1)).flatten()
        counts_per_cell = np.array(adata.X.sum(axis=1)).flatten()

        # Min genes: 5th percentile or 200, whichever is lower
        min_genes = min(int(np.percentile(genes_per_cell, 5)), 200)

        # Max genes: 95th percentile or 6000, whichever is higher
        max_genes = max(int(np.percentile(genes_per_cell, 95)), 6000)

        # Mitochondrial threshold
        if chars['has_mito']:
            mito_pct = adata.obs['pct_counts_mt'] if 'pct_counts_mt' in adata.obs else None
            if mito_pct is not None:
                mito_threshold = min(np.percentile(mito_pct, 95), 10.0)
            else:
                mito_threshold = 5.0
        else:
            mito_threshold = 5.0

        recommendations = {
            'min_genes': min_genes,
            'max_genes': max_genes,
            'min_cells': 3,
            'mito_threshold': mito_threshold,
            'run_soupx': True,
            'run_scrublet': chars['n_cells'] > 1000,
            'reasoning': {
                'min_genes': f"Based on 5th percentile of gene counts ({min_genes})",
                'max_genes': f"Based on 95th percentile of gene counts ({max_genes})",
                'mito_threshold': f"Based on data distribution (95th percentile: {mito_threshold:.1f}%)",
                'run_scrublet': "Recommended for datasets >1000 cells" if chars['n_cells'] > 1000 else "Not needed for small datasets"
            }
        }

        return recommendations

    def recommend_normalization_params(self, adata: ad.AnnData) -> Dict[str, Any]:
        """
        Recommend normalization parameters

        Args:
            adata: AnnData object

        Returns:
            Dictionary of recommended normalization parameters
        """
        chars = self.analyze_data_characteristics(adata)

        # HVG number based on dataset size
        if chars['dataset_size'] == 'small':
            n_hvg = 2000
        elif chars['dataset_size'] == 'medium':
            n_hvg = 3000
        else:
            n_hvg = 4000

        # Method selection
        if chars['n_batches'] > 1:
            hvg_flavor = 'seurat_v3'  # Better for batch-aware selection
        else:
            hvg_flavor = 'seurat'

        recommendations = {
            'method': 'log1p',
            'target_sum': 10000,
            'n_hvg': n_hvg,
            'hvg_flavor': hvg_flavor,
            'hvg_batch_key': 'batch' if chars['n_batches'] > 1 else None,
            'scale': True,
            'reasoning': {
                'n_hvg': f"Recommended {n_hvg} HVGs for {chars['dataset_size']} dataset",
                'hvg_flavor': f"Using {hvg_flavor} for {'batch-aware' if chars['n_batches'] > 1 else 'standard'} selection",
                'hvg_batch_key': "Batch-aware HVG selection enabled" if chars['n_batches'] > 1 else "Single batch, no batch correction needed"
            }
        }

        return recommendations

    def recommend_integration_params(self, adata: ad.AnnData) -> Dict[str, Any]:
        """
        Recommend batch integration parameters

        Args:
            adata: AnnData object

        Returns:
            Dictionary of recommended integration parameters
        """
        chars = self.analyze_data_characteristics(adata)

        if chars['n_batches'] <= 1:
            return {
                'run': False,
                'reasoning': "Single batch detected, integration not needed"
            }

        # Method selection based on dataset size
        if chars['dataset_size'] == 'large':
            method = 'harmony'  # Faster for large datasets
        else:
            method = 'scvi'  # More accurate for smaller datasets

        recommendations = {
            'run': True,
            'method': method,
            'batch_key': 'batch',
            'harmony': {
                'n_pcs': 50,
                'theta': 2.0
            },
            'scvi': {
                'n_latent': 30,
                'n_layers': 2,
                'n_epochs': 400 if chars['dataset_size'] != 'large' else 200
            },
            'reasoning': {
                'method': f"Using {method} for {chars['dataset_size']} dataset with {chars['n_batches']} batches",
                'n_batches': f"Detected {chars['n_batches']} batches, integration recommended"
            }
        }

        return recommendations

    def recommend_clustering_params(self, adata: ad.AnnData) -> Dict[str, Any]:
        """
        Recommend clustering parameters

        Args:
            adata: AnnData object

        Returns:
            Dictionary of recommended clustering parameters
        """
        chars = self.analyze_data_characteristics(adata)

        # n_neighbors based on dataset size
        if chars['dataset_size'] == 'small':
            n_neighbors = 10
        elif chars['dataset_size'] == 'medium':
            n_neighbors = 15
        else:
            n_neighbors = 30

        # Resolution range
        if chars['dataset_size'] == 'small':
            resolutions = [0.3, 0.5, 0.7]
        elif chars['dataset_size'] == 'medium':
            resolutions = [0.4, 0.6, 0.8, 1.0]
        else:
            resolutions = [0.5, 0.8, 1.0, 1.2]

        recommendations = {
            'n_neighbors': n_neighbors,
            'n_pcs': 50,
            'resolution': resolutions,
            'algorithm': 'leiden',
            'metric': 'euclidean',
            'reasoning': {
                'n_neighbors': f"Using {n_neighbors} neighbors for {chars['dataset_size']} dataset",
                'resolution': f"Testing {len(resolutions)} resolutions to find optimal clustering",
                'algorithm': "Leiden algorithm recommended for better community detection"
            }
        }

        return recommendations

    def recommend_all_params(self, adata: ad.AnnData) -> Dict[str, Dict[str, Any]]:
        """
        Generate comprehensive parameter recommendations for all steps

        Args:
            adata: AnnData object

        Returns:
            Dictionary of recommendations for all analysis steps
        """
        print("[INFO] Analyzing data characteristics...")
        chars = self.analyze_data_characteristics(adata)

        print(f"[INFO] Dataset characteristics:")
        print(f"  Cells: {chars['n_cells']}")
        print(f"  Genes: {chars['n_genes']}")
        print(f"  Median genes/cell: {chars['median_genes']:.0f}")
        print(f"  Median UMIs/cell: {chars['median_counts']:.0f}")
        print(f"  Dataset size: {chars['dataset_size']}")
        print(f"  Batches: {chars['n_batches']}")

        print("\n[INFO] Generating recommendations...")

        all_recommendations = {
            'data_characteristics': chars,
            'qc': self.recommend_qc_params(adata),
            'normalization': self.recommend_normalization_params(adata),
            'integration': self.recommend_integration_params(adata),
            'clustering': self.recommend_clustering_params(adata)
        }

        return all_recommendations

    def print_recommendations(self, recommendations: Dict[str, Any]):
        """Pretty print recommendations"""
        print("\n" + "="*70)
        print("PARAMETER RECOMMENDATIONS")
        print("="*70)

        for step, params in recommendations.items():
            if step == 'data_characteristics':
                continue

            print(f"\n{step.upper()}:")
            print("-" * 70)

            if 'reasoning' in params:
                reasoning = params.pop('reasoning')

            for key, value in params.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")

            if 'reasoning' in locals():
                print("\n  Reasoning:")
                for key, reason in reasoning.items():
                    print(f"    - {reason}")

        print("="*70)
