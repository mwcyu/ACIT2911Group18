# Testing Guide

This directory contains the test suite for the Flask e-commerce application.

## Structure

```
tests/
├── conftest.py          # Shared pytest fixtures
├── constants.py         # Test constants and sample data
├── helpers.py          # Test helper functions
├── README.md           # This file
├── integration/        # Integration tests
└── unit/              # Unit tests
```

## Test Categories

- **Unit Tests**: Tests individual components in isolation (models, utilities)
- **Integration Tests**: Tests components working together (routes, database)

## Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage report
pytest --cov=.

# Run specific test file
pytest tests/unit/test_models.py
```

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `app`: Flask test application
- `client`: Flask test client
- `db`: Database session
- `test_user`: Sample user
- `test_product`: Sample product
- `test_category`: Sample category
- `logged_in_client`: Pre-authenticated client

## Helpers

Common test helper functions are in `helpers.py`:

- `login()`: Helper to log in a test user
- `create_test_product()`: Create a product for testing
- `assert_flashed_message()`: Check for Flash messages

## Best Practices

1. Use fixtures from conftest.py instead of creating test data manually
2. Group related tests in classes
3. Use descriptive test names that explain the scenario
4. One assertion per test when possible
5. Use test constants from constants.py
6. Mock external services and API calls