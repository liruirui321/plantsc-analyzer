#!/usr/bin/env python3
"""
Knowledge Retriever (RAG)

Retrieves relevant knowledge from the built-in knowledge base
using vector similarity search for context-aware recommendations.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import json


class KnowledgeRetriever:
    """Knowledge base retriever with optional vector search"""

    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir else self._find_knowledge_dir()
        self.markers_cache = {}
        self.methods_cache = {}
        self._load_knowledge()

    def _find_knowledge_dir(self) -> Path:
        """Find the knowledge base directory"""
        candidates = [
            Path(__file__).parent.parent / 'knowledge_base',
            Path.cwd() / 'knowledge_base',
            Path.home() / '.plantsc' / 'knowledge_base'
        ]
        for p in candidates:
            if p.exists():
                return p
        return candidates[0]

    def _load_knowledge(self):
        """Load all knowledge base files"""
        # Load markers
        markers_dir = self.knowledge_dir / 'markers'
        if markers_dir.exists():
            for species_dir in markers_dir.iterdir():
                if species_dir.is_dir() and species_dir.name != '__pycache__':
                    species = species_dir.name
                    self.markers_cache[species] = {}
                    for csv_file in species_dir.glob('*.csv'):
                        try:
                            import pandas as pd
                            df = pd.read_csv(csv_file)
                            tissue = csv_file.stem.replace('_markers', '')
                            self.markers_cache[species][tissue] = df
                        except Exception:
                            pass

        # Load methods knowledge
        methods_dir = self.knowledge_dir / 'methods'
        if methods_dir.exists():
            for md_file in methods_dir.glob('*.md'):
                self.methods_cache[md_file.stem] = md_file.read_text()

        print(f"[INFO] Knowledge base loaded:")
        print(f"  Species: {list(self.markers_cache.keys())}")
        print(f"  Methods docs: {list(self.methods_cache.keys())}")

    def get_markers(self, species: str, tissue: str = None,
                    cell_type: str = None) -> List[Dict]:
        """
        Retrieve marker genes from the database

        Args:
            species: Species name
            tissue: Tissue type (optional)
            cell_type: Cell type (optional)

        Returns:
            List of marker gene records
        """
        if species not in self.markers_cache:
            print(f"[WARNING] No markers found for species: {species}")
            print(f"[INFO] Available species: {list(self.markers_cache.keys())}")
            return []

        results = []
        species_markers = self.markers_cache[species]

        # Search across all tissue files
        for tissue_name, df in species_markers.items():
            if tissue and tissue.lower() not in tissue_name.lower():
                continue

            if cell_type:
                filtered = df[df['cell_type'].str.contains(cell_type, case=False, na=False)]
            else:
                filtered = df

            for _, row in filtered.iterrows():
                results.append(row.to_dict())

        return results

    def get_available_species(self) -> List[str]:
        """Get list of available species"""
        return list(self.markers_cache.keys())

    def get_available_tissues(self, species: str) -> List[str]:
        """Get list of available tissues for a species"""
        if species not in self.markers_cache:
            return []
        return list(self.markers_cache[species].keys())

    def get_method_info(self, method_name: str) -> Optional[str]:
        """
        Retrieve method documentation

        Args:
            method_name: Method name (e.g., 'qc_methods', 'integration_methods')

        Returns:
            Method documentation text
        """
        # Exact match
        if method_name in self.methods_cache:
            return self.methods_cache[method_name]

        # Fuzzy match
        for key, value in self.methods_cache.items():
            if method_name.lower() in key.lower():
                return value

        return None

    def search_markers_by_gene(self, gene_symbol: str) -> List[Dict]:
        """
        Search for a gene across all species and tissues

        Args:
            gene_symbol: Gene symbol to search

        Returns:
            List of matching marker records
        """
        results = []
        for species, tissues in self.markers_cache.items():
            for tissue, df in tissues.items():
                matches = df[df['gene_symbol'].str.contains(gene_symbol, case=False, na=False)]
                for _, row in matches.iterrows():
                    record = row.to_dict()
                    record['species'] = species
                    record['tissue_source'] = tissue
                    results.append(record)

        return results

    def recommend_markers_for_tissue(self, species: str, tissue: str,
                                     confidence: str = 'high') -> List[Dict]:
        """
        Recommend marker genes for a specific tissue

        Args:
            species: Species name
            tissue: Tissue type
            confidence: Minimum confidence level

        Returns:
            Sorted list of recommended markers
        """
        markers = self.get_markers(species, tissue)

        if confidence:
            confidence_order = {'high': 3, 'medium': 2, 'low': 1}
            min_conf = confidence_order.get(confidence, 0)
            markers = [
                m for m in markers
                if confidence_order.get(m.get('confidence', 'low'), 0) >= min_conf
            ]

        # Sort by confidence
        markers.sort(
            key=lambda x: confidence_order.get(x.get('confidence', 'low'), 0),
            reverse=True
        )

        return markers
