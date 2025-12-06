from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.database.connection import get_db_connection
from src.utils.logging import get_logger

logger = get_logger(__name__)

class ListTablesParams(BaseModel):
    database: Optional[str] = Field(None, description="Target database (optional)")
    schema: str = Field("dbo", description="Schema name (default 'dbo')")

class DescribeTableParams(BaseModel):
    table_name: str = Field(..., description="Table name")
    schema: str = Field("dbo", description="Schema name (default 'dbo')")
    database: Optional[str] = Field(None, description="Target database (optional)")

def list_databases() -> List[Dict[str, Any]]:
    """List all accessible databases on the server."""
    db = get_db_connection()
    query = """
    SELECT 
        name,
        state_desc as state,
        recovery_model_desc as recovery_model,
        compatibility_level
    FROM sys.databases
    WHERE state = 0  -- Online
    ORDER BY name
    """
    return db.execute_query(query)

def list_tables(schema: str = "dbo", database: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all tables in the specified database and schema."""
    db = get_db_connection()
    
    # If database is specified, we need to switch context or qualify the query
    # Ideally, we should switch connection context, but for simplicity here we assume
    # the connection allows cross-db access or we rely on the default DB.
    # A safer way in MSSQL is to change the query to use the DB prefix if valid.
    
    db_prefix = f"[{database}]." if database else ""
    
    query = f"""
    SELECT 
        t.name as table_name,
        s.name as schema_name,
        t.create_date,
        t.modify_date,
        (SELECT SUM(row_count) FROM {db_prefix}sys.dm_db_partition_stats WHERE object_id = t.object_id AND index_id < 2) as row_count
    FROM {db_prefix}sys.tables t
    JOIN {db_prefix}sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = ?
    ORDER BY t.name
    """
    
    return db.execute_query(query, (schema,))

def describe_table(table_name: str, schema: str = "dbo", database: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed schema information for a specific table."""
    db = get_db_connection()
    db_prefix = f"[{database}]." if database else ""
    
    # Get columns
    cols_query = f"""
    SELECT 
        c.name,
        ty.name as type,
        c.max_length,
        c.is_nullable,
        object_definition(c.default_object_id) as default_value
    FROM {db_prefix}sys.columns c
    JOIN {db_prefix}sys.types ty ON c.user_type_id = ty.user_type_id
    JOIN {db_prefix}sys.tables t ON c.object_id = t.object_id
    JOIN {db_prefix}sys.schemas s ON t.schema_id = s.schema_id
    WHERE t.name = ? AND s.name = ?
    ORDER BY c.column_id
    """
    columns = db.execute_query(cols_query, (table_name, schema))
    
    # Get Primary Keys
    pk_query = f"""
    SELECT c.name
    FROM {db_prefix}sys.indexes i
    JOIN {db_prefix}sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    JOIN {db_prefix}sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    JOIN {db_prefix}sys.tables t ON i.object_id = t.object_id
    JOIN {db_prefix}sys.schemas s ON t.schema_id = s.schema_id
    WHERE i.is_primary_key = 1
    AND t.name = ? AND s.name = ?
    """
    pks = db.execute_query(pk_query, (table_name, schema))
    primary_keys = [row['name'] for row in pks]
    
    return {
        "table": table_name,
        "schema": schema,
        "columns": columns,
        "primary_key": primary_keys
    }

