#!/usr/bin/env python3
"""
LLM-Assisted Cell Type Annotation

Uses Large Language Models (OpenAI GPT-4, Anthropic Claude) to assist
with cell type annotation based on marker gene expression.

Based on: Assessing GPT-4 for cell type annotation in single-cell RNA-seq analysis
Nature Methods, 2024. DOI: 10.1038/s41592-024-02235-4
"""

import argparse
import sys
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

try:
    import scanpy as sc
except ImportError:
    print("[ERROR] scanpy not installed. Run: pip install scanpy")
    sys.exit(1)


class LLMAnnotator:
    """LLM-assisted cell type annotation"""

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        provider: str = "openai"
    ):
        """
        Initialize LLM annotator

        Args:
            model: Model name (gpt-4, gpt-3.5-turbo, claude-3-opus, etc.)
            api_key: API key (if None, reads from environment)
            provider: LLM provider (openai, anthropic)
        """
        self.model = model
        self.provider = provider

        if provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                print("[ERROR] openai package not installed. Run: pip install openai")
                sys.exit(1)

        elif provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("[ERROR] anthropic package not installed. Run: pip install anthropic")
                sys.exit(1)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def annotate_cluster(
        self,
        marker_genes: List[str],
        expression_values: Optional[Dict[str, float]] = None,
        species: str = "Arabidopsis thaliana",
        tissue: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Annotate a single cluster using LLM

        Args:
            marker_genes: List of marker genes (top DEGs)
            expression_values: Optional dict of gene -> expression value
            species: Plant species
            tissue: Tissue type (e.g., root, leaf)
            context: Additional context

        Returns:
            Dict with cell_type, confidence, reasoning
        """
        # Build prompt
        prompt = self._build_annotation_prompt(
            marker_genes,
            expression_values,
            species,
            tissue,
            context
        )

        # Query LLM
        response = self._query_llm(prompt)

        # Parse response
        result = self._parse_annotation_response(response)

        return result

    def annotate_all_clusters(
        self,
        adata,
        cluster_key: str = 'leiden',
        n_genes: int = 20,
        species: str = "Arabidopsis thaliana",
        tissue: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Annotate all clusters in AnnData object

        Args:
            adata: AnnData object
            cluster_key: Key for cluster labels
            n_genes: Number of top marker genes per cluster
            species: Plant species
            tissue: Tissue type

        Returns:
            DataFrame with annotations
        """
        print(f"[INFO] Annotating {adata.obs[cluster_key].nunique()} clusters...")

        # Find marker genes for each cluster
        sc.tl.rank_genes_groups(adata, cluster_key, method='wilcoxon')

        annotations = []

        for cluster in adata.obs[cluster_key].cat.categories:
            print(f"[INFO] Annotating cluster {cluster}...")

            # Get top marker genes
            marker_genes = self._get_top_markers(adata, cluster, n_genes)

            # Get expression values
            expression_values = self._get_expression_values(adata, cluster, marker_genes)

            # Annotate
            result = self.annotate_cluster(
                marker_genes,
                expression_values,
                species,
                tissue
            )

            annotations.append({
                'cluster': cluster,
                'cell_type': result['cell_type'],
                'confidence': result['confidence'],
                'reasoning': result['reasoning'],
                'marker_genes': ', '.join(marker_genes[:10])
            })

        return pd.DataFrame(annotations)

    def _build_annotation_prompt(
        self,
        marker_genes: List[str],
        expression_values: Optional[Dict[str, float]],
        species: str,
        tissue: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build annotation prompt for LLM"""

        prompt = f"""You are an expert in plant single-cell RNA-seq analysis.
Your task is to identify the cell type based on marker gene expression.

Species: {species}
"""

        if tissue:
            prompt += f"Tissue: {tissue}\n"

        if context:
            prompt += f"Context: {context}\n"

        prompt += f"\nTop marker genes (highly expressed in this cluster):\n"

        if expression_values:
            for gene in marker_genes[:20]:
                expr = expression_values.get(gene, 'N/A')
                if isinstance(expr, float):
                    prompt += f"- {gene} (log2FC: {expr:.2f})\n"
                else:
                    prompt += f"- {gene}\n"
        else:
            for gene in marker_genes[:20]:
                prompt += f"- {gene}\n"

        prompt += """
Based on these marker genes, please:
1. Identify the most likely cell type
2. Provide a confidence score (0-1)
3. Explain your reasoning

Format your response as:
Cell Type: [cell type name]
Confidence: [0-1]
Reasoning: [brief explanation]
"""

        return prompt

    def _query_llm(self, prompt: str) -> str:
        """Query LLM with prompt"""

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in plant biology and single-cell RNA-seq analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

    def _parse_annotation_response(self, response: str) -> Dict:
        """Parse LLM response"""

        lines = response.strip().split('\n')

        cell_type = "Unknown"
        confidence = 0.5
        reasoning = ""

        for line in lines:
            line = line.strip()

            if line.startswith("Cell Type:"):
                cell_type = line.replace("Cell Type:", "").strip()

            elif line.startswith("Confidence:"):
                conf_str = line.replace("Confidence:", "").strip()
                try:
                    confidence = float(conf_str)
                except:
                    confidence = 0.5

            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()

        return {
            'cell_type': cell_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'raw_response': response
        }

    def _get_top_markers(self, adata, cluster, n_genes: int) -> List[str]:
        """Get top marker genes for a cluster"""

        cluster_idx = list(adata.obs[adata.uns['rank_genes_groups']['params']['groupby']].cat.categories).index(str(cluster))

        genes = []
        for i in range(min(n_genes, len(adata.uns['rank_genes_groups']['names']))):
            gene = adata.uns['rank_genes_groups']['names'][i][cluster_idx]
            genes.append(gene)

        return genes

    def _get_expression_values(self, adata, cluster, genes: List[str]) -> Dict[str, float]:
        """Get expression values (log2FC) for genes"""

        cluster_key = adata.uns['rank_genes_groups']['params']['groupby']
        cluster_idx = list(adata.obs[cluster_key].cat.categories).index(str(cluster))

        values = {}
        for gene in genes:
            try:
                gene_idx = list(adata.var_names).index(gene)
                logfc = adata.uns['rank_genes_groups']['logfoldchanges'][gene_idx][cluster_idx]
                values[gene] = logfc
            except:
                values[gene] = None

        return values


def main():
    parser = argparse.ArgumentParser(description='LLM-Assisted Cell Type Annotation')
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--output', required=True, help='Output annotation CSV')
    parser.add_argument('--cluster_key', default='leiden', help='Cluster key in adata.obs')
    parser.add_argument('--n_genes', type=int, default=20, help='Number of marker genes')
    parser.add_argument('--species', default='Arabidopsis thaliana', help='Plant species')
    parser.add_argument('--tissue', help='Tissue type')
    parser.add_argument('--model', default='gpt-4', help='LLM model')
    parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'],
                       help='LLM provider')
    parser.add_argument('--api_key', help='API key (or set via environment)')

    args = parser.parse_args()

    # Load data
    print(f"[INFO] Loading {args.input}...")
    adata = sc.read_h5ad(args.input)

    # Initialize annotator
    print(f"[INFO] Initializing LLM annotator ({args.provider}/{args.model})...")
    annotator = LLMAnnotator(
        model=args.model,
        api_key=args.api_key,
        provider=args.provider
    )

    # Annotate
    annotations = annotator.annotate_all_clusters(
        adata,
        cluster_key=args.cluster_key,
        n_genes=args.n_genes,
        species=args.species,
        tissue=args.tissue
    )

    # Save
    annotations.to_csv(args.output, index=False)
    print(f"[SUCCESS] Saved annotations to {args.output}")

    # Print summary
    print("\n" + "="*60)
    print("Annotation Summary")
    print("="*60)
    print(annotations[['cluster', 'cell_type', 'confidence']].to_string(index=False))
    print("="*60)


if __name__ == '__main__':
    main()
