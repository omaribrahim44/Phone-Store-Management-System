# Design Document

## Overview

This design establishes a comprehensive testing framework and data integrity improvements for the Phone Management System. The approach combines property-based testing (PBT) to verify universal correctness properties with unit tests for specific scenarios. We'll also implement validation layers, improve transaction handling, and enhance security measures.

The design follows a layered architecture:
- **Validation Layer**: Input validation before data reaches the database
- **Transaction Layer**: Ensures atomic operations with proper rollback
- **Testing Layer**: Property-based and unit tests for all critical operations
- **Audit Layer**: Enhanced logging for all state changes

## Architecture

### Current Architecture
```
UI Layer (ttkbootstrap)
    ↓
Controllers (repair_controller, inventory_controller, etc.)
    ↓
Models (modules/models.py)
    ↓
Database Layer (modules/db.py)
    ↓
SQLite Database
```

### Enhanced Architecture
```
UI Layer (ttkbootstrap)
    ↓
Controllers (with validation)
    ↓
Validators (new: modules/validators.py - enhanced)
    ↓
Models (with transaction management)
    ↓
Database Layer (with connection pooling)
    ↓
SQLite Database
    ↓
Audit Logger (enhanced)
```

## Components and Interfaces

### 1. Enhanced Validators Module

**Location**: `modules/validators.py`

**Purpose**: Centralized validation for all input data

**Key Functions**:
- `validate_price(value: float) -> ValidationResult`: Ensures non-negative prices
- `validate_quantity(value: int) -> ValidationResult`: Ensures non-negative quantities
- `validate_phone(phone: str) -> ValidationResult`: Validates and normalizes phone numbers
- `validate_sku(sku: str) -> ValidationResult`: Ensures unique, non-empty SKUs
- `validate_password(password: str) -> ValidationResult`: Enforces password complexity
- `validate_email(email: str) -> ValidationResult`: Validates email format

**ValidationResult Structure**:
```python
@dataclass
class ValidationResult:
    valid: bool
    normalized_value: Any
    error_message: Optional[str]
```

### 2. Transaction Manager

**Location**: `modules/transaction_manager.py`

**Purpose**: Ensures atomic database operations with proper rollback

**Key Functions**:
- `@transactional` decorator: Wraps functions in transaction with auto-rollback
- `execute_in_transaction(func, *args, **kwargs)`: Executes function atomically
- `rollback_on_error(conn)`: Handles rollback on exceptions

### 3. Enhanced Models with Validation

**Modifications to**: `modules/models.py`

**Changes**:
- Add validation calls before database operations
- Wrap multi-step operations in transactions
- Return detailed error information instead of boolean
- Add proper exception handling with rollback

### 4. Password Security Enhancement

**Location**: `modules/security.py`

**Purpose**: Improve password hashing and verification

**Key Functions**:
- `hash_password_secure(plain: str) -> str`: Uses bcrypt or argon2
- `verify_password_secure(stored: str, plain: str) -> bool`: Constant-time comparison
- `check_password_strength(password: str) -> StrengthResult`: Validates complexity

### 5. Test Infrastructure

**Location**: `tests/` directory structure

**Structure**:
```
tests/
├── __init__.py
├── conftest.py (pytest fixtures)
├── test_inventory.py (inventory property tests)
├── test_sales.py (sales property tests)
├── test_repairs.py (repair property tests)
├── test_financial.py (financial calculation tests)
├── test_transactions.py (transaction atomicity tests)
├── test_validation.py (validation tests)
├── test_security.py (password security tests)
└── generators.py (test data generators for PBT)
```

## Data Models

### Enhanced Inventory Model
```python
@dataclass
class InventoryItem:
    item_id: int
    sku: str  # Must be unique, non-empty
    name: str  # Must be non-empty
    category: str
    description: str
    quantity: int  # Must be >= 0
    buy_price: float  # Must be >= 0
    sell_price: float  # Must be >= 0
    barcode: Optional[str]
    
    def validate(self) -> ValidationResult:
        """Validate all fields"""
        pass
```

### Enhanced Sale Model
```python
@dataclass
class Sale:
    sale_id: int
    sale_date: str
    customer_name: str
    total_amount: float  # Must be >= 0
    items: List[SaleItem]
    
    def calculate_total(self) -> float:
        """Calculate total from items"""
        return sum(item.quantity * item.unit_price for item in self.items)
    
    def validate(self) -> ValidationResult:
        """Ensure total matches item sum"""
        pass
```

### Enhanced Repair Order Model
```python
@dataclass
class RepairOrder:
    repair_id: int
    order_number: str  # Must be unique
    customer_name: str
    customer_phone: str  # Normalized format
    device_model: str
    imei: Optional[str]  # Optional field
    reported_problem: str
    received_date: str
    estimated_delivery: str
    status: str  # Must be valid status
    technician: str
    total_estimate: float  # Must match parts total
    notes: str
    parts: List[RepairPart]
    
    def calculate_parts_total(self) -> float:
        """Calculate total from parts"""
        return sum(part.qty * part.unit_price for part in self.parts)
    
    def validate(self) -> ValidationResult:
        """Ensure estimate matches parts"""
        pass
```

## Cor
rectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Inventory Properties

**Property 1: Non-negative inventory quantities**
*For any* inventory item added to the system, the stored quantity must be greater than or equal to zero.
**Validates: Requirements 1.1**

**Property 2: Inventory decrease matches sales**
*For any* completed sale, the inventory quantity decrease for each item must exactly equal the quantity sold.
**Validates: Requirements 1.2**

**Property 3: Sale rollback restores inventory**
*For any* sale transaction that fails, the inventory quantities must be identical to their state before the sale attempt.
**Validates: Requirements 1.4**

### Financial Calculation Properties

**Property 4: Sale total equals item sum**
*For any* sale with any items, the total_amount must equal the sum of (quantity × unit_price) for all items.
**Validates: Requirements 2.1**

**Property 5: Repair total equals parts sum**
*For any* repair order with any parts, the total_estimate must equal the sum of (qty × unit_price) for all parts.
**Validates: Requirements 2.2**

**Property 6: Profit calculation correctness**
*For any* set of completed transactions, profit must equal total revenue minus total costs.
**Validates: Requirements 2.3**

**Property 7: Tax calculation correctness**
*For any* amount and configured tax rate, the calculated tax must equal amount × (tax_rate / 100).
**Validates: Requirements 2.4**

### Transaction Atomicity Properties

**Property 8: Sale atomicity**
*For any* sale creation that encounters an error, either all related records (sale, sale_items, inventory updates) exist in the database or none exist.
**Validates: Requirements 3.1, 3.3**

**Property 9: Repair order atomicity**
*For any* repair order creation that encounters an error, either all related records (repair_order, repair_parts, repair_history) exist or none exist.
**Validates: Requirements 3.2**

**Property 10: Transaction rollback completeness**
*For any* database transaction that raises an exception, all changes within that transaction must be rolled back.
**Validates: Requirements 3.4**

### Validation Properties

**Property 11: Required field validation**
*For any* entity with required fields, attempting to save with empty required fields must be rejected.
**Validates: Requirements 4.3**

**Property 12: Phone number format validation**
*For any* phone number input, invalid formats must be rejected and valid formats must be normalized to a consistent pattern.
**Validates: Requirements 4.5**

### Repair Order Properties

**Property 13: Status change logging**
*For any* repair order status change, a corresponding entry must appear in repair_history with the old status, new status, and timestamp.
**Validates: Requirements 5.1**

**Property 14: Repair total consistency**
*For any* repair order, the total_estimate must always equal the sum of all associated repair parts costs.
**Validates: Requirements 5.2**

**Property 15: Repair history chronological ordering**
*For any* repair order, querying its history must return entries ordered by action_date in descending order (newest first).
**Validates: Requirements 5.4**

**Property 16: Cascading repair deletion**
*For any* repair order, deleting it must also delete all associated repair_parts and repair_history entries.
**Validates: Requirements 5.5**

**Property 37: Part linking atomicity**
*For any* part added to a repair order, the part must be linked to the repair atomically and the total estimate must be updated immediately.
**Validates: Requirements 5.6**

**Property 38: Checkout receipt generation**
*For any* repair checkout that is saved, a receipt must be generated with all repair details, parts, and payment information.
**Validates: Requirements 5.7**

### Backup and Restore Properties

**Property 17: Backup file validity**
*For any* database state, creating a backup must produce a file that SQLite can open and query without errors.
**Validates: Requirements 6.1**

**Property 18: Restore rollback on failure**
*For any* restore operation that fails, the current database must remain unchanged.
**Validates: Requirements 6.3**

**Property 19: Backup retention policy**
*For any* backup cleanup operation, the number of remaining backups must equal the configured max_backups value.
**Validates: Requirements 6.4**

**Property 20: Backup timestamp recording**
*For any* successful backup creation, the configuration must be updated with the backup timestamp.
**Validates: Requirements 6.5**

### Security Properties

**Property 21: Password hashing**
*For any* password, the stored value must be a hash (not plaintext) and must be different from the original password.
**Validates: Requirements 7.1**

**Property 22: Password complexity enforcement**
*For any* password that doesn't meet complexity requirements (minimum length, character types), user creation must be rejected.
**Validates: Requirements 7.3**

**Property 23: Unique password salts**
*For any* two users, their password hashes must use different salts even if they have the same password.
**Validates: Requirements 7.4**

### Audit Logging Properties

**Property 24: Repair creation audit**
*For any* repair order created, an audit log entry must exist with action_type="CREATE", entity_type="repair", and the repair_id.
**Validates: Requirements 8.1**

**Property 25: Status change audit**
*For any* repair status change, an audit log entry must exist with the old_value and new_value populated.
**Validates: Requirements 8.2**

**Property 26: Inventory modification audit**
*For any* inventory quantity change, an audit log entry must exist with the before and after quantities.
**Validates: Requirements 8.3**

**Property 27: User management audit**
*For any* user creation or deletion, an audit log entry must exist with action_type="CREATE" or "DELETE" and entity_type="user".
**Validates: Requirements 8.4**

**Property 28: Audit log chronological ordering**
*For any* audit log query, entries must be returned ordered by timestamp in descending order.
**Validates: Requirements 8.5**

### Customer Data Properties

**Property 29: Phone number normalization**
*For any* customer phone number stored, it must be in a normalized format (e.g., digits only or consistent formatting).
**Validates: Requirements 9.1**

**Property 30: Customer history completeness**
*For any* customer phone number, retrieving history must return all repair orders with that phone number.
**Validates: Requirements 9.2**

**Property 31: Customer statistics accuracy**
*For any* customer, the aggregated statistics (order count, total spent) must match the sum of their individual repair orders.
**Validates: Requirements 9.3**

### Dashboard Report Properties

**Property 32: Dashboard data freshness**
*For any* database state, dashboard statistics must reflect the current values without caching stale data.
**Validates: Requirements 10.1**

**Property 33: Revenue filtering correctness**
*For any* set of repair orders, revenue calculations must include only those with status "Completed" or "Delivered".
**Validates: Requirements 10.2**

**Property 34: Low stock threshold accuracy**
*For any* configured threshold value, the low stock count must equal the number of items with quantity less than the threshold.
**Validates: Requirements 10.3**

**Property 35: Overdue repair counting**
*For any* current date, the overdue count must equal the number of non-completed repairs with estimated_delivery before that date.
**Validates: Requirements 10.4**

**Property 36: Profit calculation completeness**
*For any* set of transactions, profit must account for both repair revenue and sales revenue minus all associated costs.
**Validates: Requirements 10.5**

## Error Handling

### Validation Errors
- All validation failures return `ValidationResult` with `valid=False` and descriptive `error_message`
- UI displays validation errors to users before attempting database operations
- No invalid data reaches the database layer

### Database Errors
- All database operations wrapped in try-except blocks
- Transactions automatically rolled back on any exception
- Errors logged with full context (operation, parameters, stack trace)
- User-friendly error messages displayed in UI

### Transaction Failures
- Use context managers for transaction handling: `with transaction():`
- Automatic rollback on exception exit
- Cleanup of any partial state (e.g., temporary files)
- Retry logic for transient failures (e.g., database locked)

### Backup/Restore Errors
- Validate backup file before restore operation
- Create safety backup before restore
- Rollback to safety backup if restore fails
- Clear error messages for common failures (file not found, corrupted backup)

## Testing Strategy

### Property-Based Testing Framework

**Library**: Hypothesis (Python's leading PBT library)

**Configuration**:
- Minimum 100 iterations per property test
- Deterministic random seed for reproducibility
- Shrinking enabled to find minimal failing examples
- Database state reset between test runs

**Test Data Generators**:

Located in `tests/generators.py`:

```python
from hypothesis import strategies as st

# Inventory generators
@st.composite
def inventory_item(draw):
    return {
        'sku': draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'name': draw(st.text(min_size=1, max_size=100)),
        'quantity': draw(st.integers(min_value=0, max_value=10000)),
        'buy_price': draw(st.floats(min_value=0.01, max_value=100000, allow_nan=False, allow_infinity=False)),
        'sell_price': draw(st.floats(min_value=0.01, max_value=100000, allow_nan=False, allow_infinity=False)),
        'category': draw(st.sampled_from(['Phones', 'Accessories', 'Parts', 'Services']))
    }

# Sale generators
@st.composite
def sale_with_items(draw, inventory_items):
    num_items = draw(st.integers(min_value=1, max_value=10))
    items = draw(st.lists(st.sampled_from(inventory_items), min_size=num_items, max_size=num_items))
    return {
        'customer_name': draw(st.text(min_size=1, max_size=100)),
        'items': [(item['item_id'], draw(st.integers(min_value=1, max_value=item['quantity'])), item['sell_price'], item['buy_price']) for item in items]
    }

# Repair order generators
@st.composite
def repair_order(draw):
    return {
        'order_number': draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))),
        'customer_name': draw(st.text(min_size=1, max_size=100)),
        'customer_phone': draw(st.from_regex(r'\d{10,15}', fullmatch=True)),
        'device_model': draw(st.sampled_from(['iPhone 12', 'Samsung S21', 'Pixel 6', 'OnePlus 9'])),
        'imei': draw(st.one_of(st.none(), st.from_regex(r'\d{15}', fullmatch=True))),  # Optional: can be None or valid IMEI
        'problem': draw(st.text(min_size=10, max_size=200)),
        'technician': draw(st.text(min_size=1, max_size=50))
    }
```

### Unit Testing Approach

**Framework**: pytest

**Coverage Goals**:
- 80%+ code coverage for critical modules (models, validators, transaction_manager)
- 100% coverage for financial calculation functions
- All error paths tested

**Test Organization**:
- One test file per module
- Fixtures for common test data and database setup
- Parametrized tests for multiple similar scenarios
- Clear test names describing what is being tested

### Integration Testing

**Scope**:
- End-to-end workflows (create sale → update inventory → generate receipt)
- Multi-step repair workflows (create → add parts → update status → complete)
- Backup and restore full cycle
- Concurrent operation scenarios

**Approach**:
- Use temporary test database
- Reset database state between tests
- Test with realistic data volumes
- Verify audit logs for all operations

### Test Execution

**Commands**:
```bash
# Run all tests
pytest tests/

# Run only property tests
pytest tests/ -m property

# Run with coverage
pytest tests/ --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_inventory.py -v
```

**CI/CD Integration**:
- Tests run on every commit
- Fail build if any test fails
- Generate coverage reports
- Track test execution time

### Property Test Tagging

Each property-based test MUST include a comment with this format:
```python
def test_inventory_non_negative():
    """
    **Feature: data-integrity-testing, Property 1: Non-negative inventory quantities**
    **Validates: Requirements 1.1**
    """
    # Test implementation
```

This ensures traceability from requirements → properties → tests.

## Implementation Notes

### Database Transaction Pattern

```python
from contextlib import contextmanager

@contextmanager
def transaction():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        log.error(f"Transaction rolled back: {e}")
        raise
    finally:
        conn.close()

# Usage
def create_sale_atomic(customer_name, items):
    with transaction() as conn:
        c = conn.cursor()
        # All operations here are atomic
        c.execute("INSERT INTO sales ...")
        for item in items:
            c.execute("INSERT INTO sale_items ...")
            c.execute("UPDATE inventory ...")
```

### Validation Pattern

```python
def add_inventory_item_validated(sku, name, qty, buy, sell, category):
    # Validate all inputs
    validations = [
        validate_sku(sku),
        validate_quantity(qty),
        validate_price(buy),
        validate_price(sell)
    ]
    
    for result in validations:
        if not result.valid:
            return ValidationError(result.error_message)
    
    # Proceed with database operation
    return add_inventory_item(sku, name, qty, buy, sell, category)
```

### Password Security Migration

```python
# New secure hashing (bcrypt)
import bcrypt

def hash_password_secure(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode('utf-8'), salt).decode('utf-8')

def verify_password_secure(stored: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), stored.encode('utf-8'))

# Migration function for existing users
def migrate_passwords():
    """One-time migration - users must reset passwords"""
    # Mark all users as needing password reset
    # Or: keep old hash_password for backward compatibility
```

## Dependencies

### New Dependencies
- `hypothesis` - Property-based testing framework
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `bcrypt` - Secure password hashing
- `faker` - Generate realistic test data

### Updated requirements.txt
```
ttkbootstrap>=1.10.1
reportlab>=4.0.0
qrcode>=7.4.2
hypothesis>=6.90.0
pytest>=7.4.0
pytest-cov>=4.1.0
bcrypt>=4.1.0
faker>=20.0.0
```

## Migration Strategy

### Phase 1: Testing Infrastructure (Week 1)
1. Set up pytest and hypothesis
2. Create test directory structure
3. Implement test data generators
4. Write first 10 property tests

### Phase 2: Validation Layer (Week 2)
1. Enhance validators.py with all validation functions
2. Add ValidationResult dataclass
3. Integrate validation into models
4. Write validation tests

### Phase 3: Transaction Management (Week 3)
1. Implement transaction context manager
2. Wrap all multi-step operations
3. Add rollback handling
4. Write transaction atomicity tests

### Phase 4: Security Enhancements (Week 4)
1. Implement bcrypt password hashing
2. Add password complexity validation
3. Plan password migration strategy
4. Write security tests

### Phase 5: Audit Improvements (Week 5)
1. Enhance audit logging coverage
2. Add missing audit points
3. Ensure chronological ordering
4. Write audit tests

### Phase 6: Full Test Suite (Week 6)
1. Complete all 36 property tests
2. Add unit tests for edge cases
3. Integration tests for workflows
4. Achieve 80%+ coverage

## Success Metrics

- **Test Coverage**: 80%+ for critical modules
- **Property Tests**: All 36 properties implemented and passing
- **Zero Critical Bugs**: No data integrity issues in production
- **Performance**: Tests complete in under 5 minutes
- **Maintainability**: New features include tests from day one
