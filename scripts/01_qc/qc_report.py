#!/usr/bin/env python3
"""
QC Report Generator

Generates comprehensive HTML report summarizing QC results across all samples.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PlantSC QC Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c5f2d;
            border-bottom: 3px solid #2c5f2d;
            padding-bottom: 10px;
        }
        h2 {
            color: #4a7c59;
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #2c5f2d;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .pass {
            color: green;
            font-weight: bold;
        }
        .fail {
            color: red;
            font-weight: bold;
        }
        .warning {
            color: orange;
            font-weight: bold;
        }
        .metric-box {
            display: inline-block;
            padding: 15px;
            margin: 10px;
            background-color: #e8f5e9;
            border-radius: 5px;
            min-width: 200px;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c5f2d;
        }
        .plot-container {
            text-align: center;
            margin: 20px 0;
        }
        .plot-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 PlantSC-Analyzer QC Report</h1>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
        <p><strong>Total Samples:</strong> {{ n_samples }}</p>

        <h2>📊 Summary Statistics</h2>
        <div>
            <div class="metric-box">
                <div class="metric-label">Total Cells (Before)</div>
                <div class="metric-value">{{ total_cells_before | int }}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Total Cells (After)</div>
                <div class="metric-value">{{ total_cells_after | int }}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Retention Rate</div>
                <div class="metric-value">{{ retention_rate }}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Median Genes/Cell</div>
                <div class="metric-value">{{ median_genes | int }}</div>
            </div>
        </div>

        <h2>📋 Sample-wise QC Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>Sample ID</th>
                    <th>Cells Before</th>
                    <th>Cells After</th>
                    <th>Retention %</th>
                    <th>Median Genes</th>
                    <th>Median UMIs</th>
                    <th>Median Mito%</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for row in samples %}
                <tr>
                    <td>{{ row.sample_id }}</td>
                    <td>{{ row.cells_before | int }}</td>
                    <td>{{ row.cells_after | int }}</td>
                    <td>{{ row.retention_pct }}%</td>
                    <td>{{ row.median_genes | int }}</td>
                    <td>{{ row.median_counts | int }}</td>
                    <td>{{ row.median_mito_pct }}%</td>
                    <td class="{{ row.status_class }}">{{ row.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>📈 QC Metrics Distribution</h2>
        <div class="plot-container">
            <img src="qc_summary_plots.png" alt="QC Summary Plots">
        </div>

        <h2>✅ QC Criteria</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Threshold</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>Minimum Genes</td>
                <td>{{ qc_params.min_genes }}</td>
                <td>Cells with fewer genes are removed</td>
            </tr>
            <tr>
                <td>Maximum Genes</td>
                <td>{{ qc_params.max_genes }}</td>
                <td>Cells with more genes (potential doublets) are removed</td>
            </tr>
            <tr>
                <td>Mitochondrial %</td>
                <td>{{ qc_params.mito_threshold }}%</td>
                <td>Cells with higher mito% (dying cells) are removed</td>
            </tr>
            <tr>
                <td>Minimum Cells</td>
                <td>{{ qc_params.min_cells }}</td>
                <td>Genes expressed in fewer cells are removed</td>
            </tr>
        </table>

        <h2>💡 Recommendations</h2>
        <ul>
            {% for rec in recommendations %}
            <li>{{ rec }}</li>
            {% endfor %}
        </ul>

        <div class="footer">
            <p>Generated by PlantSC-Analyzer v0.1.0-alpha</p>
            <p>For questions or issues, visit: <a href="https://github.com/YOUR_USERNAME/plantsc-analyzer">GitHub</a></p>
        </div>
    </div>
</body>
</html>
"""


def generate_summary_plots(metrics_df: pd.DataFrame, output_path: str):
    """Generate summary plots for QC report"""

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('QC Metrics Summary Across Samples', fontsize=16)

    # 1. Cells before vs after
    x = np.arange(len(metrics_df))
    width = 0.35
    axes[0, 0].bar(x - width/2, metrics_df['cells_before'], width, label='Before', alpha=0.8)
    axes[0, 0].bar(x + width/2, metrics_df['cells_after'], width, label='After', alpha=0.8)
    axes[0, 0].set_xlabel('Sample')
    axes[0, 0].set_ylabel('Number of Cells')
    axes[0, 0].set_title('Cells Before/After Filtering')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')
    axes[0, 0].legend()

    # 2. Retention rate
    retention = (metrics_df['cells_after'] / metrics_df['cells_before'] * 100)
    axes[0, 1].bar(metrics_df['sample_id'], retention, color='skyblue', alpha=0.8)
    axes[0, 1].axhline(y=80, color='red', linestyle='--', label='80% threshold')
    axes[0, 1].set_xlabel('Sample')
    axes[0, 1].set_ylabel('Retention Rate (%)')
    axes[0, 1].set_title('Cell Retention Rate')
    axes[0, 1].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')
    axes[0, 1].legend()

    # 3. Median genes per cell
    axes[0, 2].bar(metrics_df['sample_id'], metrics_df['median_genes_per_cell'],
                   color='lightgreen', alpha=0.8)
    axes[0, 2].set_xlabel('Sample')
    axes[0, 2].set_ylabel('Median Genes per Cell')
    axes[0, 2].set_title('Median Genes per Cell')
    axes[0, 2].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')

    # 4. Median counts per cell
    axes[1, 0].bar(metrics_df['sample_id'], metrics_df['median_counts_per_cell'],
                   color='salmon', alpha=0.8)
    axes[1, 0].set_xlabel('Sample')
    axes[1, 0].set_ylabel('Median UMIs per Cell')
    axes[1, 0].set_title('Median UMIs per Cell')
    axes[1, 0].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')

    # 5. Median mito percentage
    axes[1, 1].bar(metrics_df['sample_id'], metrics_df['median_mito_pct'],
                   color='orange', alpha=0.8)
    axes[1, 1].axhline(y=5, color='red', linestyle='--', label='5% threshold')
    axes[1, 1].set_xlabel('Sample')
    axes[1, 1].set_ylabel('Median Mitochondrial %')
    axes[1, 1].set_title('Median Mitochondrial Content')
    axes[1, 1].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')
    axes[1, 1].legend()

    # 6. Genes before vs after
    axes[1, 2].bar(x - width/2, metrics_df['genes_before'], width, label='Before', alpha=0.8)
    axes[1, 2].bar(x + width/2, metrics_df['genes_after'], width, label='After', alpha=0.8)
    axes[1, 2].set_xlabel('Sample')
    axes[1, 2].set_ylabel('Number of Genes')
    axes[1, 2].set_title('Genes Before/After Filtering')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(metrics_df['sample_id'], rotation=45, ha='right')
    axes[1, 2].legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_recommendations(metrics_df: pd.DataFrame) -> list:
    """Generate QC recommendations based on metrics"""
    recommendations = []

    # Check retention rate
    low_retention = metrics_df[
        (metrics_df['cells_after'] / metrics_df['cells_before']) < 0.7
    ]
    if len(low_retention) > 0:
        recommendations.append(
            f"⚠️ {len(low_retention)} sample(s) have <70% cell retention. "
            f"Consider adjusting QC thresholds or checking sample quality."
        )

    # Check median genes
    low_genes = metrics_df[metrics_df['median_genes_per_cell'] < 500]
    if len(low_genes) > 0:
        recommendations.append(
            f"⚠️ {len(low_genes)} sample(s) have median genes/cell <500. "
            f"This may indicate low sequencing depth or poor sample quality."
        )

    # Check mito percentage
    high_mito = metrics_df[metrics_df['median_mito_pct'] > 10]
    if len(high_mito) > 0:
        recommendations.append(
            f"⚠️ {len(high_mito)} sample(s) have median mito% >10%. "
            f"This may indicate stressed or dying cells."
        )

    if len(recommendations) == 0:
        recommendations.append("✅ All samples passed QC with good metrics!")

    return recommendations


def main():
    parser = argparse.ArgumentParser(description='Generate QC summary report')
    parser.add_argument('--metrics', nargs='+', required=True,
                       help='Input metrics CSV files (one per sample)')
    parser.add_argument('--output', required=True, help='Output HTML report')
    parser.add_argument('--min_genes', type=int, default=200)
    parser.add_argument('--max_genes', type=int, default=6000)
    parser.add_argument('--mito_threshold', type=float, default=5.0)
    parser.add_argument('--min_cells', type=int, default=3)

    args = parser.parse_args()

    try:
        # Load all metrics
        metrics_list = []
        for metrics_file in args.metrics:
            df = pd.read_csv(metrics_file)
            metrics_list.append(df)

        metrics_df = pd.concat(metrics_list, ignore_index=True)

        print(f"[INFO] Loaded metrics for {len(metrics_df)} samples")

        # Generate summary plots
        output_dir = Path(args.output).parent
        plot_path = output_dir / 'qc_summary_plots.png'
        generate_summary_plots(metrics_df, str(plot_path))

        # Prepare data for template
        samples_data = []
        for _, row in metrics_df.iterrows():
            retention_pct = row['cells_after'] / row['cells_before'] * 100

            # Determine status
            if retention_pct >= 80 and row['median_genes_per_cell'] >= 500:
                status = '✅ PASS'
                status_class = 'pass'
            elif retention_pct >= 60:
                status = '⚠️ WARNING'
                status_class = 'warning'
            else:
                status = '❌ FAIL'
                status_class = 'fail'

            samples_data.append({
                'sample_id': row['sample_id'],
                'cells_before': row['cells_before'],
                'cells_after': row['cells_after'],
                'retention_pct': f"{retention_pct:.1f}",
                'median_genes': row['median_genes_per_cell'],
                'median_counts': row['median_counts_per_cell'],
                'median_mito_pct': f"{row['median_mito_pct']:.2f}",
                'status': status,
                'status_class': status_class
            })

        # Calculate summary statistics
        total_cells_before = metrics_df['cells_before'].sum()
        total_cells_after = metrics_df['cells_after'].sum()
        retention_rate = f"{total_cells_after / total_cells_before * 100:.1f}"
        median_genes = metrics_df['median_genes_per_cell'].median()

        # Generate recommendations
        recommendations = generate_recommendations(metrics_df)

        # Render HTML
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            n_samples=len(metrics_df),
            total_cells_before=total_cells_before,
            total_cells_after=total_cells_after,
            retention_rate=retention_rate,
            median_genes=median_genes,
            samples=samples_data,
            qc_params={
                'min_genes': args.min_genes,
                'max_genes': args.max_genes,
                'mito_threshold': args.mito_threshold,
                'min_cells': args.min_cells
            },
            recommendations=recommendations
        )

        # Write HTML report
        with open(args.output, 'w') as f:
            f.write(html_content)

        print(f"[INFO] QC report generated: {args.output}")
        print(f"[INFO] Summary plots saved: {plot_path}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
