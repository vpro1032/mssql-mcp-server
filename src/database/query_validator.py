import re
from typing import Tuple, Optional

class QueryValidator:
    """
    Validates SQL queries for safety and security.
    """
    
    # Patterns for dangerous operations
    DANGEROUS_PATTERNS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bALTER\b", 
        r"\bCREATE\b", r"\bGRANT\b", r"\bREVOKE\b", r"\bEXEC\b", 
        r"\bEXECUTE\b", r"\bxp_cmdshell\b", r"\bsp_configure\b"
    ]
    
    # Pattern for multiple statements (semicolon not inside quotes)
    MULTI_STATEMENT_PATTERN = r";(?=(?:[^']*'[^']*')*[^']*$)"
    
    def __init__(self, allow_write: bool = False):
        self.allow_write = allow_write

    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validates a query string.
        Returns: (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"

        # Check for multiple statements
        if re.search(self.MULTI_STATEMENT_PATTERN, query):
             return False, "Multiple statements are not allowed"

        normalized_query = query.upper()
        
        # If write operations are not allowed, enforce strictly read-only
        if not self.allow_write:
            # Must start with SELECT or WITH (for CTEs)
            if not (normalized_query.strip().startswith("SELECT") or 
                    normalized_query.strip().startswith("WITH")):
                
                # Check for INSERT/UPDATE explicitly if it didn't start with SELECT
                if "INSERT" in normalized_query or "UPDATE" in normalized_query:
                     return False, "Write operations (INSERT, UPDATE) are not allowed in read-only mode"
                
                # Check other dangerous patterns
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, normalized_query, re.IGNORECASE):
                        return False, f"Operation not allowed: {pattern.replace(r'\\b', '')}"
            
            # Double check for dangerous keywords even in SELECTs (e.g. into outfile, subqueries with exec)
            # This is a basic check; parameterized queries are the real defense
            if "xp_cmdshell" in query.lower():
                return False, "Dangerous stored procedure execution is not allowed"

        return True, None

    def is_select_statement(self, query: str) -> bool:
        return query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("WITH")
