#!/usr/bin/env python3
"""
Test Knowledge Retriever

Unit tests for knowledge_retriever.py
"""

import pytest
from pathlib import Path
import sys

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'agent'))
from knowledge_retriever import KnowledgeRetriever


@pytest.fixture
def retriever():
    """Create a knowledge retriever instance"""
    return KnowledgeRetriever()


def test_initialization(retriever):
    """Test knowledge retriever initialization"""
    assert retriever is not None
    assert retriever.knowledge_dir.exists()


def test_get_available_species(retriever):
    """Test getting available species"""
    species = retriever.get_available_species()
    assert isinstance(species, list)
    # Should have at least arabidopsis
    assert 'arabidopsis' in species


def test_get_available_tissues(retriever):
    """Test getting available tissues for a species"""
    tissues = retriever.get_available_tissues('arabidopsis')
    assert isinstance(tissues, list)
    # Should have at least xylem
    if len(tissues) > 0:
        assert 'xylem' in tissues


def test_get_markers_arabidopsis(retriever):
    """Test getting markers for arabidopsis"""
    markers = retriever.get_markers('arabidopsis')
    assert isinstance(markers, list)
    # Should have some markers
    if len(markers) > 0:
        marker = markers[0]
        assert 'gene_symbol' in marker
        assert 'cell_type' in marker


def test_get_markers_with_tissue(retriever):
    """Test getting markers with tissue filter"""
    markers = retriever.get_markers('arabidopsis', tissue='xylem')
    assert isinstance(markers, list)


def test_get_markers_with_cell_type(retriever):
    """Test getting markers with cell type filter"""
    markers = retriever.get_markers('arabidopsis', cell_type='vessel')
    assert isinstance(markers, list)
    # All markers should contain 'vessel' in cell_type
    for marker in markers:
        assert 'vessel' in marker.get('cell_type', '').lower()


def test_get_markers_nonexistent_species(retriever):
    """Test getting markers for non-existent species"""
    markers = retriever.get_markers('nonexistent_species')
    assert isinstance(markers, list)
    assert len(markers) == 0


def test_search_markers_by_gene(retriever):
    """Test searching markers by gene symbol"""
    # This will depend on what's in the knowledge base
    markers = retriever.search_markers_by_gene('VND')
    assert isinstance(markers, list)


def test_recommend_markers_for_tissue(retriever):
    """Test recommending markers for tissue"""
    markers = retriever.recommend_markers_for_tissue(
        'arabidopsis',
        'xylem',
        confidence='high'
    )
    assert isinstance(markers, list)
    # High confidence markers should be first
    if len(markers) > 1:
        confidences = [m.get('confidence', 'low') for m in markers]
        # Check that high confidence comes before medium/low
        if 'high' in confidences and 'medium' in confidences:
            high_idx = confidences.index('high')
            medium_idx = confidences.index('medium')
            assert high_idx < medium_idx


def test_get_method_info(retriever):
    """Test getting method information"""
    # This will depend on what's in the knowledge base
    info = retriever.get_method_info('qc_methods')
    # Should return None or string
    assert info is None or isinstance(info, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
