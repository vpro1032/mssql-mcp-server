import asyncio
import json
from typing import Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl

from src.tools.query import execute_query, QueryParams
from src.tools.introspection import list_databases, list_tables, describe_table, ListTablesParams, DescribeTableParams
from src.tools.advanced import execute_procedure, execute_write, ExecuteProcedureParams, ExecuteWriteParams
from src.database.connection import get_pool_stats
from src.utils.logging import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Create Server instance
server = Server("mssql-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="mssql_query",
            description="Execute a SQL query (SELECT only by default) against the database.",
            inputSchema=QueryParams.model_json_schema(),
        ),
        types.Tool(
            name="mssql_list_databases",
            description="List all accessible databases on the server.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="mssql_list_tables",
            description="List all tables in a specific database and schema.",
            inputSchema=ListTablesParams.model_json_schema(),
        ),
        types.Tool(
            name="mssql_describe_table",
            description="Get detailed schema information for a specific table.",
            inputSchema=DescribeTableParams.model_json_schema(),
        ),
        types.Tool(
            name="mssql_pool_stats",
            description="Get connection pool statistics for monitoring performance.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="mssql_execute_procedure",
            description="Execute a stored procedure with parameters (requires MSSQL_ALLOW_WRITE_OPERATIONS=true).",
            inputSchema=ExecuteProcedureParams.model_json_schema(),
        ),
        types.Tool(
            name="mssql_execute_write",
            description="Execute INSERT, UPDATE, DELETE statements (requires MSSQL_ALLOW_WRITE_OPERATIONS=true).",
            inputSchema=ExecuteWriteParams.model_json_schema(),
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not arguments:
        arguments = {}
        
    try:
        if name == "mssql_query":
            # Extract params manually to ensure defaults work if not provided
            query = arguments.get("query")
            database = arguments.get("database")
            max_rows = arguments.get("max_rows", 1000)
            
            if not query:
                raise ValueError("Query is required")
                
            result = execute_query(query, database, max_rows)
            
            # If result has 'error' key, we might want to return it clearly
            if not result.get("success", True):
                 return [types.TextContent(type="text", text=f"Error: {result.get('error')}")]
                 
            # Format results as JSON string
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, default=str, indent=2)
                )
            ]
            
        elif name == "mssql_list_databases":
            result = list_databases()
            return [types.TextContent(type="text", text=json.dumps({"databases": result}, default=str, indent=2))]
            
        elif name == "mssql_list_tables":
            # schema is optional, default 'dbo'
            schema = arguments.get("schema", "dbo")
            database = arguments.get("database")
            result = list_tables(schema, database)
            return [types.TextContent(type="text", text=json.dumps({"tables": result}, default=str, indent=2))]
            
        elif name == "mssql_describe_table":
            table_name = arguments.get("table_name")
            if not table_name:
                raise ValueError("table_name is required")
            schema = arguments.get("schema", "dbo")
            database = arguments.get("database")
            result = describe_table(table_name, schema, database)
            return [types.TextContent(type="text", text=json.dumps(result, default=str, indent=2))]

        elif name == "mssql_pool_stats":
            stats = get_pool_stats()
            return [types.TextContent(type="text", text=json.dumps(stats, default=str, indent=2))]

        elif name == "mssql_execute_procedure":
            procedure_name = arguments.get("procedure_name")
            if not procedure_name:
                raise ValueError("procedure_name is required")
            parameters = arguments.get("parameters")
            database = arguments.get("database")
            timeout = arguments.get("timeout", 30)
            result = execute_procedure(procedure_name, parameters, database, timeout)
            return [types.TextContent(type="text", text=json.dumps(result, default=str, indent=2))]

        elif name == "mssql_execute_write":
            statement = arguments.get("statement")
            if not statement:
                raise ValueError("statement is required")
            database = arguments.get("database")
            dry_run = arguments.get("dry_run", False)
            result = execute_write(statement, database, dry_run)
            return [types.TextContent(type="text", text=json.dumps(result, default=str, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    # In a real implementation, we might list all schemas/tables as resources
    # For now, we return a template or static list, or dynamically fetch
    # This can be expensive if there are many tables.
    # We will implement a few examples or just leave it dynamic via URI patterns
    return []

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str | bytes:
    # URI format: mssql://schema/{database}/{schema}
    # URI format: mssql://sample/{database}/{schema}/{table}
    
    parsed_path = str(uri).replace("mssql://", "")
    parts = parsed_path.split("/")
    
    resource_type = parts[0]
    
    if resource_type == "schema":
        if len(parts) < 3:
            raise ValueError("Invalid schema URI. Expected: mssql://schema/{database}/{schema}")
        database, schema = parts[1], parts[2]
        tables = list_tables(schema, database)
        return json.dumps(tables, default=str, indent=2)
        
    elif resource_type == "sample":
        if len(parts) < 4:
            raise ValueError("Invalid sample URI. Expected: mssql://sample/{database}/{schema}/{table}")
        database, schema, table = parts[1], parts[2], parts[3]
        query = f"SELECT TOP 10 * FROM [{database}].[{schema}].[{table}]"
        result = execute_query(query, database, 10)
        return json.dumps(result, default=str, indent=2)
        
    raise ValueError(f"Unknown resource type: {resource_type}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mssql-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
