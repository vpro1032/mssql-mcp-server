# MSSQL Database MCP Server - Requirements Document

## Project Overview

Create an enterprise-grade Model Context Protocol (MCP) server for Microsoft SQL Server that enables AI assistants to interact with MSSQL databases through a secure, containerized solution deployable on Docker Desktop for Windows and Mac.

## Core Objectives

1. Provide secure, read-only and controlled write access to MSSQL databases
2. Support enterprise authentication methods (SQL Server Auth, Windows Auth via Docker)
3. Enable deployment via Docker Desktop on Windows and Mac with minimal configuration
4. Implement comprehensive error handling and logging
5. Support connection pooling and query optimization
6. Provide schema introspection and metadata discovery capabilities

## Technology Stack

### Primary Implementation
- **Language**: Python 3.11+ or TypeScript/Node.js 22+
- **MCP SDK**: 
  - Python: `mcp` library from Anthropic
  - TypeScript: `@modelcontextprotocol/sdk`
- **Database Driver**:
  - Python: `pyodbc` with Microsoft ODBC Driver 18 for SQL Server
  - TypeScript: `mssql` (tedious driver)
- **Container**: Docker with multi-stage builds
- **Base Image**: 
  - Python: `python:3.11-slim` or `python:3.11-alpine`
  - Node: `node:22-alpine`

### Dependencies
- Connection pooling library
- Async I/O support
- Environment variable management
- Structured logging (JSON format)
- Health check endpoint support

## Functional Requirements

### 1. Database Connection Management

#### FR-1.1: Connection Configuration
- Support connection via environment variables:
  - `MSSQL_HOST`: Database server hostname/IP
  - `MSSQL_PORT`: Port (default 1433)
  - `MSSQL_DATABASE`: Default database name
  - `MSSQL_USER`: SQL Server username
  - `MSSQL_PASSWORD`: SQL Server password
  - `MSSQL_ENCRYPT`: Enable/disable encryption (default true)
  - `MSSQL_TRUST_SERVER_CERTIFICATE`: Trust self-signed certs (default false)
  - `MSSQL_CONNECTION_TIMEOUT`: Timeout in seconds (default 30)
  - `MSSQL_REQUEST_TIMEOUT`: Query timeout in seconds (default 30)

#### FR-1.2: Connection Pooling
- Implement connection pooling with configurable:
  - Min pool size (default 2)
  - Max pool size (default 10)
  - Idle timeout (default 300 seconds)
  - Connection lifetime (default 1800 seconds)

#### FR-1.3: Connection Health
- Implement connection health checks
- Auto-reconnect on connection loss
- Validate connections before query execution

### 2. MCP Tools Implementation

#### FR-2.1: Query Execution Tool
**Tool Name**: `mssql_query`

**Description**: Execute SELECT queries with safety constraints

**Parameters**:
- `query` (string, required): SQL SELECT statement
- `database` (string, optional): Target database (overrides default)
- `max_rows` (integer, optional): Maximum rows to return (default 1000, max 10000)
- `timeout` (integer, optional): Query timeout in seconds (default 30, max 300)

**Returns**:
- JSON array of result rows
- Column metadata (names, types)
- Row count
- Execution time

**Safety Features**:
- Block non-SELECT statements (INSERT, UPDATE, DELETE, DROP, etc.)
- Prevent multiple statements (semicolon detection)
- Validate query syntax before execution
- Apply row limits
- Enforce query timeouts

#### FR-2.2: Schema Introspection Tool
**Tool Name**: `mssql_list_tables`

**Description**: List all tables in the database

**Parameters**:
- `database` (string, optional): Target database
- `schema` (string, optional): Filter by schema (default 'dbo')
- `include_views` (boolean, optional): Include views (default false)

**Returns**:
- Array of table objects containing:
  - Table name
  - Schema name
  - Row count estimate
  - Create date
  - Modification date

#### FR-2.3: Table Schema Tool
**Tool Name**: `mssql_describe_table`

**Description**: Get detailed schema information for a specific table

**Parameters**:
- `table_name` (string, required): Table name
- `schema` (string, optional): Schema name (default 'dbo')
- `database` (string, optional): Target database

**Returns**:
- Table metadata:
  - Column names, types, nullability, defaults
  - Primary keys
  - Foreign keys
  - Indexes
  - Constraints
  - Row count
  - Table size

#### FR-2.4: Database List Tool
**Tool Name**: `mssql_list_databases`

**Description**: List all accessible databases on the server

**Parameters**: None

**Returns**:
- Array of database objects containing:
  - Database name
  - State (online/offline)
  - Recovery model
  - Compatibility level
  - Size

#### FR-2.5: Stored Procedure Execution Tool (Optional)
**Tool Name**: `mssql_execute_procedure`

**Description**: Execute stored procedures with parameters

**Parameters**:
- `procedure_name` (string, required): Stored procedure name
- `parameters` (object, optional): Named parameters as key-value pairs
- `database` (string, optional): Target database
- `timeout` (integer, optional): Execution timeout

**Returns**:
- Result sets (if any)
- Return value
- Output parameters

**Safety Features**:
- Whitelist of allowed procedures (configurable)
- Parameter type validation
- Transaction isolation

#### FR-2.6: Write Operations Tool (Optional, Configurable)
**Tool Name**: `mssql_execute_write`

**Description**: Execute INSERT, UPDATE, DELETE with strict controls

**Parameters**:
- `statement` (string, required): DML statement
- `database` (string, optional): Target database
- `dry_run` (boolean, optional): Validate without executing

**Returns**:
- Rows affected
- Execution time
- Validation results (if dry_run)

**Safety Features**:
- Require explicit enable flag: `MSSQL_ALLOW_WRITE_OPERATIONS=true`
- Transaction wrapper with rollback capability
- Statement validation and parsing
- Audit logging of all write operations
- Row affect limits (configurable)

### 3. MCP Resources Implementation

#### FR-3.1: Database Schema Resource
**Resource URI**: `mssql://schema/{database}/{schema}`

**Description**: Provide database schema as a readable resource

**Content**: Complete schema definition in JSON or SQL format

#### FR-3.2: Table Data Sample Resource
**Resource URI**: `mssql://sample/{database}/{schema}/{table}`

**Description**: Provide sample rows from a table

**Content**: First 10 rows of the table with schema

## Non-Functional Requirements

### NFR-1: Security

#### NFR-1.1: Authentication
- Support SQL Server authentication
- Support connection string encryption
- Never log passwords or sensitive connection details
- Use Docker secrets for credential management

#### NFR-1.2: Authorization
- Implement query filtering to prevent unauthorized access
- Support read-only mode by default
- Require explicit configuration for write operations
- Validate user permissions before query execution

#### NFR-1.3: SQL Injection Prevention
- Use parameterized queries where possible
- Implement SQL parsing and validation
- Block dangerous SQL patterns (EXECUTE, xp_cmdshell, etc.)
- Sanitize all user inputs

#### NFR-1.4: Network Security
- Support TLS/SSL encryption for database connections
- Allow configuration of certificate validation
- Support network isolation via Docker networks

### NFR-2: Performance

#### NFR-2.1: Query Performance
- Implement query result caching (optional, configurable TTL)
- Use connection pooling to reduce overhead
- Stream large result sets when possible
- Implement query execution plans logging (optional)

#### NFR-2.2: Resource Management
- Limit memory usage per query
- Implement query timeouts
- Use async/await for non-blocking operations
- Monitor and log resource utilization

### NFR-3: Reliability

#### NFR-3.1: Error Handling
- Graceful handling of connection failures
- Retry logic with exponential backoff
- Detailed error messages without exposing sensitive information
- Transaction rollback on errors

#### NFR-3.2: Logging
- Structured logging in JSON format
- Configurable log levels (DEBUG, INFO, WARN, ERROR)
- Log query execution times
- Log connection pool statistics
- Audit trail for write operations

#### NFR-3.3: Monitoring
- Health check endpoint for container orchestration
- Expose metrics (queries/sec, connection count, errors)
- Database connection status monitoring

### NFR-4: Maintainability

#### NFR-4.1: Code Quality
- Type hints/TypeScript strict mode
- Comprehensive unit tests (>80% coverage)
- Integration tests with test database
- Linting and formatting (pylint/black or ESLint/Prettier)

#### NFR-4.2: Documentation
- Inline code documentation
- API documentation for all tools
- Docker deployment guide
- Configuration reference
- Troubleshooting guide

### NFR-5: Portability

#### NFR-5.1: Docker Support
- Multi-arch Docker image (amd64, arm64)
- Docker Compose configuration included
- Support for Docker Desktop on Windows and Mac
- Minimal image size (<200MB compressed)

#### NFR-5.2: Configuration
- Environment variable based configuration
- Support for .env files
- Configuration validation on startup
- Sensible defaults for all settings

## Docker Implementation Requirements

### Docker-1: Dockerfile

```dockerfile
# Multi-stage build example structure
FROM python:3.11-slim as builder
# Install build dependencies
# Install Microsoft ODBC Driver 18
# Install Python dependencies

FROM python:3.11-slim
# Copy only runtime dependencies
# Copy application code
# Set non-root user
# Expose health check port (optional)
# Set entrypoint
```

### Docker-2: Docker Compose

Provide a `docker-compose.yml` with:
- MCP server service configuration
- MSSQL server service for testing (optional)
- Volume mounts for configuration
- Network configuration
- Environment variable examples
- Health checks

### Docker-3: Environment Configuration

Example `.env.example` file:
```env
MSSQL_HOST=sqlserver
MSSQL_PORT=1433
MSSQL_DATABASE=master
MSSQL_USER=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_ENCRYPT=true
MSSQL_TRUST_SERVER_CERTIFICATE=false
MSSQL_ALLOW_WRITE_OPERATIONS=false
LOG_LEVEL=INFO
```

## MCP Server Configuration

### MCP Configuration File
The server should be configurable via Claude Desktop or other MCP clients with a configuration like:

```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "-e", "MSSQL_HOST=localhost",
        "-e", "MSSQL_PORT=1433",
        "-e", "MSSQL_DATABASE=MyDatabase",
        "-e", "MSSQL_USER=myuser",
        "-e", "MSSQL_PASSWORD=mypassword",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

## IDE Integration Requirements

### Overview
The MSSQL MCP server must be easily integrable with popular AI-powered development environments. Each IDE has its own MCP configuration approach, and the server should support all three major platforms.

### Claude Code Integration

**Configuration Location**: 
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration Example - Docker Deployment**:
```json
{
  "mcpServers": {
    "mssql-production": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "-e", "MSSQL_HOST=localhost",
        "-e", "MSSQL_PORT=1433",
        "-e", "MSSQL_DATABASE=ProductionDB",
        "-e", "MSSQL_USER=readonly_user",
        "-e", "MSSQL_PASSWORD=SecurePass123!",
        "-e", "MSSQL_ENCRYPT=true",
        "-e", "MSSQL_TRUST_SERVER_CERTIFICATE=false",
        "-e", "LOG_LEVEL=INFO",
        "mssql-mcp-server:latest"
      ]
    },
    "mssql-development": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "-e", "MSSQL_HOST=localhost",
        "-e", "MSSQL_PORT=1433",
        "-e", "MSSQL_DATABASE=DevDB",
        "-e", "MSSQL_USER=dev_user",
        "-e", "MSSQL_PASSWORD=DevPass123!",
        "-e", "MSSQL_ALLOW_WRITE_OPERATIONS=true",
        "-e", "LOG_LEVEL=DEBUG",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

**Configuration Example - Native Execution (Python)**:
```json
{
  "mcpServers": {
    "mssql": {
      "command": "python",
      "args": ["-m", "mssql_mcp_server"],
      "env": {
        "MSSQL_HOST": "localhost",
        "MSSQL_PORT": "1433",
        "MSSQL_DATABASE": "MyDatabase",
        "MSSQL_USER": "myuser",
        "MSSQL_PASSWORD": "mypassword"
      }
    }
  }
}
```

**Configuration Example - Native Execution (Node.js)**:
```json
{
  "mcpServers": {
    "mssql": {
      "command": "node",
      "args": ["path/to/mssql-mcp-server/dist/index.js"],
      "env": {
        "MSSQL_HOST": "localhost",
        "MSSQL_PORT": "1433",
        "MSSQL_DATABASE": "MyDatabase",
        "MSSQL_USER": "myuser",
        "MSSQL_PASSWORD": "mypassword"
      }
    }
  }
}
```

**Verification Steps**:
1. Save configuration to `claude_desktop_config.json`
2. Restart Claude Desktop application
3. Open Claude and verify MCP server appears in settings
4. Test with prompt: "List all tables in my database"

### Cursor IDE Integration

**Configuration Location**:
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp-config.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp-config.json`

**Note**: Cursor's MCP support may vary by version. Check Cursor documentation for latest configuration format.

**Configuration Example - Docker Deployment**:
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "--env-file", "/path/to/.env",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

**Configuration Example - Using Docker Compose**:
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker-compose",
      "args": [
        "-f", "/path/to/docker-compose.yml",
        "run",
        "--rm",
        "mssql-mcp-server"
      ]
    }
  }
}
```

**Environment File Approach** (`.env` file):
```env
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=MyDatabase
MSSQL_USER=myuser
MSSQL_PASSWORD=mypassword
MSSQL_ENCRYPT=true
MSSQL_TRUST_SERVER_CERTIFICATE=false
LOG_LEVEL=INFO
```

**Verification Steps**:
1. Save configuration file
2. Restart Cursor IDE
3. Open MCP panel in Cursor
4. Verify MSSQL server is listed and connected
5. Test with AI prompt that requires database access

### Windsurf IDE Integration

**Configuration Location**:
- Windows: `%APPDATA%\Windsurf\mcp-servers.json`
- Mac: `~/Library/Application Support/Windsurf/mcp-servers.json`
- Linux: `~/.config/Windsurf/mcp-servers.json`

**Configuration Example - Docker with Volume Mounts**:
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "-v", "${workspaceFolder}/.env:/app/.env:ro",
        "mssql-mcp-server:latest"
      ],
      "env": {
        "ENV_FILE": "/app/.env"
      }
    }
  }
}
```

**Configuration Example - Multiple Databases**:
```json
{
  "mcpServers": {
    "mssql-analytics": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--network", "host",
        "-e", "MSSQL_HOST=analytics.company.com",
        "-e", "MSSQL_DATABASE=AnalyticsDB",
        "-e", "MSSQL_USER=readonly",
        "-e", "MSSQL_PASSWORD=ReadOnlyPass!",
        "mssql-mcp-server:latest"
      ]
    },
    "mssql-transactions": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--network", "host",
        "-e", "MSSQL_HOST=transactions.company.com",
        "-e", "MSSQL_DATABASE=TransactionsDB",
        "-e", "MSSQL_USER=app_user",
        "-e", "MSSQL_PASSWORD=AppPass!",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

**Verification Steps**:
1. Create or update `mcp-servers.json`
2. Restart Windsurf IDE
3. Check MCP server status in Windsurf settings
4. Test database queries through AI assistant

### Cross-IDE Configuration Best Practices

#### 1. Environment Variable Management

**Option A: Direct in Config (Quick Start)**
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "VAR=value", "..."]
    }
  }
}
```

**Option B: External .env File (Recommended)**
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env-file", ".env", "..."]
    }
  }
}
```

**Option C: Docker Compose (Team Collaboration)**
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker-compose",
      "args": ["-f", "docker-compose.mcp.yml", "run", "--rm", "mssql-mcp"]
    }
  }
}
```

#### 2. Security Considerations

**DO NOT** commit credentials to version control:
- Add `*_config.json` to `.gitignore`
- Add `.env` to `.gitignore`
- Use environment-specific configuration files

**Recommended Structure**:
```
.gitignore              # Ignore sensitive configs
.env.example            # Template with placeholder values
.env                    # Local config (not committed)
mcp-config.template.json # Template config
README-MCP-SETUP.md     # Setup instructions
```

**Example .env.example**:
```env
# MSSQL Connection Settings
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=MyDatabase
MSSQL_USER=your_username
MSSQL_PASSWORD=your_secure_password
MSSQL_ENCRYPT=true
MSSQL_TRUST_SERVER_CERTIFICATE=false

# Server Settings
MSSQL_ALLOW_WRITE_OPERATIONS=false
LOG_LEVEL=INFO
```

#### 3. Network Configuration

**Local Development (Same Machine)**:
```bash
--network host  # Direct access to localhost services
```

**Docker Compose Network**:
```yaml
networks:
  mcp-network:
    driver: bridge

services:
  mssql-mcp-server:
    networks:
      - mcp-network
```

**Corporate VPN/Remote Server**:
```bash
# Ensure Docker can resolve corporate DNS
--dns 10.0.0.1 --dns 8.8.8.8
```

#### 4. Troubleshooting Integration Issues

**Issue: MCP Server Not Appearing**
- Check config file location is correct for your OS
- Validate JSON syntax (use JSON validator)
- Restart IDE completely (not just reload)
- Check IDE logs for MCP initialization errors

**Issue: Connection Refused**
- Verify MSSQL server is accessible: `telnet hostname 1433`
- Check Docker network mode (`host` vs `bridge`)
- Verify firewall rules allow connection
- Test connection with SQL client first

**Issue: Authentication Failed**
- Verify credentials are correct
- Check SQL Server allows SQL authentication (not just Windows Auth)
- Verify user has appropriate permissions
- Check if password contains special characters that need escaping

**Issue: Docker Image Not Found**
- Build or pull the image first: `docker build -t mssql-mcp-server:latest .`
- Verify image exists: `docker images | grep mssql-mcp-server`
- Use full image name if using registry: `myregistry/mssql-mcp-server:latest`

### IDE-Specific Features Configuration

#### Claude Code Specific
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": ["..."],
      "settings": {
        "autoStart": true,
        "restartOnFailure": true
      }
    }
  }
}
```

#### Cursor Specific
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": ["..."],
      "capabilities": {
        "tools": true,
        "resources": true,
        "prompts": false
      }
    }
  }
}
```

#### Windsurf Specific
```json
{
  "mcpServers": {
    "mssql": {
      "command": "docker",
      "args": ["..."],
      "metadata": {
        "description": "MSSQL Database Server",
        "icon": "database",
        "tags": ["sql", "database", "mssql"]
      }
    }
  }
}
```

### Testing IDE Integration

#### Integration Test Checklist

1. **Basic Connectivity**
   - [ ] MCP server appears in IDE
   - [ ] Connection status shows as connected
   - [ ] No errors in IDE console

2. **Tool Availability**
   - [ ] `mssql_query` tool is available
   - [ ] `mssql_list_tables` tool is available
   - [ ] `mssql_describe_table` tool is available
   - [ ] `mssql_list_databases` tool is available

3. **Query Execution**
   - [ ] Can execute simple SELECT query
   - [ ] Can list all tables
   - [ ] Can describe table schema
   - [ ] Error messages are clear and helpful

4. **Performance**
   - [ ] Query response time < 5 seconds for simple queries
   - [ ] Large result sets are handled gracefully
   - [ ] No IDE freezing during query execution

5. **Security**
   - [ ] Read-only mode prevents write operations
   - [ ] SQL injection attempts are blocked
   - [ ] Invalid queries return appropriate errors

### Sample Integration Test Prompts

Use these prompts in your IDE to verify integration:

```
1. "List all databases on my SQL Server"
2. "Show me all tables in the [YourDatabase] database"
3. "Describe the schema of the [TableName] table"
4. "Query the top 10 rows from [TableName]"
5. "Find all tables that contain a column named 'CustomerID'"
6. "Show me the foreign key relationships for [TableName]"
7. "What's the total row count across all tables?"
```

### Documentation Requirements for Integration

The project must include an `IDE-INTEGRATION.md` file covering:

1. **Prerequisites**
   - Docker Desktop installed and running
   - IDE version requirements
   - MSSQL server access

2. **Step-by-Step Setup** for each IDE
   - Exact file locations
   - Configuration templates
   - Copy-paste ready examples

3. **Common Issues and Solutions**
   - Platform-specific quirks
   - Network configuration issues
   - Authentication problems

4. **Advanced Configurations**
   - Multiple database connections
   - Environment-specific configs
   - Team sharing strategies

5. **Video/Screenshot Walkthrough** (optional but recommended)
   - Visual guide for first-time setup
   - Demonstration of features

## Project Structure

```
mssql-mcp-server/
├── src/
│   ├── server.py (or server.ts)
│   ├── tools/
│   │   ├── query.py
│   │   ├── schema.py
│   │   └── introspection.py
│   ├── resources/
│   │   └── schema_resource.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── pool.py
│   │   └── query_validator.py
│   └── utils/
│       ├── logging.py
│       └── config.py
├── tests/
│   ├── unit/
│   ├── integration/
│   │   └── test_mcp_tools.py       # Automated integration tests
├── test-data/
│   └── 01-init-db.sql              # Test database schema
├── docs/
│   ├── SETUP.md
│   ├── CONFIGURATION.md
│   ├── IDE-INTEGRATION.md          # New: Detailed IDE setup guide
│   ├── TROUBLESHOOTING.md
│   └── EXAMPLES.md                 # New: Usage examples
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.test.yml     # Test environment compose file
├── ide-configs/                     # New: Sample IDE configurations
│   ├── claude-code-config.json
│   ├── cursor-config.json
│   └── windsurf-config.json
├── test-runner.sh                   # Automated test runner
├── quick-test.sh                    # Manual testing script
├── .env.example
├── .gitignore
├── requirements.txt (or package.json)
├── README.md
└── LICENSE
```

## Testing Requirements

### Test-1: Unit Tests
- Test query validation logic
- Test SQL injection prevention
- Test connection pool management
- Test error handling
- Mock database interactions

### Test-2: Integration Tests
- Test against real MSSQL server (containerized)
- Test all MCP tools
- Test connection failure scenarios
- Test query timeouts
- Test concurrent requests

### Test-3: Security Tests
- Test SQL injection attempts
- Test unauthorized query patterns
- Test connection string security
- Test write operation restrictions

## AI-Assisted Testing Strategy

### Overview
This section provides a simple, automated testing strategy that AI tools (Claude Code, Cursor) can execute to validate the MCP server implementation. The strategy uses Docker containers for both MSSQL database and automated testing.

### Testing Architecture

```
┌─────────────────────────────────────────────────────────┐
│  AI Tool (Claude Code / Cursor)                         │
│  ├─ Builds MCP Server Docker Image                      │
│  ├─ Starts Test MSSQL Container                         │
│  ├─ Runs Automated Test Suite                           │
│  └─ Validates Results                                   │
└─────────────────────────────────────────────────────────┘
```

### Prerequisites for AI Testing

The AI tool must have access to:
1. Docker CLI commands via terminal/bash
2. Ability to create and run test scripts
3. Ability to read test output and validate results
4. Network access for pulling Docker images

### Test Environment Setup

#### Step 1: Create Test Docker Compose File

**File**: `docker-compose.test.yml`

```yaml
version: '3.8'

services:
  # Test MSSQL Database
  mssql-test:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: mssql-test-db
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=Test1234!@#$
      - MSSQL_PID=Developer
    ports:
      - "1433:1433"
    volumes:
      - ./test-data:/docker-entrypoint-initdb.d
    healthcheck:
      test: /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Test1234!@#$$ -Q "SELECT 1"
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - test-network

  # MCP Server Under Test
  mssql-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mssql-mcp-test
    depends_on:
      mssql-test:
        condition: service_healthy
    environment:
      - MSSQL_HOST=mssql-test
      - MSSQL_PORT=1433
      - MSSQL_DATABASE=TestDB
      - MSSQL_USER=sa
      - MSSQL_PASSWORD=Test1234!@#$$
      - MSSQL_ENCRYPT=false
      - MSSQL_TRUST_SERVER_CERTIFICATE=true
      - MSSQL_ALLOW_WRITE_OPERATIONS=true
      - LOG_LEVEL=DEBUG
    stdin_open: true
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

#### Step 2: Create Test Database Schema

**File**: `test-data/01-init-db.sql`

```sql
-- Create test database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TestDB')
BEGIN
    CREATE DATABASE TestDB;
END
GO

USE TestDB;
GO

-- Create test schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'test')
BEGIN
    EXEC('CREATE SCHEMA test');
END
GO

-- Create test tables
CREATE TABLE test.Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) UNIQUE,
    CreatedDate DATETIME DEFAULT GETDATE(),
    IsActive BIT DEFAULT 1
);

CREATE TABLE test.Orders (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT GETDATE(),
    TotalAmount DECIMAL(10,2),
    Status NVARCHAR(20),
    FOREIGN KEY (CustomerID) REFERENCES test.Customers(CustomerID)
);

CREATE TABLE test.Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    ProductName NVARCHAR(100) NOT NULL,
    Category NVARCHAR(50),
    Price DECIMAL(10,2),
    StockQuantity INT DEFAULT 0
);

-- Insert test data
INSERT INTO test.Customers (FirstName, LastName, Email) VALUES
('John', 'Doe', 'john.doe@example.com'),
('Jane', 'Smith', 'jane.smith@example.com'),
('Bob', 'Johnson', 'bob.johnson@example.com'),
('Alice', 'Williams', 'alice.williams@example.com'),
('Charlie', 'Brown', 'charlie.brown@example.com');

INSERT INTO test.Products (ProductName, Category, Price, StockQuantity) VALUES
('Laptop', 'Electronics', 999.99, 50),
('Mouse', 'Electronics', 29.99, 200),
('Keyboard', 'Electronics', 79.99, 150),
('Monitor', 'Electronics', 299.99, 75),
('Desk Chair', 'Furniture', 199.99, 30);

INSERT INTO test.Orders (CustomerID, OrderDate, TotalAmount, Status) VALUES
(1, '2024-01-15', 1299.97, 'Completed'),
(2, '2024-01-16', 999.99, 'Completed'),
(3, '2024-01-17', 329.98, 'Pending'),
(1, '2024-01-18', 79.99, 'Completed'),
(4, '2024-01-19', 499.98, 'Shipped');

-- Create a test stored procedure
CREATE PROCEDURE test.GetCustomerOrders
    @CustomerID INT
AS
BEGIN
    SELECT 
        o.OrderID,
        o.OrderDate,
        o.TotalAmount,
        o.Status
    FROM test.Orders o
    WHERE o.CustomerID = @CustomerID
    ORDER BY o.OrderDate DESC;
END
GO

-- Create a test view
CREATE VIEW test.vw_CustomerOrderSummary AS
SELECT 
    c.CustomerID,
    c.FirstName,
    c.LastName,
    COUNT(o.OrderID) as TotalOrders,
    ISNULL(SUM(o.TotalAmount), 0) as TotalSpent
FROM test.Customers c
LEFT JOIN test.Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName;
GO
```

### Automated Test Suite

#### Step 3: Create MCP Test Script

**File**: `tests/integration/test_mcp_tools.py`

```python
#!/usr/bin/env python3
"""
Automated MCP Server Integration Tests
This script can be executed by AI tools to validate MCP server functionality
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, List

class MCPTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def send_mcp_request(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP request to the server via stdin/stdout"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments
            }
        }
        
        # In real implementation, this would communicate with MCP server
        # For testing, we'll use docker exec
        try:
            cmd = [
                "docker", "exec", "-i", "mssql-mcp-test",
                "python", "-c", 
                f"import json; import sys; print(json.dumps({json.dumps(request)}))"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def assert_test(self, test_name: str, condition: bool, message: str = ""):
        """Assert a test condition and record result"""
        if condition:
            self.passed_tests += 1
            status = "✓ PASS"
            print(f"{status}: {test_name}")
        else:
            self.failed_tests += 1
            status = "✗ FAIL"
            print(f"{status}: {test_name}")
            if message:
                print(f"  → {message}")
        
        self.test_results.append({
            "test": test_name,
            "status": "passed" if condition else "failed",
            "message": message
        })
        
        return condition
    
    def test_list_databases(self):
        """Test 1: List all databases"""
        print("\n[TEST 1] Testing mssql_list_databases...")
        
        # Simulate tool call
        result = self.send_mcp_request("mssql_list_databases", {})
        
        # Validate response structure
        has_databases = isinstance(result.get("databases"), list)
        self.assert_test(
            "List databases returns array",
            has_databases,
            f"Expected list, got {type(result.get('databases'))}"
        )
        
        # Check TestDB exists
        if has_databases:
            db_names = [db.get("name") for db in result["databases"]]
            has_testdb = "TestDB" in db_names
            self.assert_test(
                "TestDB exists in database list",
                has_testdb,
                f"Found databases: {db_names}"
            )
    
    def test_list_tables(self):
        """Test 2: List tables in TestDB"""
        print("\n[TEST 2] Testing mssql_list_tables...")
        
        result = self.send_mcp_request("mssql_list_tables", {
            "database": "TestDB",
            "schema": "test"
        })
        
        # Validate response
        has_tables = isinstance(result.get("tables"), list)
        self.assert_test(
            "List tables returns array",
            has_tables
        )
        
        if has_tables:
            table_names = [t.get("name") for t in result["tables"]]
            
            # Check expected tables exist
            expected_tables = ["Customers", "Orders", "Products"]
            for table in expected_tables:
                has_table = table in table_names
                self.assert_test(
                    f"Table 'test.{table}' exists",
                    has_table,
                    f"Found tables: {table_names}"
                )
    
    def test_describe_table(self):
        """Test 3: Describe table schema"""
        print("\n[TEST 3] Testing mssql_describe_table...")
        
        result = self.send_mcp_request("mssql_describe_table", {
            "table_name": "Customers",
            "schema": "test",
            "database": "TestDB"
        })
        
        # Validate schema information
        has_columns = isinstance(result.get("columns"), list)
        self.assert_test(
            "Describe table returns columns",
            has_columns
        )
        
        if has_columns:
            column_names = [c.get("name") for c in result["columns"]]
            
            # Check expected columns
            expected_columns = ["CustomerID", "FirstName", "LastName", "Email"]
            for col in expected_columns:
                has_column = col in column_names
                self.assert_test(
                    f"Column '{col}' exists in Customers table",
                    has_column
                )
            
            # Check primary key information
            has_pk = result.get("primary_key") is not None
            self.assert_test(
                "Primary key information is present",
                has_pk
            )
    
    def test_simple_query(self):
        """Test 4: Execute simple SELECT query"""
        print("\n[TEST 4] Testing mssql_query (simple SELECT)...")
        
        result = self.send_mcp_request("mssql_query", {
            "query": "SELECT TOP 5 * FROM test.Customers ORDER BY CustomerID",
            "database": "TestDB"
        })
        
        # Validate query results
        has_rows = isinstance(result.get("rows"), list)
        self.assert_test(
            "Query returns rows array",
            has_rows
        )
        
        if has_rows:
            row_count = len(result["rows"])
            self.assert_test(
                "Query returns expected number of rows",
                row_count == 5,
                f"Expected 5 rows, got {row_count}"
            )
            
            # Check execution metadata
            has_metadata = "execution_time" in result
            self.assert_test(
                "Query result includes execution time",
                has_metadata
            )
    
    def test_join_query(self):
        """Test 5: Execute JOIN query"""
        print("\n[TEST 5] Testing mssql_query (JOIN)...")
        
        query = """
        SELECT 
            c.FirstName, 
            c.LastName, 
            COUNT(o.OrderID) as OrderCount
        FROM test.Customers c
        LEFT JOIN test.Orders o ON c.CustomerID = o.CustomerID
        GROUP BY c.FirstName, c.LastName
        ORDER BY OrderCount DESC
        """
        
        result = self.send_mcp_request("mssql_query", {
            "query": query,
            "database": "TestDB"
        })
        
        has_rows = isinstance(result.get("rows"), list)
        self.assert_test(
            "JOIN query executes successfully",
            has_rows and len(result["rows"]) > 0
        )
    
    def test_query_with_limit(self):
        """Test 6: Test max_rows parameter"""
        print("\n[TEST 6] Testing query row limit...")
        
        result = self.send_mcp_request("mssql_query", {
            "query": "SELECT * FROM test.Products",
            "database": "TestDB",
            "max_rows": 3
        })
        
        if isinstance(result.get("rows"), list):
            row_count = len(result["rows"])
            self.assert_test(
                "Row limit is enforced",
                row_count <= 3,
                f"Expected max 3 rows, got {row_count}"
            )
    
    def test_sql_injection_prevention(self):
        """Test 7: SQL injection prevention"""
        print("\n[TEST 7] Testing SQL injection prevention...")
        
        # Attempt SQL injection
        malicious_queries = [
            "SELECT * FROM test.Customers; DROP TABLE test.Orders;",
            "SELECT * FROM test.Customers WHERE 1=1; DELETE FROM test.Products;",
            "SELECT * FROM test.Customers; EXEC sp_executesql N'DROP TABLE test.Customers';"
        ]
        
        all_blocked = True
        for query in malicious_queries:
            result = self.send_mcp_request("mssql_query", {
                "query": query,
                "database": "TestDB"
            })
            
            # Should return error, not execute
            is_blocked = "error" in result or result.get("success") == False
            if not is_blocked:
                all_blocked = False
                break
        
        self.assert_test(
            "SQL injection attempts are blocked",
            all_blocked,
            "Server should reject multi-statement queries"
        )
    
    def test_write_operation_blocked(self):
        """Test 8: Write operations blocked in read-only mode"""
        print("\n[TEST 8] Testing write operation protection...")
        
        # Test INSERT
        result = self.send_mcp_request("mssql_query", {
            "query": "INSERT INTO test.Customers (FirstName, LastName) VALUES ('Test', 'User')",
            "database": "TestDB"
        })
        
        is_blocked = "error" in result or result.get("success") == False
        self.assert_test(
            "INSERT is blocked in read-only mode",
            is_blocked
        )
        
        # Test UPDATE
        result = self.send_mcp_request("mssql_query", {
            "query": "UPDATE test.Customers SET FirstName='Hacked' WHERE CustomerID=1",
            "database": "TestDB"
        })
        
        is_blocked = "error" in result or result.get("success") == False
        self.assert_test(
            "UPDATE is blocked in read-only mode",
            is_blocked
        )
    
    def test_view_query(self):
        """Test 9: Query against view"""
        print("\n[TEST 9] Testing query against view...")
        
        result = self.send_mcp_request("mssql_query", {
            "query": "SELECT * FROM test.vw_CustomerOrderSummary",
            "database": "TestDB"
        })
        
        has_rows = isinstance(result.get("rows"), list)
        self.assert_test(
            "View query executes successfully",
            has_rows and len(result["rows"]) > 0
        )
    
    def test_connection_resilience(self):
        """Test 10: Connection error handling"""
        print("\n[TEST 10] Testing connection error handling...")
        
        # Try to connect to non-existent database
        result = self.send_mcp_request("mssql_query", {
            "query": "SELECT 1",
            "database": "NonExistentDB"
        })
        
        has_error = "error" in result
        has_message = isinstance(result.get("error"), str) and len(result["error"]) > 0
        
        self.assert_test(
            "Invalid database returns proper error",
            has_error and has_message,
            "Should return descriptive error message"
        )
    
    def run_all_tests(self):
        """Execute all tests"""
        print("=" * 60)
        print("MCP SERVER INTEGRATION TEST SUITE")
        print("=" * 60)
        
        # Wait for services to be ready
        print("\nWaiting for services to be ready...")
        time.sleep(5)
        
        # Run all test methods
        test_methods = [
            self.test_list_databases,
            self.test_list_tables,
            self.test_describe_table,
            self.test_simple_query,
            self.test_join_query,
            self.test_query_with_limit,
            self.test_sql_injection_prevention,
            self.test_write_operation_blocked,
            self.test_view_query,
            self.test_connection_resilience
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"\n✗ EXCEPTION in {test_method.__name__}: {str(e)}")
                self.failed_tests += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"✓ Passed: {self.passed_tests}")
        print(f"✗ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        print("=" * 60)
        
        # Save results to file
        with open('/tmp/test-results.json', 'w') as f:
            json.dump({
                "total": self.passed_tests + self.failed_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "tests": self.test_results
            }, f, indent=2)
        
        # Exit with appropriate code
        sys.exit(0 if self.failed_tests == 0 else 1)

if __name__ == "__main__":
    tester = MCPTester()
    tester.run_all_tests()
```

### Step 4: Create Simple Test Runner Script

**File**: `test-runner.sh`

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "MSSQL MCP Server - Automated Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}[${1}]${NC} ${3}"
}

# Step 1: Clean up any existing containers
print_status "CLEANUP" "$YELLOW" "Removing existing test containers..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# Step 2: Build the MCP server image
print_status "BUILD" "$YELLOW" "Building MCP server Docker image..."
docker build -t mssql-mcp-server:test . || {
    print_status "BUILD" "$RED" "Failed to build Docker image"
    exit 1
}

# Step 3: Start test environment
print_status "START" "$YELLOW" "Starting test environment (MSSQL + MCP Server)..."
docker-compose -f docker-compose.test.yml up -d

# Step 4: Wait for MSSQL to be ready
print_status "WAIT" "$YELLOW" "Waiting for MSSQL database to be ready..."
timeout=60
counter=0
until docker exec mssql-test-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Test1234!@#$' -Q "SELECT 1" > /dev/null 2>&1; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        print_status "WAIT" "$RED" "Timeout waiting for MSSQL database"
        docker-compose -f docker-compose.test.yml logs mssql-test
        docker-compose -f docker-compose.test.yml down -v
        exit 1
    fi
    echo -n "."
done
echo ""
print_status "READY" "$GREEN" "MSSQL database is ready"

# Step 5: Wait for MCP server to be ready
print_status "WAIT" "$YELLOW" "Waiting for MCP server to be ready..."
sleep 10

# Step 6: Run integration tests
print_status "TEST" "$YELLOW" "Running integration tests..."
python3 tests/integration/test_mcp_tools.py

TEST_EXIT_CODE=$?

# Step 7: Save logs
print_status "LOGS" "$YELLOW" "Saving container logs..."
docker-compose -f docker-compose.test.yml logs > test-logs.txt

# Step 8: Cleanup
print_status "CLEANUP" "$YELLOW" "Cleaning up test environment..."
docker-compose -f docker-compose.test.yml down -v

# Step 9: Report results
echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "RESULT" "$GREEN" "All tests passed! ✓"
    echo "=========================================="
    exit 0
else
    print_status "RESULT" "$RED" "Some tests failed! ✗"
    echo "=========================================="
    echo "Check test-logs.txt for details"
    exit 1
fi
```

### Step 5: Quick Test Script for Manual Verification

**File**: `quick-test.sh`

```bash
#!/bin/bash
# Quick manual test script for AI tools

echo "Quick MCP Server Test"
echo "====================="

# Test 1: List databases
echo -e "\n[Test 1] Listing databases..."
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"mssql_list_databases","arguments":{}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

# Test 2: List tables
echo -e "\n[Test 2] Listing tables..."
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"mssql_list_tables","arguments":{"database":"TestDB","schema":"test"}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_DATABASE=TestDB \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

# Test 3: Query data
echo -e "\n[Test 3] Querying customer data..."
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"mssql_query","arguments":{"query":"SELECT TOP 3 * FROM test.Customers","database":"TestDB"}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_DATABASE=TestDB \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

echo -e "\nDone!"
```

### AI Tool Testing Instructions

#### For Claude Code:

1. **Initial Setup**:
```bash
# Clone/create project
cd mssql-mcp-server

# Make scripts executable
chmod +x test-runner.sh quick-test.sh
```

2. **Run Full Test Suite**:
```bash
./test-runner.sh
```

3. **Verify Results**:
   - Check console output for test results
   - Review `test-results.json` for detailed results
   - Check `test-logs.txt` if tests fail

#### For Cursor:

1. **Add Test Task to `.vscode/tasks.json`**:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run MCP Tests",
      "type": "shell",
      "command": "./test-runner.sh",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Quick MCP Test",
      "type": "shell",
      "command": "./quick-test.sh",
      "group": "test"
    }
  ]
}
```

2. **Run via Command Palette**:
   - `Ctrl+Shift+P` → "Tasks: Run Test Task"

### Acceptance Criteria for AI Tools

The AI tool should verify the following before marking the implementation complete:

#### Must Pass (Critical):
- [ ] Docker image builds successfully
- [ ] MSSQL container starts and initializes database
- [ ] MCP server container starts without errors
- [ ] All 10 integration tests pass
- [ ] No security vulnerabilities (SQL injection tests pass)
- [ ] Connection error handling works correctly

#### Should Pass (Important):
- [ ] Test execution completes in under 5 minutes
- [ ] Logs show no ERROR level messages
- [ ] Test results JSON file is generated correctly
- [ ] All expected tables and data exist in test database

#### Nice to Have:
- [ ] Query response time < 100ms for simple queries
- [ ] Memory usage < 500MB for MCP server container
- [ ] All test output is clearly formatted

### AI Tool Validation Commands

**AI tools can execute these commands to validate the implementation**:

```bash
# 1. Verify Docker images exist
docker images | grep mssql-mcp-server

# 2. Check if containers are running
docker ps | grep mssql-test

# 3. Verify MSSQL is accessible
docker exec mssql-test-db /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'Test1234!@#$' \
  -Q "SELECT name FROM sys.databases"

# 4. Check MCP server logs
docker logs mssql-mcp-test

# 5. Verify test database structure
docker exec mssql-test-db /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'Test1234!@#$' \
  -Q "USE TestDB; SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"

# 6. Test MCP server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
docker exec -i mssql-mcp-test python -m mssql_mcp_server

# 7. Check test results
cat test-results.json | jq '.passed, .failed'
```

### Troubleshooting Guide for AI Tools

**Issue: MSSQL container fails to start**
```bash
# Check logs
docker logs mssql-test-db

# Common fix: Increase Docker memory to 4GB minimum
```

**Issue: MCP server can't connect to MSSQL**
```bash
# Verify network connectivity
docker exec mssql-mcp-test ping mssql-test

# Check MSSQL is listening
docker exec mssql-test-db netstat -an | grep 1433
```

**Issue: Tests timeout**
```bash
# Increase timeout in test-runner.sh
# Check system resources
docker stats
```

**Issue: Permission denied on scripts**
```bash
chmod +x test-runner.sh quick-test.sh
```

### Expected Output

**Successful Test Run**:
```
==========================================
MSSQL MCP Server - Automated Test Suite
==========================================

[CLEANUP] Removing existing test containers...
[BUILD] Building MCP server Docker image...
[START] Starting test environment (MSSQL + MCP Server)...
[WAIT] Waiting for MSSQL database to be ready...
[READY] MSSQL database is ready
[TEST] Running integration tests...

============================================================
MCP SERVER INTEGRATION TEST SUITE
============================================================

[TEST 1] Testing mssql_list_databases...
✓ PASS: List databases returns array
✓ PASS: TestDB exists in database list

[TEST 2] Testing mssql_list_tables...
✓ PASS: List tables returns array
✓ PASS: Table 'test.Customers' exists
✓ PASS: Table 'test.Orders' exists
✓ PASS: Table 'test.Products' exists

... (additional tests)

============================================================
TEST SUMMARY
============================================================
Total Tests: 25
✓ Passed: 25
✗ Failed: 0
Success Rate: 100.0%
============================================================

[RESULT] All tests passed! ✓
==========================================
```

This testing strategy provides a complete, automated way for AI tools to validate the MCP server implementation without manual intervention.

## Documentation Requirements

### Doc-1: README.md
- Project description and features
- Quick start guide
- Docker installation steps
- Configuration reference
- Example usage with Claude Desktop
- Troubleshooting section

### Doc-2: SETUP.md
- Detailed installation instructions
- MSSQL server setup (if needed)
- Docker Desktop configuration
- Network configuration
- Windows vs Mac specific instructions

### Doc-3: CONFIGURATION.md
- All environment variables explained
- Connection string options
- Security best practices
- Performance tuning guidelines
- Write operation configuration

### Doc-4: API.md
- Complete MCP tool reference
- Request/response examples
- Error codes and messages
- Resource URI patterns

### Doc-5: IDE-INTEGRATION.md (Required)
- Prerequisites for each IDE (Claude Code, Cursor, Windsurf)
- Step-by-step configuration instructions
- Platform-specific notes (Windows, Mac, Linux)
- Configuration file locations
- Sample configurations for common scenarios
- Troubleshooting IDE-specific issues
- Integration verification steps
- Sample test prompts

## Deployment Scenarios

### Scenario 1: Local Development
- Docker Compose with MSSQL container
- Development database with sample data
- Hot reload for code changes

### Scenario 2: Corporate Network
- Connect to existing MSSQL server
- Support for Windows Authentication (if possible)
- VPN/network considerations
- Proxy support

### Scenario 3: Cloud Deployment
- Connect to Azure SQL Database
- Connect to AWS RDS for SQL Server
- Managed identity support (future)

## Success Criteria

1. Server successfully connects to MSSQL database
2. All core tools (query, list_tables, describe_table) work correctly
3. Docker image builds and runs on both Windows and Mac Docker Desktop
4. Query safety mechanisms prevent unauthorized operations
5. Error handling provides clear, actionable messages
6. Documentation enables setup in under 10 minutes
7. Performance handles 100+ concurrent queries
8. Security tests pass with no vulnerabilities
9. Successfully integrates with Claude Code, Cursor, and Windsurf IDEs
10. Configuration examples work out-of-the-box for each IDE
11. Integration testing checklist passes for all IDEs

## Future Enhancements

1. Support for multiple database connections
2. Query result caching with Redis
3. GraphQL-like query builder
4. SQL query suggestions and auto-completion
5. Integration with Azure Active Directory
6. Backup and restore operations
7. Performance monitoring dashboard
8. Query execution plan analysis
9. Support for temporal tables
10. Change data capture (CDC) integration

## Implementation Priority

### Phase 1: MVP (Priority: High)
- Basic connection management
- Core query tool with safety features
- Schema introspection tools
- Docker containerization
- Basic documentation
- IDE integration guides (Claude Code, Cursor, Windsurf)
- Sample configuration files for all IDEs

### Phase 2: Enterprise Features (Priority: Medium)
- Connection pooling optimization
- Advanced error handling
- Comprehensive logging
- Write operations (with safety)
- Full test coverage

### Phase 3: Advanced Features (Priority: Low)
- Stored procedure execution
- Resource providers
- Caching layer
- Performance metrics
- Advanced authentication

## Notes for Implementation

1. **Security First**: Prioritize security over features. Default to read-only mode.

2. **Error Messages**: Provide helpful error messages that guide users to solutions without exposing system internals.

3. **Performance**: Use async/await patterns throughout. Avoid blocking operations.

4. **Docker Best Practices**: 
   - Use multi-stage builds to minimize image size
   - Run as non-root user
   - Use .dockerignore file
   - Pin dependency versions

5. **MSSQL Specifics**:
   - Handle SQL Server specific data types correctly
   - Support schema-qualified object names (schema.table)
   - Handle case sensitivity settings
   - Support collation differences

6. **MCP Best Practices**:
   - Provide clear tool descriptions
   - Use appropriate parameter types
   - Return structured, consistent responses
   - Handle streaming for large results

7. **Cross-Platform Considerations**:
   - Test on both Windows and Mac Docker Desktop
   - Handle path differences
   - Test network connectivity differences
   - Document platform-specific quirks

8. **IDE Integration**:
   - Provide ready-to-use configuration examples for each IDE
   - Test with actual IDE installations, not just theoretically
   - Document exact file paths for each OS + IDE combination
   - Include troubleshooting section for common IDE-specific issues
   - Provide verification steps after configuration
   - Consider IDE version differences (note minimum versions if applicable)

## License

Recommend: MIT License for maximum adoption

## Support and Maintenance

- GitHub issues for bug reports
- Contribution guidelines
- Code of conduct
- Version release process
- Breaking change policy

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Target Implementation**: Claude Code with MCP SDK
