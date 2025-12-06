from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.database.connection import get_db_connection
from src.database.query_validator import QueryValidator
from src.utils.config import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class QueryParams(BaseModel):
    query: str = Field(..., description="SQL SELECT statement")
    database: Optional[str] = Field(None, description="Target database (overrides default)")
    max_rows: int = Field(1000, description="Maximum rows to return (default 1000)")

def execute_query(query: str, database: Optional[str] = None, max_rows: int = 1000) -> Dict[str, Any]:
    """
    Execute a SELECT query with safety constraints.
    """
    settings = get_settings()
    validator = QueryValidator(allow_write=settings.MSSQL_ALLOW_WRITE_OPERATIONS)
    
    # Validate Query
    is_valid, error = validator.validate_query(query)
    if not is_valid:
        return {"error": error, "success": False}
        
    db = get_db_connection()
    
    # Enforce row limit in query if possible, or post-process
    # Adding TOP to query is complex with regex, so we'll fetch and truncate for now
    # or let the user handle TOP. 
    # Better approach: We can check if TOP is present, if not add it, but that's risky with parsing.
    # We will simply truncate the result set in Python to avoid memory issues.
    
    final_query = query
    if database:
        # NOTE: This assumes the connection user has rights to USE database or access it.
        # It's better to qualify tables, but we can't easily parse that.
        # We'll prepend 'USE [Database];' if it's a single batch, but python driver might not like that 
        # combined with fetchall if it returns multiple result sets.
        # Safest way without changing connection: 
        # We rely on cross-database queries (SELECT * FROM [DB].[Schema].[Table])
        # If the user provided `database`, we expect them to either have fully qualified names
        # OR we try to run `USE {database}` first.
        # Since pyodbc supports executing 'USE' as a separate command on same cursor:
        pass 
        
    try:
        start_time = 0
        import time
        start_time = time.time()
        
        # We use a context manager for connection to allow 'USE' if needed
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if database:
                cursor.execute(f"USE [{database}]")
            
            cursor.execute(final_query)
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = []
                count = 0
                for row in cursor:
                    if count >= max_rows:
                        break
                    # Convert row values to be JSON serializable
                    row_dict = {}
                    for i, val in enumerate(row):
                         # Handle types that might not serialize well (datetime, decimals)
                         # Simple strategy: str() them if needed, or let Pydantic/JSON encoder handle basic types
                         # For now we map to dict
                         row_dict[columns[i]] = val
                    rows.append(row_dict)
                    count += 1
                
                execution_time = time.time() - start_time
                
                return {
                    "rows": rows,
                    "columns": columns,
                    "row_count": len(rows),
                    "execution_time": execution_time,
                    "success": True
                }
            else:
                # No results
                return {
                    "rows": [],
                    "row_count": 0,
                    "success": True
                }
                
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        return {
            "error": str(e),
            "success": False
        }

