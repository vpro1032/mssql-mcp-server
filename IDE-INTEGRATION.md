# MSSQL MCP Server - IDE Integration Guide

This guide provides step-by-step instructions for integrating the MSSQL MCP Server with popular AI-powered IDEs.

## Prerequisites

1. **Docker Desktop**: Installed and running on your machine.
2. **MSSQL Server**: Access to a running SQL Server instance (local or remote).
3. **MCP Server Image**: Built locally or pulled from registry.
   ```bash
   # Build locally
   docker build -t mssql-mcp-server:latest .
   ```

---

## 1. Claude Desktop Integration

**Configuration Location**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
Add the following to your `claude_desktop_config.json`:

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
        "-e", "MSSQL_DATABASE=master",
        "-e", "MSSQL_USER=sa",
        "-e", "MSSQL_PASSWORD=YourPassword",
        "-e", "MSSQL_ENCRYPT=true",
        "-e", "MSSQL_TRUST_SERVER_CERTIFICATE=false",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

> **Note**: Replace credentials with your actual database details. For macOS Docker Desktop, `localhost` usually works if using `--network host`, otherwise use `host.docker.internal`.

---

## 2. Cursor IDE Integration

**Configuration Location**:
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp-config.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp-config.json`

**Configuration**:
Add to `mcp-config.json`:

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
        "-e", "MSSQL_HOST=host.docker.internal",
        "-e", "MSSQL_PORT=1433", 
        "-e", "MSSQL_DATABASE=master",
        "-e", "MSSQL_USER=sa",
        "-e", "MSSQL_PASSWORD=YourPassword",
        "-e", "MSSQL_TRUST_SERVER_CERTIFICATE=true",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

---

## 3. Windsurf IDE Integration

**Configuration Location**:
- Windows: `%APPDATA%\Windsurf\mcp-servers.json`
- Mac: `~/Library/Application Support/Windsurf/mcp-servers.json`
- Linux: `~/.config/Windsurf/mcp-servers.json`

**Configuration**:

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
      ]
    }
  }
}
```

---

## Troubleshooting

### Connection Refused
- **Check Docker Network**: Ensure you are using `--network host` if connecting to `localhost`.
- **Check Hostname**: On Mac/Windows, use `host.docker.internal` to refer to the host machine from within a container.
- **Check Firewall**: Ensure port 1433 is open.

### Authentication Failed
- Verify `MSSQL_USER` and `MSSQL_PASSWORD`.
- If using a self-signed certificate (common in dev), set `MSSQL_TRUST_SERVER_CERTIFICATE=true`.

### "Tool not found"
- Restart your IDE completely to reload MCP configuration.
- Check IDE logs for initialization errors.

## Verification

Ask your AI assistant:
> "List all databases on my SQL Server."
> "Describe the schema of table X."

