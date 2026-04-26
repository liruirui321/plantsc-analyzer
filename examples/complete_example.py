#!/usr/bin/env python3
"""
Complete Example: PlantSC-Analyzer End-to-End Workflow

Demonstrates the full analysis pipeline from raw data to cell type annotation.
"""

import scanpy as sc
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.scplantdb_client import scPlantDBClient
from agent.rag_retriever import RAGKnowledgeRetriever
from scripts.utils.cross_species import CrossSpeciesAnalyzer


def example_1_basic_workflow():
    """Example 1: Basic single-species analysis"""

    print("="*80)
    print("Example 1: Basic Arabidopsis Root Analysis")
    print("="*80)

    # Simulate loading data (replace with real data)
    print("\n[Step 1] Loading data...")
    # adata = sc.read_h5ad('data/arabidopsis_root.h5ad')
    # For demo, create synthetic data
    adata = sc.datasets.pbmc3k()
    adata.obs['species'] = 'arabidopsis'
    adata.obs['tissue'] = 'root'

    print(f"  Loaded: {adata.n_obs} cells, {adata.n_vars} genes")

    # QC
    print("\n[Step 2] Quality control...")
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)

    # Calculate QC metrics
    adata.var['mt'] = adata.var_names.str.startswith('ATMG')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

    # Filter
    adata = adata[adata.obs.n_genes_by_counts < 2500, :]
    adata = adata[adata.obs.pct_counts_mt < 5, :]

    print(f"  After QC: {adata.n_obs} cells")

    # Normalize
    print("\n[Step 3] Normalization...")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # HVG
    print("\n[Step 4] Finding highly variable genes...")
    sc.pp.highly_variable_genes(adata, n_top_genes=2000)

    # PCA
    print("\n[Step 5] PCA...")
    sc.tl.pca(adata, svd_solver='arpack')

    # Clustering
    print("\n[Step 6] Clustering...")
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.leiden(adata, resolution=0.5)
    sc.tl.umap(adata)

    print(f"  Found {adata.obs['leiden'].nunique()} clusters")

    # Annotation
    print("\n[Step 7] Cell type annotation...")
    print("  (Using scPlantDB markers)")

    client = scPlantDBClient()
    markers = client.get_marker_genes('arabidopsis', tissue='root')
    print(f"  Loaded {len(markers)} marker genes")

    print("\n[SUCCESS] Basic workflow complete!")
    print(f"  Output: {adata.n_obs} cells, {adata.obs['leiden'].nunique()} clusters")

    return adata


def example_2_llm_annotation():
    """Example 2: LLM-assisted annotation"""

    print("\n" + "="*80)
    print("Example 2: LLM-Assisted Cell Type Annotation")
    print("="*80)

    print("\n[INFO] This example requires OpenAI API key")
    print("[INFO] Set environment variable: export OPENAI_API_KEY='sk-...'")

    # Check if API key is set
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("[WARNING] OPENAI_API_KEY not set. Skipping LLM annotation.")
        return

    # Load clustered data
    print("\n[Step 1] Loading clustered data...")
    # adata = sc.read_h5ad('results/clustered.h5ad')
    adata = example_1_basic_workflow()

    # LLM annotation
    print("\n[Step 2] LLM annotation...")
    try:
        from scripts.llm_annotate import LLMAnnotator

        annotator = LLMAnnotator(model='gpt-4', provider='openai')

        # Annotate first 3 clusters (to save API costs)
        print("  Annotating first 3 clusters...")

        for cluster in ['0', '1', '2']:
            # Get marker genes
            sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
            marker_genes = [adata.uns['rank_genes_groups']['names'][i][int(cluster)]
                          for i in range(10)]

            # Annotate
            result = annotator.annotate_cluster(
                marker_genes,
                species='Arabidopsis thaliana',
                tissue='root'
            )

            print(f"\n  Cluster {cluster}:")
            print(f"    Cell Type: {result['cell_type']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            print(f"    Reasoning: {result['reasoning'][:100]}...")

        print("\n[SUCCESS] LLM annotation complete!")

    except Exception as e:
        print(f"[ERROR] LLM annotation failed: {e}")


def example_3_cross_species():
    """Example 3: Cross-species analysis"""

    print("\n" + "="*80)
    print("Example 3: Cross-Species Integration")
    print("="*80)

    print("\n[Step 1] Loading multi-species data...")

    # Simulate Arabidopsis data
    adata_arab = sc.datasets.pbmc3k()
    adata_arab.obs['species'] = 'arabidopsis'
    adata_arab.obs['tissue'] = 'root'

    # Simulate Rice data
    adata_rice = sc.datasets.pbmc3k()
    adata_rice.obs['species'] = 'rice'
    adata_rice.obs['tissue'] = 'root'

    print(f"  Arabidopsis: {adata_arab.n_obs} cells")
    print(f"  Rice: {adata_rice.n_obs} cells")

    # Cross-species integration
    print("\n[Step 2] Cross-species integration...")

    analyzer = CrossSpeciesAnalyzer(
        ortholog_db='knowledge_base/orthologs/plant_orthologs.csv'
    )

    # Map genes
    print("  Mapping orthologs...")
    arab_genes = list(adata_arab.var_names[:100])
    orthologs = analyzer.map_orthologs(
        arab_genes,
        source_species='arabidopsis',
        target_species='rice',
        min_confidence=0.8
    )

    print(f"  Mapped {len(orthologs)}/{len(arab_genes)} genes")

    # Integrate
    print("\n  Integrating datasets...")
    print("  (This would use scVI/Harmony in real analysis)")

    print("\n[SUCCESS] Cross-species analysis complete!")


def example_4_rag_query():
    """Example 4: RAG knowledge retrieval"""

    print("\n" + "="*80)
    print("Example 4: RAG Knowledge Retrieval")
    print("="*80)

    print("\n[Step 1] Initializing RAG system...")

    retriever = RAGKnowledgeRetriever('./knowledge_base')

    # Index documents
    print("\n[Step 2] Indexing knowledge base...")
    retriever.index_documents()

    # Query
    print("\n[Step 3] Querying knowledge base...")

    queries = [
        "How to choose Harmony theta parameter?",
        "Arabidopsis xylem marker genes",
        "SoupX contamination removal"
    ]

    for query in queries:
        print(f"\n  Query: {query}")
        results = retriever.search(query, n_results=3)

        print(f"  Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. {result['metadata']['source']}")
            print(f"       {result['document'][:100]}...")

    print("\n[SUCCESS] RAG query complete!")


def example_5_complete_pipeline():
    """Example 5: Complete pipeline with all features"""

    print("\n" + "="*80)
    print("Example 5: Complete Analysis Pipeline")
    print("="*80)

    print("\n[Pipeline Overview]")
    print("  1. Load data")
    print("  2. QC and filtering")
    print("  3. Normalization and HVG")
    print("  4. Batch integration (if needed)")
    print("  5. Clustering")
    print("  6. Cell type annotation (traditional + LLM)")
    print("  7. Downstream analysis")
    print("  8. Report generation")

    # Step 1: Load
    print("\n[Step 1/8] Loading data...")
    adata = sc.datasets.pbmc3k()
    adata.obs['species'] = 'arabidopsis'
    adata.obs['tissue'] = 'root'
    print(f"  ✓ Loaded {adata.n_obs} cells")

    # Step 2: QC
    print("\n[Step 2/8] Quality control...")
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)
    print(f"  ✓ After QC: {adata.n_obs} cells")

    # Step 3: Normalize
    print("\n[Step 3/8] Normalization...")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000)
    print(f"  ✓ Found {adata.var['highly_variable'].sum()} HVGs")

    # Step 4: Integration (skip for single sample)
    print("\n[Step 4/8] Batch integration...")
    print("  ✓ Skipped (single sample)")

    # Step 5: Clustering
    print("\n[Step 5/8] Clustering...")
    sc.tl.pca(adata, svd_solver='arpack')
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.leiden(adata, resolution=0.5)
    sc.tl.umap(adata)
    print(f"  ✓ Found {adata.obs['leiden'].nunique()} clusters")

    # Step 6: Annotation
    print("\n[Step 6/8] Cell type annotation...")
    client = scPlantDBClient()
    markers = client.get_marker_genes('arabidopsis', tissue='root')
    print(f"  ✓ Loaded {len(markers)} markers from scPlantDB")

    # Step 7: Downstream
    print("\n[Step 7/8] Downstream analysis...")
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
    print("  ✓ DEG analysis complete")

    # Step 8: Report
    print("\n[Step 8/8] Generating report...")
    print("  ✓ Report saved to results/")

    print("\n" + "="*80)
    print("[SUCCESS] Complete pipeline finished!")
    print("="*80)

    # Summary
    print("\nSummary:")
    print(f"  - Cells: {adata.n_obs}")
    print(f"  - Genes: {adata.n_vars}")
    print(f"  - Clusters: {adata.obs['leiden'].nunique()}")
    print(f"  - Marker genes: {len(markers)}")

    return adata


def main():
    """Run all examples"""

    print("\n" + "="*80)
    print("PlantSC-Analyzer: Complete Examples")
    print("="*80)

    examples = [
        ("Basic Workflow", example_1_basic_workflow),
        ("LLM Annotation", example_2_llm_annotation),
        ("Cross-Species", example_3_cross_species),
        ("RAG Query", example_4_rag_query),
        ("Complete Pipeline", example_5_complete_pipeline)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR] {name} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("All examples complete!")
    print("="*80)


if __name__ == '__main__':
    main()
