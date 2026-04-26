#!/usr/bin/env python3
"""
Generate Project Statistics Report

Analyzes the codebase and generates comprehensive statistics.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import subprocess


def count_lines(filepath):
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0


def get_git_stats():
    """Get git statistics"""
    try:
        commits = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD']).decode().strip()
        contributors = subprocess.check_output(['git', 'log', '--format=%an']).decode().strip().split('\n')
        unique_contributors = len(set(contributors))
        return int(commits), unique_contributors
    except:
        return 0, 0


def analyze_codebase(root_dir):
    """Analyze codebase structure and statistics"""
    stats = {
        'files': defaultdict(int),
        'lines': defaultdict(int),
        'total_files': 0,
        'total_lines': 0,
        'directories': set()
    }

    extensions = {
        '.py': 'Python',
        '.nf': 'Nextflow',
        '.md': 'Markdown',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.csv': 'CSV',
        '.sh': 'Shell',
        '.r': 'R',
        '.R': 'R'
    }

    for root, dirs, files in os.walk(root_dir):
        # Skip .git directory
        if '.git' in root:
            continue

        stats['directories'].add(root)

        for file in files:
            filepath = Path(root) / file
            ext = filepath.suffix

            if ext in extensions:
                file_type = extensions[ext]
                stats['files'][file_type] += 1
                lines = count_lines(filepath)
                stats['lines'][file_type] += lines
                stats['total_files'] += 1
                stats['total_lines'] += lines

    return stats


def analyze_markers(markers_dir):
    """Analyze marker gene database"""
    marker_stats = {
        'species': defaultdict(lambda: defaultdict(int)),
        'total_markers': 0,
        'total_files': 0
    }

    for csv_file in Path(markers_dir).rglob('*.csv'):
        if csv_file.name == 'README.md':
            continue

        parts = csv_file.parts
        if 'markers' in parts:
            idx = parts.index('markers')
            if idx + 1 < len(parts):
                species = parts[idx + 1]
                tissue = csv_file.stem.replace('_markers', '')

                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    n_markers = len(df)
                    marker_stats['species'][species][tissue] = n_markers
                    marker_stats['total_markers'] += n_markers
                    marker_stats['total_files'] += 1
                except:
                    pass

    return marker_stats


def analyze_tests(tests_dir):
    """Analyze test coverage"""
    test_stats = {
        'test_files': 0,
        'test_functions': 0
    }

    for test_file in Path(tests_dir).glob('test_*.py'):
        test_stats['test_files'] += 1

        try:
            with open(test_file, 'r') as f:
                content = f.read()
                test_stats['test_functions'] += content.count('def test_')
        except:
            pass

    return test_stats


def generate_report(root_dir):
    """Generate comprehensive statistics report"""
    print("=" * 80)
    print("PlantSC-Analyzer Project Statistics Report")
    print("=" * 80)
    print()

    # Git statistics
    commits, contributors = get_git_stats()
    print("📊 Git Statistics")
    print("-" * 80)
    print(f"  Total commits: {commits}")
    print(f"  Contributors: {contributors}")
    print()

    # Codebase statistics
    stats = analyze_codebase(root_dir)
    print("📁 Codebase Statistics")
    print("-" * 80)
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total lines: {stats['total_lines']:,}")
    print(f"  Directories: {len(stats['directories'])}")
    print()

    print("  Files by type:")
    for file_type in sorted(stats['files'].keys()):
        count = stats['files'][file_type]
        lines = stats['lines'][file_type]
        print(f"    {file_type:12s}: {count:3d} files, {lines:6,d} lines")
    print()

    # Marker gene statistics
    markers_dir = Path(root_dir) / 'knowledge_base' / 'markers'
    if markers_dir.exists():
        marker_stats = analyze_markers(markers_dir)
        print("🧬 Marker Gene Database")
        print("-" * 80)
        print(f"  Total markers: {marker_stats['total_markers']}")
        print(f"  Total files: {marker_stats['total_files']}")
        print()

        for species, tissues in marker_stats['species'].items():
            print(f"  {species.capitalize()}:")
            for tissue, count in sorted(tissues.items()):
                print(f"    {tissue:15s}: {count:3d} markers")
        print()

    # Test statistics
    tests_dir = Path(root_dir) / 'tests'
    if tests_dir.exists():
        test_stats = analyze_tests(tests_dir)
        print("🧪 Test Coverage")
        print("-" * 80)
        print(f"  Test files: {test_stats['test_files']}")
        print(f"  Test functions: {test_stats['test_functions']}")
        print()

    # Documentation statistics
    docs_dir = Path(root_dir) / 'docs'
    if docs_dir.exists():
        doc_files = list(docs_dir.rglob('*.md'))
        print("📚 Documentation")
        print("-" * 80)
        print(f"  Documentation files: {len(doc_files)}")
        total_doc_lines = sum(count_lines(f) for f in doc_files)
        print(f"  Documentation lines: {total_doc_lines:,}")
        print()

    # Module statistics
    print("🔧 Module Statistics")
    print("-" * 80)

    scripts_dir = Path(root_dir) / 'scripts'
    if scripts_dir.exists():
        for step_dir in sorted(scripts_dir.glob('[0-9]*')):
            step_name = step_dir.name
            py_files = list(step_dir.glob('*.py'))
            if py_files:
                total_lines = sum(count_lines(f) for f in py_files)
                print(f"  {step_name:25s}: {len(py_files):2d} scripts, {total_lines:5,d} lines")

    print()

    # Nextflow modules
    workflows_dir = Path(root_dir) / 'workflows' / 'modules'
    if workflows_dir.exists():
        nf_files = list(workflows_dir.glob('*.nf'))
        print("⚙️  Nextflow Modules")
        print("-" * 80)
        print(f"  Total modules: {len(nf_files)}")
        for nf_file in sorted(nf_files):
            lines = count_lines(nf_file)
            print(f"    {nf_file.stem:20s}: {lines:4d} lines")
        print()

    print("=" * 80)
    print("Report generated successfully!")
    print("=" * 80)


if __name__ == '__main__':
    root_dir = Path(__file__).parent.parent.parent
    generate_report(root_dir)
