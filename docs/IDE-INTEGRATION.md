# IDE Integration Guide

## Claude Desktop

**Config Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration:**
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
        "--env-file", "/absolute/path/to/.env",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

## Cursor

**Config Location:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp-config.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`

**Configuration:**
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
        "--env-file", "/absolute/path/to/.env",
        "mssql-mcp-server:latest"
      ]
    }
  }
}
```

## Windsurf

**Config Location:** `mcp-servers.json` (see IDE settings)

**Configuration:**
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

