# Contributing to PlantSC-Analyzer

Thank you for your interest in contributing to PlantSC-Analyzer! This document provides guidelines for contributing to the project.

---

## 🌟 Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues
- Include detailed description
- Provide reproducible example
- Specify environment (OS, Python version, etc.)

### 2. Suggest Features
- Open a GitHub Issue with "Feature Request" label
- Describe the use case
- Explain why it would be useful

### 3. Add Marker Genes
- Add to `knowledge_base/markers/`
- Follow CSV format
- Include references (PMID)
- Submit Pull Request

### 4. Improve Documentation
- Fix typos
- Add examples
- Translate to other languages
- Improve clarity

### 5. Submit Code
- Bug fixes
- New features
- Performance improvements
- Test coverage

---

## 🚀 Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/plantsc-analyzer.git
cd plantsc-analyzer
```

### 2. Set Up Development Environment

```bash
# Create conda environment
conda env create -f envs/environment.yml
conda activate plantsc

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## 📝 Contribution Guidelines

### Code Style

**Python**:
- Follow PEP 8
- Use Black for formatting: `black scripts/ agent/`
- Use type hints where appropriate
- Maximum line length: 100 characters

**Nextflow**:
- Use 4 spaces for indentation
- Clear process names
- Document parameters

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```bash
feat(qc): add support for custom QC thresholds
fix(cluster): resolve resolution parameter bug
docs(tutorial): add multi-sample integration example
```

### Testing

**Run tests before submitting**:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov=agent --cov-report=html

# Run specific test
pytest tests/test_io_utils.py -v
```

**Add tests for new features**:
- Unit tests for functions
- Integration tests for workflows
- Test edge cases

### Documentation

**Update documentation when**:
- Adding new features
- Changing parameters
- Modifying workflows

**Documentation locations**:
- User-facing: `docs/`
- Code comments: inline
- API reference: docstrings

---

## 🧬 Adding Marker Genes

### Format

Create CSV file in `knowledge_base/markers/{species}/{tissue}_markers.csv`:

```csv
gene_symbol,cell_type,confidence,reference,description
VND7,Xylem vessel,high,PMID:12345678,VASCULAR-RELATED NAC-DOMAIN 7
SHR,Endodermis,high,PMID:87654321,SHORT-ROOT - endodermis development
```

**Fields**:
- `gene_symbol`: Gene name (required)
- `cell_type`: Cell type (required)
- `confidence`: high/medium/low (required)
- `reference`: PMID or DOI (required)
- `description`: Brief description (optional)

### Validation

```bash
# Validate marker file
python scripts/utils/validate_markers.py knowledge_base/markers/arabidopsis/new_markers.csv
```

---

## 🔬 Adding New Methods

### 1. Create Script

```python
#!/usr/bin/env python3
"""
Brief description

Detailed description of what this script does.
"""

import argparse
import scanpy as sc

def main():
    parser = argparse.ArgumentParser(description="Your method")
    parser.add_argument('--input', required=True, help='Input h5ad file')
    parser.add_argument('--output', required=True, help='Output h5ad file')
    args = parser.parse_args()
    
    # Your implementation
    
if __name__ == '__main__':
    main()
```

### 2. Add Nextflow Module

```groovy
process YOUR_METHOD {
    publishDir "${params.outdir}/your_step", mode: 'copy'
    
    input:
    path input_h5ad
    
    output:
    path "output.h5ad"
    
    script:
    """
    python ${projectDir}/scripts/your_method.py \\
        --input ${input_h5ad} \\
        --output output.h5ad
    """
}
```

### 3. Add Tests

```python
def test_your_method():
    """Test your method"""
    # Create test data
    # Run method
    # Assert results
    pass
```

### 4. Update Documentation

- Add to `docs/user_guide.md`
- Add parameters to `configs/project_template.yaml`
- Update `README.md` if major feature

---

## 📚 Adding Literature

### 1. Add to Literature Database

Edit `knowledge_base/papers/LITERATURE_DATABASE.md`:

```markdown
**Your Paper Title**
- **Authors**: Author A, Author B
- **Journal**: Journal Name, Year
- **PMID**: 12345678
- **DOI**: 10.xxxx/xxxxx
- **Key Points**:
  - Point 1
  - Point 2
- **File**: `papers/category/Author_Year_Title.pdf`
```

### 2. Extract Marker Genes

If paper contains marker genes:
1. Extract to CSV format
2. Add to appropriate marker file
3. Reference PMID in CSV

---

## 🧪 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### 2. Submit PR

```bash
git push origin feature/your-feature-name
```

Then open Pull Request on GitHub with:
- Clear title
- Description of changes
- Related issues (if any)
- Screenshots (if UI changes)

### 3. Review Process

- Maintainers will review
- Address feedback
- CI tests must pass
- At least 1 approval required

### 4. After Merge

- Delete your branch
- Pull latest main
- Celebrate! 🎉

---

## 🐛 Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With parameters '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.10]
- PlantSC-Analyzer version: [e.g., 0.1.0-alpha]

**Additional context**
Any other relevant information.
```

---

## 💡 Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other relevant information.
```

---

## 📞 Contact

- **GitHub Issues**: https://github.com/liruirui321/plantsc-analyzer/issues
- **Maintainer**: Cherry

---

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behavior**:
- Using welcoming language
- Being respectful
- Accepting constructive criticism
- Focusing on what's best for the community

**Unacceptable behavior**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations may result in temporary or permanent ban from the project.

---

## 🙏 Acknowledgments

Thank you to all contributors who help make PlantSC-Analyzer better!

### Contributors

- Cherry - Project creator and maintainer
- [Your name here] - Contributor

---

**Happy Contributing!** 🌱
