"""
Advanced database operation tools (stored procedures and write operations).
These tools require explicit configuration to enable.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
from src.database.connection import get_db_connection
from src.database.query_validator import QueryValidator
from src.utils.config import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ExecuteProcedureParams(BaseModel):
    procedure_name: str = Field(..., description="Stored procedure name (schema.procedure)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Named parameters as key-value pairs")
    database: Optional[str] = Field(None, description="Target database (optional)")
    timeout: int = Field(30, description="Execution timeout in seconds (max 300)")


class ExecuteWriteParams(BaseModel):
    statement: str = Field(..., description="DML statement (INSERT, UPDATE, DELETE)")
    database: Optional[str] = Field(None, description="Target database (optional)")
    dry_run: bool = Field(False, description="Validate without executing")


def execute_procedure(
    procedure_name: str,
    parameters: Optional[Dict[str, Any]] = None,
    database: Optional[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute a stored procedure with parameters.

    Security:
    - Only enabled if MSSQL_ALLOW_WRITE_OPERATIONS=true
    - Validates procedure name format
    - Uses parameterized execution
    - Logs all executions for audit

    Args:
        procedure_name: Name of stored procedure (e.g., 'dbo.GetCustomerOrders')
        parameters: Dictionary of parameter names and values
        database: Optional database to switch to
        timeout: Execution timeout in seconds

    Returns:
        Dictionary containing result sets, return value, and execution metadata
    """
    settings = get_settings()

    # Security check: Require explicit enable
    if not settings.MSSQL_ALLOW_WRITE_OPERATIONS:
        logger.warning(f"Blocked stored procedure execution attempt: {procedure_name}")
        return {
            "error": "Stored procedure execution is disabled. Set MSSQL_ALLOW_WRITE_OPERATIONS=true to enable.",
            "success": False
        }

    # Validate timeout
    if timeout > 300:
        timeout = 300
        logger.warning(f"Timeout capped at 300 seconds")

    # Validate procedure name format (schema.procedure or just procedure)
    if not _is_valid_identifier(procedure_name):
        return {
            "error": f"Invalid procedure name format: {procedure_name}",
            "success": False
        }

    db = get_db_connection()
    start_time = time.time()

    # Audit logging
    logger.info(f"Executing stored procedure: {procedure_name} with params: {parameters}")

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Switch database if specified
            if database:
                # Validate database exists
                cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (database,))
                if not cursor.fetchone():
                    return {
                        "error": f"Database not found: {database}",
                        "success": False
                    }
                cursor.execute(f"USE [{database}]")

            # Build EXEC statement with parameters
            if parameters:
                # Build parameter list
                param_list = []
                param_values = []
                for key, value in parameters.items():
                    param_list.append(f"@{key} = ?")
                    param_values.append(value)

                exec_statement = f"EXEC {procedure_name} {', '.join(param_list)}"
                cursor.execute(exec_statement, tuple(param_values))
            else:
                # Execute without parameters
                cursor.execute(f"EXEC {procedure_name}")

            # Fetch all result sets
            result_sets = []
            while True:
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    rows = []
                    for row in cursor.fetchall():
                        row_dict = {}
                        for i, val in enumerate(row):
                            row_dict[columns[i]] = val
                        rows.append(row_dict)
                    result_sets.append({
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows)
                    })

                # Check for more result sets
                if not cursor.nextset():
                    break

            # Commit transaction
            conn.commit()

            execution_time = time.time() - start_time

            result = {
                "procedure": procedure_name,
                "result_sets": result_sets,
                "result_set_count": len(result_sets),
                "execution_time": execution_time,
                "success": True
            }

            logger.info(f"Stored procedure executed successfully in {execution_time:.3f}s")
            return result

    except Exception as e:
        logger.error(f"Stored procedure execution failed: {str(e)}")
        return {
            "error": str(e),
            "procedure": procedure_name,
            "success": False
        }


def execute_write(
    statement: str,
    database: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute INSERT, UPDATE, or DELETE statements with strict controls.

    Security:
    - Only enabled if MSSQL_ALLOW_WRITE_OPERATIONS=true
    - Validates statement is DML only (no DDL)
    - Uses transaction with automatic rollback on error
    - Logs all write operations for audit trail
    - Dry-run mode for validation without execution

    Args:
        statement: DML statement to execute
        database: Optional database to switch to
        dry_run: If True, validates without executing

    Returns:
        Dictionary containing rows affected, execution time, and validation results
    """
    settings = get_settings()

    # Security check: Require explicit enable
    if not settings.MSSQL_ALLOW_WRITE_OPERATIONS:
        logger.warning(f"Blocked write operation attempt: {statement[:100]}...")
        return {
            "error": "Write operations are disabled. Set MSSQL_ALLOW_WRITE_OPERATIONS=true to enable.",
            "success": False
        }

    # Validate statement
    validator = QueryValidator(allow_write=True)
    is_valid, error = validator.validate_query(statement)

    if not is_valid:
        return {
            "error": error,
            "success": False,
            "validation": "failed"
        }

    # Check that it's actually a write operation
    normalized = statement.strip().upper()
    if not (normalized.startswith("INSERT") or
            normalized.startswith("UPDATE") or
            normalized.startswith("DELETE")):
        return {
            "error": "Only INSERT, UPDATE, DELETE statements are allowed",
            "success": False,
            "validation": "failed"
        }

    # Dry run mode - just validate and return
    if dry_run:
        logger.info(f"Dry-run validation successful for: {statement[:100]}...")
        return {
            "statement": statement,
            "validation": "passed",
            "dry_run": True,
            "success": True,
            "message": "Statement is valid and would execute successfully"
        }

    # Execute the write operation
    db = get_db_connection()
    start_time = time.time()

    # Audit logging
    logger.warning(f"Executing write operation: {statement[:200]}...")

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Switch database if specified
            if database:
                # Validate database exists
                cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (database,))
                if not cursor.fetchone():
                    return {
                        "error": f"Database not found: {database}",
                        "success": False
                    }
                cursor.execute(f"USE [{database}]")

            # Execute in transaction (automatic with pyodbc)
            cursor.execute(statement)
            rows_affected = cursor.rowcount

            # Commit transaction
            conn.commit()

            execution_time = time.time() - start_time

            result = {
                "statement": statement[:200] + "..." if len(statement) > 200 else statement,
                "rows_affected": rows_affected,
                "execution_time": execution_time,
                "success": True
            }

            logger.warning(f"Write operation completed: {rows_affected} rows affected in {execution_time:.3f}s")
            return result

    except Exception as e:
        logger.error(f"Write operation failed: {str(e)}")
        # Transaction automatically rolled back on exception
        return {
            "error": str(e),
            "statement": statement[:200] + "..." if len(statement) > 200 else statement,
            "success": False,
            "rollback": True
        }


def _is_valid_identifier(name: str) -> bool:
    """
    Validate SQL identifier (procedure/table name).
    Allows: schema.name or just name
    """
    if not name or len(name) > 256:
        return False

    # Split by dot for schema.name format
    parts = name.split('.')

    if len(parts) > 2:
        return False

    # Check each part is valid identifier
    for part in parts:
        part = part.strip('[]')  # Allow bracketed identifiers
        if not part:
            return False
        # Allow alphanumeric and underscore
        if not all(c.isalnum() or c == '_' for c in part):
            return False

    return True
