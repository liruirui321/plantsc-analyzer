"""
PlantSC Interactive Agent

交互式单细胞分析 Agent，提供：
1. 参数推荐
2. 质量检查
3. 结果解读
4. 知识库查询
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from knowledge_retriever import KnowledgeRetriever
from parameter_recommender import ParameterRecommender
from report_generator import ReportGenerator


class PlantSCAgent:
    """植物单细胞分析交互式 Agent"""

    def __init__(self, config_path: str):
        self.console = Console()
        self.config = self.load_config(config_path)
        self.knowledge = KnowledgeRetriever()
        self.recommender = ParameterRecommender()
        self.reporter = ReportGenerator()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

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
        self.console.print(banner, style="bold green")

    def interactive_qc(self, qc_metrics: Dict[str, Any]) -> bool:
        """交互式质控检查"""
        self.console.print("\n[bold cyan]📊 Step 1: Quality Control Results[/bold cyan]\n")

        # 显示 QC 指标
        table = Table(title="QC Metrics Summary")
        table.add_column("Sample", style="cyan")
        table.add_column("Cells", style="magenta")
        table.add_column("Genes/Cell", style="green")
        table.add_column("Alignment Rate", style="yellow")
        table.add_column("Status", style="bold")

        for sample, metrics in qc_metrics.items():
            status = "✅ Pass" if metrics['pass'] else "❌ Fail"
            table.add_row(
                sample,
                str(metrics['n_cells']),
                str(metrics['median_genes']),
                f"{metrics['alignment_rate']:.1f}%",
                status
            )

        self.console.print(table)

        # 询问用户
        if not all(m['pass'] for m in qc_metrics.values()):
            self.console.print("\n[bold red]⚠️  Some samples failed QC![/bold red]")
            self.console.print("Recommendation: Re-sequence failed samples or adjust thresholds")

            proceed = Confirm.ask("\nDo you want to proceed anyway?", default=False)
            return proceed
        else:
            self.console.print("\n[bold green]✅ All samples passed QC![/bold green]")
            return True

    def recommend_filter_params(self, data_stats: Dict[str, Any]) -> Dict[str, Any]:
        """推荐过滤参数"""
        self.console.print("\n[bold cyan]🔍 Step 2: Filter Parameter Recommendation[/bold cyan]\n")

        # 使用推荐引擎
        recommended = self.recommender.recommend_qc_params(data_stats)

        # 显示推荐参数
        panel = Panel(
            f"""
[bold]Recommended Parameters:[/bold]

• min_genes: {recommended['min_genes']} (based on gene count distribution)
• max_genes: {recommended['max_genes']} (exclude potential doublets)
• mito_threshold: {recommended['mito_threshold']}% (mitochondrial content)
• doublet_threshold: {recommended['doublet_threshold']} (Scrublet score)

[dim]Rationale: {recommended['rationale']}[/dim]
            """,
            title="Parameter Recommendation",
            border_style="green"
        )
        self.console.print(panel)

        # 询问用户
        choice = Prompt.ask(
            "\nAccept these parameters?",
            choices=["y", "n", "edit"],
            default="y"
        )

        if choice == "y":
            return recommended
        elif choice == "edit":
            return self.edit_params(recommended)
        else:
            return self.config['qc']

    def edit_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """编辑参数"""
        self.console.print("\n[bold]Edit Parameters:[/bold]")

        edited = {}
        for key, value in params.items():
            if key == 'rationale':
                continue
            new_value = Prompt.ask(f"{key}", default=str(value))
            edited[key] = type(value)(new_value)

        return edited

    def recommend_resolution(self, clustering_metrics: Dict[str, Any]) -> float:
        """推荐聚类 resolution"""
        self.console.print("\n[bold cyan]🎯 Step 4: Clustering Resolution Selection[/bold cyan]\n")

        # 显示不同 resolution 的结果
        table = Table(title="Clustering Results at Different Resolutions")
        table.add_column("Resolution", style="cyan")
        table.add_column("N Clusters", style="magenta")
        table.add_column("Silhouette", style="green")
        table.add_column("Modularity", style="yellow")

        for res, metrics in clustering_metrics.items():
            table.add_row(
                str(res),
                str(metrics['n_clusters']),
                f"{metrics['silhouette']:.3f}",
                f"{metrics['modularity']:.3f}"
            )

        self.console.print(table)

        # 推荐最佳 resolution
        best_res = self.recommender.recommend_resolution(clustering_metrics)
        self.console.print(f"\n[bold green]✨ Recommended resolution: {best_res}[/bold green]")

        # 询问用户
        choice = Prompt.ask(
            "\nSelect resolution",
            default=str(best_res)
        )

        return float(choice)

    def confirm_annotation(self, annotation_results: Dict[str, Any]) -> bool:
        """确认细胞类型注释"""
        self.console.print("\n[bold cyan]🏷️  Step 5: Cell Type Annotation Results[/bold cyan]\n")

        # 显示注释结果
        table = Table(title="Annotated Cell Types")
        table.add_column("Cluster", style="cyan")
        table.add_column("Cell Type", style="magenta")
        table.add_column("Confidence", style="green")
        table.add_column("N Cells", style="yellow")
        table.add_column("Top Markers", style="blue")

        for cluster, info in annotation_results.items():
            table.add_row(
                str(cluster),
                info['cell_type'],
                f"{info['confidence']:.2f}",
                str(info['n_cells']),
                ", ".join(info['top_markers'][:3])
            )

        self.console.print(table)

        # 询问用户
        return Confirm.ask("\nDo these annotations look correct?", default=True)

    def run(self):
        """运行交互式分析流程"""
        self.print_banner()

        # 显示项目信息
        self.console.print(f"\n[bold]Project:[/bold] {self.config['project_name']}")
        self.console.print(f"[bold]Species:[/bold] {self.config['species']}")
        self.console.print(f"[bold]Tissue:[/bold] {self.config['tissue']}")
        self.console.print(f"[bold]Samples:[/bold] {len(self.config['samples'])}\n")

        # 确认开始
        if not Confirm.ask("Start analysis?", default=True):
            self.console.print("[yellow]Analysis cancelled.[/yellow]")
            return

        # TODO: 集成 Nextflow 执行
        self.console.print("\n[bold green]🚀 Launching Nextflow pipeline...[/bold green]")
        self.console.print("[dim]This is a placeholder. Full integration coming soon.[/dim]")


def main():
    parser = argparse.ArgumentParser(description="PlantSC Interactive Agent")
    parser.add_argument('--config', type=str, required=True, help='Path to config YAML')
    parser.add_argument('--mode', type=str, default='interactive',
                       choices=['interactive', 'auto'],
                       help='Run mode: interactive or automatic')

    args = parser.parse_args()

    agent = PlantSCAgent(args.config)
    agent.run()


if __name__ == '__main__':
    main()
