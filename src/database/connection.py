import pyodbc
import logging
from contextlib import contextmanager
from typing import Generator, Optional, Any, List, Dict
import time
import threading
from queue import Queue, Empty
from datetime import datetime, timedelta
from src.utils.config import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class ConnectionPool:
    """
    Thread-safe connection pool for pyodbc connections.
    """

    def __init__(self, connection_string: str, min_size: int = 2, max_size: int = 10,
                 idle_timeout: int = 300, connection_lifetime: int = 1800):
        self.connection_string = connection_string
        self.min_size = min_size
        self.max_size = max_size
        self.idle_timeout = idle_timeout  # seconds before idle connection is closed
        self.connection_lifetime = connection_lifetime  # max lifetime of a connection

        self._pool = Queue(maxsize=max_size)
        self._connection_count = 0
        self._lock = threading.Lock()

        # Initialize minimum connections
        self._initialize_pool()
        logger.info(f"Connection pool initialized with min={min_size}, max={max_size}")

    def _initialize_pool(self):
        """Create minimum number of connections at startup."""
        with self._lock:
            for _ in range(self.min_size):
                try:
                    conn_wrapper = self._create_connection()
                    self._pool.put(conn_wrapper)
                except Exception as e:
                    logger.error(f"Failed to initialize connection: {str(e)}")

    def _create_connection(self) -> Dict[str, Any]:
        """Create a new connection with metadata."""
        conn = pyodbc.connect(self.connection_string)
        self._connection_count += 1

        return {
            'connection': conn,
            'created_at': datetime.now(),
            'last_used': datetime.now()
        }

    def _is_connection_valid(self, conn_wrapper: Dict[str, Any]) -> bool:
        """Check if connection is still valid and not expired."""
        try:
            # Check if connection is alive
            cursor = conn_wrapper['connection'].cursor()
            cursor.execute("SELECT 1")
            cursor.close()

            # Check if connection has exceeded lifetime
            age = datetime.now() - conn_wrapper['created_at']
            if age.total_seconds() > self.connection_lifetime:
                logger.debug("Connection exceeded lifetime, will be replaced")
                return False

            return True
        except Exception as e:
            logger.debug(f"Connection validation failed: {str(e)}")
            return False

    @contextmanager
    def get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        """
        Get a connection from the pool.
        Automatically returns it to the pool when done.
        """
        conn_wrapper = None

        try:
            # Try to get existing connection from pool
            try:
                conn_wrapper = self._pool.get(block=True, timeout=5)

                # Validate connection
                if not self._is_connection_valid(conn_wrapper):
                    logger.debug("Replacing invalid connection")
                    try:
                        conn_wrapper['connection'].close()
                    except:
                        pass
                    with self._lock:
                        self._connection_count -= 1
                    conn_wrapper = self._create_connection()

            except Empty:
                # Pool is empty, create new connection if under max
                with self._lock:
                    if self._connection_count < self.max_size:
                        conn_wrapper = self._create_connection()
                        logger.debug(f"Created new connection (total: {self._connection_count})")
                    else:
                        # Wait for a connection to become available
                        logger.warning("Connection pool exhausted, waiting...")
                        conn_wrapper = self._pool.get(block=True)

            # Update last used time
            conn_wrapper['last_used'] = datetime.now()

            # Yield the actual connection
            yield conn_wrapper['connection']

        except Exception as e:
            logger.error(f"Error getting connection from pool: {str(e)}")
            # If connection is bad, don't return it to pool
            if conn_wrapper:
                try:
                    conn_wrapper['connection'].close()
                except:
                    pass
                with self._lock:
                    self._connection_count -= 1
            raise
        else:
            # Return connection to pool
            if conn_wrapper:
                try:
                    self._pool.put(conn_wrapper, block=False)
                except:
                    # Pool is full, close this connection
                    try:
                        conn_wrapper['connection'].close()
                    except:
                        pass
                    with self._lock:
                        self._connection_count -= 1

    def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all connections in pool")
        while not self._pool.empty():
            try:
                conn_wrapper = self._pool.get(block=False)
                conn_wrapper['connection'].close()
                with self._lock:
                    self._connection_count -= 1
            except Empty:
                break
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            'total_connections': self._connection_count,
            'available_connections': self._pool.qsize(),
            'max_connections': self.max_size,
            'min_connections': self.min_size
        }


class DatabaseConnection:
    _instance = None
    _pool = None

    def __init__(self):
        self.settings = get_settings()
        self._connection_string = self._build_connection_string()

        # Initialize connection pool
        if DatabaseConnection._pool is None:
            DatabaseConnection._pool = ConnectionPool(
                connection_string=self._connection_string,
                min_size=self.settings.MIN_POOL_SIZE,
                max_size=self.settings.MAX_POOL_SIZE,
                idle_timeout=self.settings.IDLE_TIMEOUT,
                connection_lifetime=self.settings.CONNECTION_LIFETIME
            )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def _build_connection_string(self) -> str:
        driver = "{ODBC Driver 18 for SQL Server}"
        # Construct connection string
        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={self.settings.MSSQL_HOST},{self.settings.MSSQL_PORT};"
            f"DATABASE={self.settings.MSSQL_DATABASE};"
            f"UID={self.settings.MSSQL_USER};"
            f"PWD={self.settings.MSSQL_PASSWORD};"
            f"Encrypt={'yes' if self.settings.MSSQL_ENCRYPT else 'no'};"
            f"TrustServerCertificate={'yes' if self.settings.MSSQL_TRUST_SERVER_CERTIFICATE else 'no'};"
            f"Connection Timeout={self.settings.MSSQL_CONNECTION_TIMEOUT};"
        )
        return conn_str

    @contextmanager
    def get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        """
        Yields a database connection from the connection pool.
        The connection is automatically returned to the pool when done.
        """
        with self._pool.get_connection() as conn:
            yield conn

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self._pool.get_stats()

    def execute_query(self, query: str, params: tuple = (), dictionary: bool = True) -> List[Dict[str, Any]]:
        """
        Executes a query and returns a list of dictionaries (rows).
        """
        start_time = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    rows = []
                    for row in cursor.fetchall():
                        if dictionary:
                            rows.append(dict(zip(columns, row)))
                        else:
                            rows.append(row)
                    
                    duration = time.time() - start_time
                    logger.info(f"Query executed in {duration:.3f}s: {query[:50]}...")
                    return rows
                else:
                    # No result set (e.g. INSERT/UPDATE)
                    conn.commit()
                    return [{"rows_affected": cursor.rowcount}]
            except pyodbc.Error as e:
                logger.error(f"Query execution error: {str(e)}")
                raise
            finally:
                cursor.close()

def get_db_connection():
    return DatabaseConnection.get_instance()

def get_pool_stats():
    """Get connection pool statistics for monitoring."""
    db = get_db_connection()
    return db.get_pool_stats()
