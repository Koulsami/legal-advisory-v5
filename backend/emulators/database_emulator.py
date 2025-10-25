"""
In-Memory Database Emulator for testing.

Provides a simple in-memory database without requiring actual database setup.
Useful for:
- Unit testing
- Integration testing
- Development without database
- CI/CD pipelines
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class InMemoryDatabase:
    """
    Simple in-memory database emulator.
    
    Supports basic CRUD operations and simple SQL parsing.
    """
    
    def __init__(self):
        """Initialize in-memory database"""
        self._tables: Dict[str, List[Dict[str, Any]]] = {}
        self._auto_increment: Dict[str, int] = {}
        self._transaction_active = False
        self._transaction_backup: Optional[Dict] = None
    
    async def execute(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query.
        
        Supports basic operations: SELECT, INSERT, UPDATE, DELETE, CREATE TABLE
        """
        query = query.strip()
        query_upper = query.upper()
        
        if query_upper.startswith("SELECT"):
            return self._execute_select(query, params)
        elif query_upper.startswith("INSERT"):
            return self._execute_insert(query, params)
        elif query_upper.startswith("UPDATE"):
            return self._execute_update(query, params)
        elif query_upper.startswith("DELETE"):
            return self._execute_delete(query, params)
        elif query_upper.startswith("CREATE TABLE"):
            return self._execute_create_table(query)
        else:
            raise ValueError(f"Unsupported query type: {query}")
    
    def _execute_select(self, query: str, params: Optional[Tuple]) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        # Simple parsing: SELECT * FROM table_name WHERE condition
        match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT query: table name not found")
        
        table_name = match.group(1)
        
        if table_name not in self._tables:
            return []
        
        results = self._tables[table_name].copy()
        
        # Simple WHERE clause support
        where_match = re.search(r'WHERE\s+(.+)', query, re.IGNORECASE)
        if where_match and params:
            where_clause = where_match.group(1)
            # Very simple: field = ?
            field_match = re.search(r'(\w+)\s*=\s*\?', where_clause)
            if field_match:
                field_name = field_match.group(1)
                filter_value = params[0]
                results = [row for row in results if row.get(field_name) == filter_value]
        
        return results
    
    def _execute_insert(self, query: str, params: Optional[Tuple]) -> List[Dict[str, Any]]:
        """Execute INSERT query"""
        # Parse: INSERT INTO table_name (col1, col2) VALUES (?, ?)
        match = re.search(r'INSERT\s+INTO\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT query")
        
        table_name = match.group(1)
        
        if table_name not in self._tables:
            self._tables[table_name] = []
        
        # Extract column names
        cols_match = re.search(r'\(([^)]+)\)\s+VALUES', query, re.IGNORECASE)
        if cols_match and params:
            columns = [col.strip() for col in cols_match.group(1).split(',')]
            
            # Create row dict
            row = {}
            for i, col in enumerate(columns):
                if i < len(params):
                    row[col] = params[i]
            
            # Add auto-increment ID if not provided
            if 'id' not in row:
                if table_name not in self._auto_increment:
                    self._auto_increment[table_name] = 1
                row['id'] = self._auto_increment[table_name]
                self._auto_increment[table_name] += 1
            
            # Add timestamp
            row['created_at'] = datetime.now().isoformat()
            
            self._tables[table_name].append(row)
            
            return [row]
        
        return []
    
    def _execute_update(self, query: str, params: Optional[Tuple]) -> List[Dict[str, Any]]:
        """Execute UPDATE query"""
        # Parse: UPDATE table_name SET col1 = ? WHERE condition
        match = re.search(r'UPDATE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE query")
        
        table_name = match.group(1)
        
        if table_name not in self._tables:
            return []
        
        # Simple SET clause
        set_match = re.search(r'SET\s+(\w+)\s*=\s*\?', query, re.IGNORECASE)
        where_match = re.search(r'WHERE\s+(\w+)\s*=\s*\?', query, re.IGNORECASE)
        
        if set_match and params and len(params) >= 1:
            set_field = set_match.group(1)
            set_value = params[0]
            
            updated_rows = []
            
            for row in self._tables[table_name]:
                # Simple WHERE condition
                if where_match and len(params) >= 2:
                    where_field = where_match.group(1)
                    where_value = params[1]
                    if row.get(where_field) == where_value:
                        row[set_field] = set_value
                        row['updated_at'] = datetime.now().isoformat()
                        updated_rows.append(row)
                else:
                    # Update all rows
                    row[set_field] = set_value
                    row['updated_at'] = datetime.now().isoformat()
                    updated_rows.append(row)
            
            return updated_rows
        
        return []
    
    def _execute_delete(self, query: str, params: Optional[Tuple]) -> List[Dict[str, Any]]:
        """Execute DELETE query"""
        # Parse: DELETE FROM table_name WHERE condition
        match = re.search(r'DELETE\s+FROM\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE query")
        
        table_name = match.group(1)
        
        if table_name not in self._tables:
            return []
        
        where_match = re.search(r'WHERE\s+(\w+)\s*=\s*\?', query, re.IGNORECASE)
        
        if where_match and params:
            where_field = where_match.group(1)
            where_value = params[0]
            
            deleted_rows = [row for row in self._tables[table_name] 
                          if row.get(where_field) == where_value]
            
            self._tables[table_name] = [row for row in self._tables[table_name] 
                                       if row.get(where_field) != where_value]
            
            return deleted_rows
        
        return []
    
    def _execute_create_table(self, query: str) -> List[Dict[str, Any]]:
        """Execute CREATE TABLE query"""
        match = re.search(r'CREATE\s+TABLE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE query")
        
        table_name = match.group(1)
        self._tables[table_name] = []
        self._auto_increment[table_name] = 1
        
        return []
    
    def begin_transaction(self):
        """Begin a transaction"""
        self._transaction_active = True
        # Deep copy current state
        import copy
        self._transaction_backup = copy.deepcopy(self._tables)
    
    def commit(self):
        """Commit transaction"""
        self._transaction_active = False
        self._transaction_backup = None
    
    def rollback(self):
        """Rollback transaction"""
        if self._transaction_backup:
            self._tables = self._transaction_backup
        self._transaction_active = False
        self._transaction_backup = None
    
    def get_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all rows from a table"""
        return self._tables.get(table_name, [])
    
    def clear_table(self, table_name: str):
        """Clear all data from a table"""
        if table_name in self._tables:
            self._tables[table_name] = []
    
    def clear_all(self):
        """Clear all tables"""
        self._tables = {}
        self._auto_increment = {}
    
    async def health_check(self) -> bool:
        """Check database health (always healthy)"""
        return True
