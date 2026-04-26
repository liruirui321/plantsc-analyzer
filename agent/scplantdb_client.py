#!/usr/bin/env python3
"""
scPlantDB Integration Module

Integrates with scPlantDB (https://biobigdata.nju.edu.cn/scplantdb/)
to fetch marker genes for plant species.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import json
from pathlib import Path
import time


class scPlantDBClient:
    """Client for accessing scPlantDB marker gene database"""

    BASE_URL = "https://biobigdata.nju.edu.cn/scplantdb"

    # Supported species (from literature)
    SUPPORTED_SPECIES = {
        'arabidopsis': 'Arabidopsis thaliana',
        'rice': 'Oryza sativa',
        'maize': 'Zea mays',
        'tomato': 'Solanum lycopersicum',
        'soybean': 'Glycine max',
        'poplar': 'Populus trichocarpa',
        'cotton': 'Gossypium hirsutum',
        'wheat': 'Triticum aestivum',
        'barley': 'Hordeum vulgare',
        'sorghum': 'Sorghum bicolor',
        'tobacco': 'Nicotiana tabacum',
        'medicago': 'Medicago truncatula',
        'brachypodium': 'Brachypodium distachyon',
        'setaria': 'Setaria viridis',
        'lotus': 'Lotus japonicus',
        'pepper': 'Capsicum annuum',
        'cucumber': 'Cucumis sativus'
    }

    def __init__(self, cache_dir: str = "./cache/scplantdb"):
        """
        Initialize scPlantDB client

        Args:
            cache_dir: Directory to cache downloaded data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PlantSC-Analyzer/0.1.0'
        })

    def get_marker_genes(
        self,
        species: str,
        tissue: Optional[str] = None,
        cell_type: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get marker genes from scPlantDB

        Args:
            species: Species name (e.g., 'arabidopsis', 'rice')
            tissue: Tissue type (e.g., 'root', 'leaf')
            cell_type: Cell type (e.g., 'xylem', 'phloem')
            use_cache: Use cached data if available

        Returns:
            DataFrame with marker genes
        """
        # Check cache
        cache_file = self._get_cache_file(species, tissue, cell_type)
        if use_cache and cache_file.exists():
            print(f"[INFO] Loading from cache: {cache_file}")
            return pd.read_csv(cache_file)

        # Fetch from scPlantDB
        print(f"[INFO] Fetching from scPlantDB: {species}")
        markers = self._fetch_markers(species, tissue, cell_type)

        # Save to cache
        if markers is not None and len(markers) > 0:
            markers.to_csv(cache_file, index=False)
            print(f"[INFO] Cached to: {cache_file}")

        return markers

    def _fetch_markers(
        self,
        species: str,
        tissue: Optional[str],
        cell_type: Optional[str]
    ) -> pd.DataFrame:
        """
        Fetch markers from scPlantDB

        Note: This is a placeholder implementation.
        Actual implementation depends on scPlantDB's API/web interface.
        """
        # Check if species is supported
        if species not in self.SUPPORTED_SPECIES:
            raise ValueError(f"Species '{species}' not supported. "
                           f"Supported: {list(self.SUPPORTED_SPECIES.keys())}")

        # Try to fetch via API (if available)
        try:
            markers = self._fetch_via_api(species, tissue, cell_type)
            if markers is not None:
                return markers
        except Exception as e:
            print(f"[WARNING] API fetch failed: {e}")

        # Fallback: Try web scraping (if API not available)
        try:
            markers = self._fetch_via_web(species, tissue, cell_type)
            if markers is not None:
                return markers
        except Exception as e:
            print(f"[WARNING] Web scraping failed: {e}")

        # Fallback: Use local curated markers
        print(f"[INFO] Using local curated markers for {species}")
        return self._load_local_markers(species, tissue)

    def _fetch_via_api(
        self,
        species: str,
        tissue: Optional[str],
        cell_type: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """
        Fetch via API (if available)

        Note: scPlantDB API endpoints need to be determined.
        This is a placeholder for future implementation.
        """
        # Example API endpoint (hypothetical)
        # url = f"{self.BASE_URL}/api/markers"
        # params = {'species': species, 'tissue': tissue, 'cell_type': cell_type}
        # response = self.session.get(url, params=params)
        # ...

        return None  # API not yet implemented

    def _fetch_via_web(
        self,
        species: str,
        tissue: Optional[str],
        cell_type: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """
        Fetch via web scraping

        Note: This requires parsing the scPlantDB web interface.
        Implementation depends on the actual HTML structure.
        """
        # This would require BeautifulSoup or similar
        # For now, return None
        return None

    def _load_local_markers(
        self,
        species: str,
        tissue: Optional[str]
    ) -> pd.DataFrame:
        """
        Load local curated markers as fallback

        Args:
            species: Species name
            tissue: Tissue type

        Returns:
            DataFrame with marker genes
        """
        # Path to local markers
        markers_dir = Path(__file__).parent.parent / 'knowledge_base' / 'markers' / species

        if tissue:
            marker_file = markers_dir / f"{tissue}_markers.csv"
        else:
            # Load all markers for this species
            marker_files = list(markers_dir.glob("*_markers.csv"))
            if not marker_files:
                raise FileNotFoundError(f"No local markers found for {species}")

            dfs = []
            for f in marker_files:
                df = pd.read_csv(f)
                df['tissue'] = f.stem.replace('_markers', '')
                dfs.append(df)

            return pd.concat(dfs, ignore_index=True)

        if not marker_file.exists():
            raise FileNotFoundError(f"Marker file not found: {marker_file}")

        return pd.read_csv(marker_file)

    def _get_cache_file(
        self,
        species: str,
        tissue: Optional[str],
        cell_type: Optional[str]
    ) -> Path:
        """Get cache file path"""
        filename = f"{species}"
        if tissue:
            filename += f"_{tissue}"
        if cell_type:
            filename += f"_{cell_type}"
        filename += ".csv"

        return self.cache_dir / filename

    def list_species(self) -> List[str]:
        """List supported species"""
        return list(self.SUPPORTED_SPECIES.keys())

    def get_species_info(self, species: str) -> Dict:
        """Get species information"""
        if species not in self.SUPPORTED_SPECIES:
            raise ValueError(f"Species '{species}' not supported")

        return {
            'short_name': species,
            'full_name': self.SUPPORTED_SPECIES[species],
            'has_local_markers': self._has_local_markers(species)
        }

    def _has_local_markers(self, species: str) -> bool:
        """Check if local markers exist"""
        markers_dir = Path(__file__).parent.parent / 'knowledge_base' / 'markers' / species
        return markers_dir.exists() and len(list(markers_dir.glob("*_markers.csv"))) > 0

    def sync_to_local(self, species: str, output_dir: str):
        """
        Sync scPlantDB markers to local directory

        Args:
            species: Species name
            output_dir: Output directory
        """
        output_path = Path(output_dir) / species
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"[INFO] Syncing {species} markers to {output_path}")

        # Fetch all markers for this species
        markers = self.get_marker_genes(species, use_cache=False)

        if markers is None or len(markers) == 0:
            print(f"[WARNING] No markers found for {species}")
            return

        # Group by tissue if available
        if 'tissue' in markers.columns:
            for tissue, group in markers.groupby('tissue'):
                output_file = output_path / f"{tissue}_markers.csv"
                group.to_csv(output_file, index=False)
                print(f"[INFO] Saved {len(group)} markers to {output_file}")
        else:
            output_file = output_path / "all_markers.csv"
            markers.to_csv(output_file, index=False)
            print(f"[INFO] Saved {len(markers)} markers to {output_file}")


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='scPlantDB Integration')
    parser.add_argument('--species', required=True, help='Species name')
    parser.add_argument('--tissue', help='Tissue type')
    parser.add_argument('--cell_type', help='Cell type')
    parser.add_argument('--list_species', action='store_true', help='List supported species')
    parser.add_argument('--sync', action='store_true', help='Sync to local directory')
    parser.add_argument('--output', default='./knowledge_base/markers', help='Output directory')

    args = parser.parse_args()

    client = scPlantDBClient()

    if args.list_species:
        print("Supported species:")
        for species in client.list_species():
            info = client.get_species_info(species)
            status = "✅" if info['has_local_markers'] else "❌"
            print(f"  {status} {species:15s} - {info['full_name']}")
        return

    if args.sync:
        client.sync_to_local(args.species, args.output)
        return

    # Fetch markers
    markers = client.get_marker_genes(
        args.species,
        tissue=args.tissue,
        cell_type=args.cell_type
    )

    if markers is not None:
        print(f"\nFound {len(markers)} markers:")
        print(markers.head(10))
    else:
        print("No markers found")


if __name__ == '__main__':
    main()
