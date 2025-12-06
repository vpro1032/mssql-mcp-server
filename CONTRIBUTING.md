# Contributing to MSSQL MCP Server

Thank you for considering contributing to the MSSQL MCP Server! This document provides guidelines for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and professional in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (queries, configuration, etc.)
- **Describe the behavior you observed** and what you expected
- **Include logs and error messages**
- **Specify your environment:**
  - OS (Windows, Mac, Linux)
  - Docker version
  - Python version
  - MSSQL Server version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any potential drawbacks** or challenges

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the code style** used throughout the project
3. **Add tests** for any new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass** before submitting
6. **Write a clear commit message** describing your changes

## Development Setup

### Prerequisites

- Docker Desktop installed and running
- Python 3.11+
- Git

### Local Development

1. Clone your fork:
   ```bash
   git clone https://github.com/vpro1032/mssql-mcp-server.git
   cd mssql-mcp-server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment template:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Run tests:
   ```bash
   ./test-runner.sh
   ```

## Code Style

### Python Code Style

- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return values
- Use **Pydantic models** for data validation
- **Maximum line length:** 100 characters
- **Docstrings:** Use Google-style docstrings

Example:
```python
def execute_query(
    query: str,
    database: Optional[str] = None,
    max_rows: int = 1000
) -> Dict[str, Any]:
    """
    Execute a SELECT query with safety constraints.

    Args:
        query: SQL SELECT statement to execute
        database: Optional database name to switch to
        max_rows: Maximum number of rows to return

    Returns:
        Dictionary containing query results, metadata, and execution time

    Raises:
        ValueError: If query validation fails
        pyodbc.Error: If database error occurs
    """
    # Implementation
    pass
```

### Code Organization

- Keep functions small and focused (< 50 lines when possible)
- Use meaningful variable and function names
- Avoid deep nesting (max 3 levels)
- Separate concerns (database, validation, tools)

### Security Guidelines

**Always consider security implications:**

- ✅ **DO** use parameterized queries
- ✅ **DO** validate all user inputs
- ✅ **DO** sanitize error messages
- ✅ **DO** follow principle of least privilege
- ❌ **DON'T** use f-strings for SQL queries
- ❌ **DON'T** expose internal error details
- ❌ **DON'T** commit credentials or secrets

## Testing

### Running Tests

```bash
# Run full integration test suite
./test-runner.sh

# Run quick manual tests
./quick-test.sh
```

### Writing Tests

- Add tests for all new features
- Include security tests for query validation
- Test error handling paths
- Use descriptive test names

Example:
```python
def test_sql_injection_prevention(self):
    """Test that multi-statement SQL injection attempts are blocked"""
    malicious_query = "SELECT * FROM users; DROP TABLE users;"
    result = self.send_mcp_request("mssql_query", {
        "query": malicious_query,
        "database": "TestDB"
    })

    self.assert_test(
        "SQL injection blocked",
        "error" in result,
        "Multi-statement queries should be rejected"
    )
```

## Documentation

### Updating Documentation

When making changes, update:

- **README.md** - For user-facing changes
- **API.md** - For tool interface changes
- **CONFIGURATION.md** - For new config options
- **Code comments** - For complex logic
- **Docstrings** - For all public functions

### Documentation Style

- Use clear, concise language
- Include code examples
- Provide both quick start and detailed explanations
- Use proper Markdown formatting

## Git Workflow

### Branch Naming

- `feature/` - New features (e.g., `feature/add-stored-procedures`)
- `fix/` - Bug fixes (e.g., `fix/sql-injection-bypass`)
- `docs/` - Documentation updates (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/connection-pooling`)

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

More detailed explanation if needed.

Fixes #123
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat(tools): add stored procedure execution support

Implements FR-2.5 from requirements document. Includes:
- Parameter validation
- Whitelist checking
- Transaction isolation

Closes #45

---

fix(security): prevent database name injection in USE statement

Added validation against sys.databases before allowing
database context switching.

Fixes #67
```

## Review Process

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Changes are focused and atomic

### Review Criteria

Reviewers will check:

1. **Code Quality** - Clean, readable, maintainable
2. **Security** - No vulnerabilities introduced
3. **Testing** - Adequate test coverage
4. **Documentation** - Clear and complete
5. **Performance** - No significant regressions
6. **Compatibility** - Works across platforms

## Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for significant contributions
- `SUPPORTERS.md` for Patreon supporters

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Bugs?** Open a GitHub Issue
- **Ideas?** Open a GitHub Issue with "enhancement" label
- **Security issues?** Email security@yourdomain.com (do not open public issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MSSQL MCP Server! 🎉
