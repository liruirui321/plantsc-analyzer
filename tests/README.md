# Test Configuration

## Running Tests

### Install test dependencies
```bash
pip install pytest pytest-cov
```

### Run all tests
```bash
# From project root
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=scripts --cov=agent --cov-report=html
```

### Run specific test files
```bash
# Test I/O utilities
pytest tests/test_io_utils.py -v

# Test parameter recommender
pytest tests/test_parameter_recommender.py -v

# Test knowledge retriever
pytest tests/test_knowledge_retriever.py -v

# Test integration
pytest tests/test_integration.py -v
```

### Run with markers
```bash
# Run only fast tests
pytest tests/ -v -m "not slow"

# Run only integration tests
pytest tests/ -v -m "integration"
```

## Test Structure

```
tests/
├── test_io_utils.py              # I/O utility tests
├── test_parameter_recommender.py # Parameter recommendation tests
├── test_knowledge_retriever.py   # Knowledge retrieval tests
├── test_integration.py           # End-to-end integration tests
└── test_data/                    # Test data files
    └── sample.h5ad               # Sample dataset
```

## Test Coverage Goals

- **Unit tests**: >80% coverage
- **Integration tests**: All major workflows
- **Edge cases**: Error handling and validation

## Writing New Tests

### Test naming convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Example test structure
```python
import pytest

@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    return create_sample()

def test_function_name(sample_data):
    """Test description"""
    result = function_to_test(sample_data)
    assert result == expected_value
```

## Continuous Integration

Tests are automatically run on:
- Push to main branch
- Pull requests
- Scheduled daily runs

## Known Issues

1. Some tests require R environment for SoupX
2. Large dataset tests may be slow
3. GPU tests require CUDA

## Test Data

Test data is stored in `tests/test_data/`:
- Small synthetic datasets for unit tests
- Sample real data for integration tests
- Marker gene databases for knowledge retrieval tests
