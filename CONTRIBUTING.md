# Contributing to Phone Store Management System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Phone-Store-Management-System.git
   cd Phone-Store-Management-System
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Initialize the database**:
   ```bash
   python db_init.py
   ```

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-export-functionality`
- `bugfix/fix-inventory-calculation`
- `enhancement/improve-ui-responsiveness`

### 2. Make Your Changes

- Write clean, readable code
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_inventory.py

# Run with coverage
pytest --cov=modules --cov=controllers
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add: Export functionality for customer data"
```

Commit message format:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for updates to existing features
- `Refactor:` for code refactoring
- `Docs:` for documentation changes
- `Test:` for test additions/changes

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Detailed description of what was changed and why
- Screenshots (if UI changes)
- Reference to any related issues

## 📝 Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

Example:
```python
def calculate_total_revenue(sales_data: list) -> float:
    """
    Calculate total revenue from sales data.
    
    Args:
        sales_data: List of sale dictionaries with 'amount' key
        
    Returns:
        Total revenue as float
    """
    return sum(sale['amount'] for sale in sales_data)
```

### UI Code Style

- Use consistent spacing and alignment
- Follow existing UI patterns
- Test on different screen sizes
- Ensure accessibility (keyboard navigation, clear labels)

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Include both unit tests and integration tests
- Use property-based testing for data validation
- Aim for 80%+ code coverage

Example test:
```python
def test_add_inventory_item():
    """Test adding a new inventory item."""
    result = add_inventory_item(
        sku="TEST001",
        name="Test Phone",
        quantity=10,
        buy_price=100.0,
        sell_price=150.0,
        category="Phones"
    )
    assert result is True
    
    # Verify item was added
    item = get_inventory_item_by_sku("TEST001")
    assert item is not None
    assert item['name'] == "Test Phone"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_inventory.py::test_add_inventory_item

# Run with coverage report
pytest --cov=modules --cov-report=html
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Include parameter types and return types
- Explain complex algorithms or business logic
- Update README.md for new features

### User Documentation

- Update user guides for UI changes
- Add screenshots for new features
- Keep documentation clear and concise
- Test instructions with fresh eyes

## 🐛 Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Screenshots**: If applicable
6. **Environment**:
   - OS (Windows/macOS/Linux)
   - Python version
   - Application version

## 💡 Feature Requests

When requesting features, include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Proposed Solution**: How you think it should work
4. **Alternatives**: Other solutions you've considered

## 🔍 Code Review Process

All contributions go through code review:

1. **Automated Checks**: Tests must pass
2. **Code Quality**: Code follows style guidelines
3. **Functionality**: Feature works as intended
4. **Documentation**: Changes are documented
5. **Testing**: Adequate test coverage

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] All tests pass (`pytest`)
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data (passwords, API keys) in code
- [ ] Branch is up to date with main

## 🤝 Community Guidelines

- Be respectful and constructive
- Help others learn and grow
- Give credit where credit is due
- Focus on the code, not the person
- Assume good intentions

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email maintainer directly

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

Thank you for contributing to Phone Store Management System! 🙏
