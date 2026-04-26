#!/usr/bin/env python3
"""
PlantSC Interactive Agent

交互式单细胞分析 Agent，提供：
1. 参数推荐
2. 质量检查
3. 结果解读
4. 知识库查询
5. 报告生成
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import scanpy as sc

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[WARNING] rich not installed. Install with: pip install rich")

from knowledge_retriever import KnowledgeRetriever
from parameter_recommender import ParameterRecommender
from report_generator import ReportGenerator


class PlantSCAgent:
    """植物单细胞分析交互式 Agent"""

    def __init__(self, config_path: str = None):
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

        self.config = self.load_config(config_path) if config_path else {}
        self.knowledge = KnowledgeRetriever()
        self.recommender = ParameterRecommender()
        self.reporter = ReportGenerator()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def print(self, text: str, style: str = None):
        """统一的打印接口"""
        if self.console:
            self.console.print(text, style=style)
        else:
            print(text)

    def print_banner(self):
        """打印欢迎信息"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌱 PlantSC-Analyzer Interactive Agent                  ║
║                                                           ║
║   Your AI assistant for plant single-cell analysis       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.print(banner, style="bold green")

    def analyze_and_recommend(self, adata_path: str) -> Dict[str, Any]:
        """
        分析数据并生成推荐参数

        Args:
            adata_path: AnnData 文件路径

        Returns:
            推荐参数字典
        """
        self.print("\n[INFO] Loading data...", style="cyan")
        adata = sc.read_h5ad(adata_path)

        self.print(f"[INFO] Loaded: {adata.n_obs} cells, {adata.n_vars} genes", style="green")

        # 生成推荐
        recommendations = self.recommender.recommend_all_params(adata)

        # 打印推荐
        self.recommender.print_recommendations(recommendations)

        return recommendations

    def query_markers(self, species: str, tissue: str = None,
                     cell_type: str = None) -> List[Dict]:
        """
        查询 Marker 基因

        Args:
            species: 物种名称
            tissue: 组织类型（可选）
            cell_type: 细胞类型（可选）

        Returns:
            Marker 基因列表
        """
        self.print(f"\n[INFO] Querying markers for {species}...", style="cyan")

        markers = self.knowledge.get_markers(species, tissue, cell_type)

        if markers:
            self.print(f"[INFO] Found {len(markers)} markers", style="green")

            # 显示前 10 个
            self.print("\nTop 10 markers:")
            for i, marker in enumerate(markers[:10], 1):
                self.print(f"  {i}. {marker.get('gene_symbol')} - {marker.get('cell_type')} "
                          f"(confidence: {marker.get('confidence', 'N/A')})")
        else:
            self.print("[WARNING] No markers found", style="yellow")

        return markers

    def generate_report(self, results_dir: str, output_path: str):
        """
        生成分析报告

        Args:
            results_dir: 结果目录
            output_path: 输出报告路径
        """
        self.print("\n[INFO] Generating analysis report...", style="cyan")

        # 收集结果
        collected = self.reporter.collect_pipeline_results(results_dir)

        # 生成报告
        project_info = self.config.get('project', {
            'project_name': 'PlantSC Analysis',
            'species': 'arabidopsis',
            'tissue': 'root'
        })

        # TODO: 从结果中提取实际指标
        metrics = {
            'Total Cells': 'N/A',
            'Total Genes': 'N/A',
            'Cell Types': 'N/A',
            'Clusters': 'N/A'
        }

        steps = []
        results = collected
        recommendations = []

        self.reporter.generate_html_report(
            project_info, metrics, steps, results, recommendations, output_path
        )

        self.print(f"[INFO] Report saved to: {output_path}", style="green")

    def interactive_mode(self):
        """交互式模式"""
        self.print_banner()

        while True:
            self.print("\n" + "="*60)
            self.print("What would you like to do?")
            self.print("  1. Analyze data and get parameter recommendations")
            self.print("  2. Query marker genes")
            self.print("  3. Generate analysis report")
            self.print("  4. Exit")
            self.print("="*60)

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                adata_path = input("Enter path to h5ad file: ").strip()
                if Path(adata_path).exists():
                    self.analyze_and_recommend(adata_path)
                else:
                    self.print(f"[ERROR] File not found: {adata_path}", style="red")

            elif choice == '2':
                species = input("Enter species (e.g., arabidopsis): ").strip()
                tissue = input("Enter tissue (optional, press Enter to skip): ").strip() or None
                cell_type = input("Enter cell type (optional, press Enter to skip): ").strip() or None
                self.query_markers(species, tissue, cell_type)

            elif choice == '3':
                results_dir = input("Enter results directory: ").strip()
                output_path = input("Enter output report path (e.g., report.html): ").strip()
                if Path(results_dir).exists():
                    self.generate_report(results_dir, output_path)
                else:
                    self.print(f"[ERROR] Directory not found: {results_dir}", style="red")

            elif choice == '4':
                self.print("\nGoodbye! 🌱", style="bold green")
                break

            else:
                self.print("[ERROR] Invalid choice. Please enter 1-4.", style="red")


def main():
    parser = argparse.ArgumentParser(description="PlantSC Interactive Agent")
    parser.add_argument('--config', type=str, default=None, help='Path to config YAML')
    parser.add_argument('--mode', type=str, default='interactive',
                       choices=['interactive', 'auto'],
                       help='Run mode: interactive or automatic')
    parser.add_argument('--analyze', type=str, default=None,
                       help='Path to h5ad file for direct analysis')
    parser.add_argument('--query_markers', type=str, default=None,
                       help='Query markers for species (e.g., arabidopsis)')
    parser.add_argument('--report', type=str, default=None,
                       help='Generate report from results directory')
    parser.add_argument('--output', type=str, default='report.html',
                       help='Output path for report')

    args = parser.parse_args()

    agent = PlantSCAgent(args.config)

    if args.analyze:
        agent.analyze_and_recommend(args.analyze)
    elif args.query_markers:
        agent.query_markers(args.query_markers)
    elif args.report:
        agent.generate_report(args.report, args.output)
    else:
        agent.interactive_mode()


if __name__ == '__main__':
    main()
