# MSSQL Database MCP Server

An enterprise-grade Model Context Protocol (MCP) server for Microsoft SQL Server. This server enables AI assistants (like Claude, Cursor, Windsurf) to securely interact with MSSQL databases to query data, inspect schemas, and retrieve metadata.

## Features

- **Read-Only by Default**: Strict safety controls to prevent accidental writes.
- **Schema Introspection**: Tools to list databases, tables, and describe table schemas.
- **Secure Authentication**: Supports SQL Server authentication with encryption.
- **Docker Ready**: Easy deployment using Docker or Docker Compose.
- **Comprehensive Logging**: Structured JSON logging for auditing.

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t mssql-mcp-server:latest .
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your MSSQL connection details:
```env
MSSQL_HOST=host.docker.internal
MSSQL_PORT=1433
MSSQL_DATABASE=master
MSSQL_USER=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_ENCRYPT=true
MSSQL_TRUST_SERVER_CERTIFICATE=true
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

## Tools Available

The server exposes the following MCP tools:

### Core Tools (Always Available)

- `mssql_query`: Execute SELECT queries (with safety checks)
- `mssql_list_databases`: List all accessible databases
- `mssql_list_tables`: List tables in a specific database/schema
- `mssql_describe_table`: Get detailed schema information (columns, PKs) for a table
- `mssql_pool_stats`: Get connection pool statistics for monitoring

### Advanced Tools (Require Write Operations Enabled)

⚠️ **These tools require `MSSQL_ALLOW_WRITE_OPERATIONS=true`**

- `mssql_execute_procedure`: Execute stored procedures with parameters
- `mssql_execute_write`: Execute INSERT, UPDATE, DELETE statements with transaction safety

## Performance Features

### Connection Pooling

The server implements intelligent connection pooling for optimal performance:

- **Reusable Connections**: Connections are pooled and reused across queries
- **Thread-Safe**: Safe for concurrent requests
- **Auto-Validation**: Connections are validated before use
- **Configurable Limits**: Control min/max pool size via environment variables
- **Connection Lifetime**: Automatic rotation of long-lived connections
- **Monitoring**: Track pool usage with `mssql_pool_stats` tool

**Configuration:**
```env
MIN_POOL_SIZE=2          # Minimum connections to maintain
MAX_POOL_SIZE=10         # Maximum concurrent connections
IDLE_TIMEOUT=300         # Seconds before idle connection closes
CONNECTION_LIFETIME=1800 # Max lifetime of a connection (30 min)
```

**Monitor Pool Health:**
```json
{
  "total_connections": 5,
  "available_connections": 3,
  "max_connections": 10,
  "min_connections": 2
}
```

## IDE Integration

For detailed integration instructions for Claude Desktop, Cursor, and Windsurf, see [IDE-INTEGRATION.md](IDE-INTEGRATION.md).

### Example Configuration (Generic)

Add this to your IDE's MCP configuration file:

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
        "-e", "MSSQL_USER=sa",
        "-e", "MSSQL_PASSWORD=password",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

## Development & Testing

The project includes an automated test suite that spins up a test MSSQL container.

### Run Tests

```bash
# Make scripts executable
chmod +x test-runner.sh

# Run full integration test suite
./test-runner.sh
```

### Project Structure

- `src/`: Source code
  - `server.py`: Main MCP server entry point
  - `tools/`: MCP tool implementations
  - `database/`: Database connection and validation logic
- `tests/`: Integration tests
- `docker/`: Docker configuration

## Security Notes

- **Write Operations**: Disabled by default. To enable, set `MSSQL_ALLOW_WRITE_OPERATIONS=true`.
- **Credentials**: Never commit `.env` files. Use Docker secrets in production.
- **Network**: Use TLS (`MSSQL_ENCRYPT=true`) for non-local connections.

## Support This Project

If you find this MSSQL MCP Server useful for your projects, please consider supporting its development!

### ☕ Become a Patron

This project is maintained by independent developers. Your support helps us:
- 🚀 Add new features and improvements
- 🐛 Fix bugs and improve stability
- 📚 Create better documentation and tutorials
- 🔒 Enhance security features
- 🎯 Provide faster support and updates

**[Support us on Patreon](https://www.patreon.com/c/Roger3333)**

### Supporter Benefits

Patrons get access to:
- 🎯 **Priority Support** - Get help faster when you need it
- 📝 **Early Access** - Try new features before public release
- 💬 **Direct Communication** - Influence the project roadmap
- 🎓 **Exclusive Tutorials** - Advanced usage guides and examples
- 🏆 **Recognition** - Your name in our SUPPORTERS.md file

### Other Ways to Support

- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and request features via [GitHub Issues](https://github.com/vpro1032/mssql-mcp-server/issues)
- 📖 **Improve documentation** by submitting pull requests
- 💬 **Spread the word** - Share with colleagues and on social media
- ☕ **Buy us a coffee** via [Ko-fi](https://ko-fi.com/your-kofi-link) (one-time donations)

### Enterprise Support

Need dedicated support, custom features, or professional services?

📧 **Contact us:** enterprise@yourdomain.com

We offer:
- Custom feature development
- Priority bug fixes
- On-site training
- Architecture consulting
- SLA-backed support contracts

---

## License

MIT License
