# Test Suite

This directory contains the test suite for the Phone Management System.

## Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest fixtures and configuration
├── generators.py            # Hypothesis test data generators
├── test_inventory.py        # Inventory module tests
├── test_sales.py            # Sales module tests
├── test_repairs.py          # Repair module tests
├── test_financial.py        # Financial calculation tests
├── test_transactions.py     # Transaction atomicity tests
├── test_validation.py       # Validation tests
├── test_security.py         # Security tests
├── test_audit.py            # Audit logging tests
├── test_backup.py           # Backup/restore tests
├── test_dashboard.py        # Dashboard statistics tests
└── test_integration.py      # Integration tests
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Property-based tests only
pytest -m property

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Security tests
pytest -m security

# Financial tests
pytest -m financial
```

### Run Specific Test File

```bash
pytest tests/test_inventory.py -v
```

### Run with Coverage

```bash
pytest --cov=modules --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -vv
```

### Run Specific Test Function

```bash
pytest tests/test_inventory.py::test_inventory_non_negative -v
```

## Hypothesis Profiles

The test suite uses Hypothesis for property-based testing with different profiles:

- **default**: 100 examples per test (normal development)
- **dev**: 50 examples (faster feedback during development)
- **ci**: 200 examples (thorough testing in CI/CD)
- **debug**: 10 examples (quick debugging)

Set the profile using environment variable:

```bash
HYPOTHESIS_PROFILE=dev pytest
```

## Test Markers

Tests are marked with categories for easy filtering:

- `@pytest.mark.property` - Property-based tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.financial` - Financial calculation tests

## Writing Tests

### Property-Based Test Example

```python
from hypothesis import given
import tests.generators as gen

@pytest.mark.property
def test_inventory_non_negative(test_db):
    """
    **Feature: data-integrity-testing, Property 1: Non-negative inventory quantities**
    **Validates: Requirements 1.1**
    """
    @given(item=gen.inventory_item())
    def check_non_negative(item):
        from modules.models import add_inventory_item
        result = add_inventory_item(**item)
        assert result is True
        
        # Verify quantity is non-negative
        from modules.db import get_conn
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory WHERE sku = ?", (item['sku'],))
        qty = c.fetchone()[0]
        conn.close()
        assert qty >= 0
    
    check_non_negative()
```

### Unit Test Example

```python
@pytest.mark.unit
def test_zero_inventory_prevention(test_db, sample_inventory_item):
    """Test that sales are rejected when inventory is zero"""
    from modules.models import add_inventory_item, create_sale
    
    # Add item with zero quantity
    item = sample_inventory_item.copy()
    item['quantity'] = 0
    add_inventory_item(**item)
    
    # Attempt to sell
    result = create_sale("Customer", [(1, 1, 100.0, 50.0)])
    
    # Should fail
    assert result is None
```

## Test Database

Each test function gets a fresh, isolated test database via the `test_db` fixture. This ensures:

- No test pollution
- Parallel test execution safety
- Clean state for each test

The test database is automatically cleaned up after tests complete.
