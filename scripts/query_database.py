#!/usr/bin/env python3
"""
Database Query Script for Todo Webapp

Queries the MySQL database to check data inside tables.
"""

from __future__ import annotations

import sys
from typing import Optional

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("Error: mysql-connector-python not installed")
    print("Install it with: pip install mysql-connector-python")
    sys.exit(1)


# Database connection details from context.xml
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "todo",
    "user": "todo",
    "password": "todo",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}


def get_connection() -> Optional[mysql.connector.MySQLConnection]:
    """
    Create database connection.

    Returns:
        MySQL connection or None if failed
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    return None


def query_table(
    connection: mysql.connector.MySQLConnection, table_name: str, limit: int = 10
) -> list:
    """
    Query all data from a table.

    Args:
        connection: Database connection
        table_name: Name of the table
        limit: Maximum number of rows to return

    Returns:
        List of tuples (rows)
    """
    cursor = connection.cursor()
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]
        return columns, rows
    except Error as e:
        print(f"Error querying {table_name}: {e}")
        return [], []
    finally:
        cursor.close()


def get_table_schema(
    connection: mysql.connector.MySQLConnection, table_name: str
) -> list:
    """
    Get table schema information.

    Args:
        connection: Database connection
        table_name: Name of the table

    Returns:
        List of column information tuples
    """
    cursor = connection.cursor()
    try:
        query = f"DESCRIBE {table_name}"
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error getting schema for {table_name}: {e}")
        return []
    finally:
        cursor.close()


def count_rows(connection: mysql.connector.MySQLConnection, table_name: str) -> int:
    """
    Count rows in a table.

    Args:
        connection: Database connection
        table_name: Name of the table

    Returns:
        Row count
    """
    cursor = connection.cursor()
    try:
        query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error counting rows in {table_name}: {e}")
        return -1
    finally:
        cursor.close()


def list_tables(connection: mysql.connector.MySQLConnection) -> list:
    """
    List all tables in the database.

    Args:
        connection: Database connection

    Returns:
        List of table names
    """
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error listing tables: {e}")
        return []
    finally:
        cursor.close()


def print_table_data(columns: list, rows: list, table_name: str) -> None:
    """
    Pretty print table data.

    Args:
        columns: Column names
        rows: Row data
        table_name: Table name for header
    """
    if not columns or not rows:
        print(f"  No data in {table_name}")
        return

    print(f"\n{'=' * 80}")
    print(f"Table: {table_name.upper()}")
    print(f"Columns: {len(columns)}, Rows: {len(rows)}")
    print("=" * 80)

    # Print column headers
    header = " | ".join(f"{col:20}" for col in columns)
    print(header)
    print("-" * len(header))

    # Print rows (mask sensitive data)
    for row in rows:
        row_str = []
        for i, col in enumerate(columns):
            value = row[i]
            if value is None:
                value = "NULL"
            elif col.lower() in ["password", "password_salt"]:
                value = "[HIDDEN]"
            elif isinstance(value, bytes):
                value = f"[BINARY {len(value)} bytes]"
            elif isinstance(value, str) and len(str(value)) > 30:
                value = str(value)[:27] + "..."
            else:
                value = str(value)
            row_str.append(f"{value:20}")
        print(" | ".join(row_str))


def main() -> int:
    """Main entry point."""
    print("=" * 80)
    print("DATABASE QUERY TOOL - Todo Webapp")
    print("=" * 80)
    print(
        f"\nConnecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    print(f"User: {DB_CONFIG['user']}")
    print()

    connection = get_connection()
    if not connection:
        print("✗ Failed to connect to database")
        print("\nPossible issues:")
        print("  1. MySQL server is not running")
        print("  2. Database 'todo' does not exist")
        print("  3. User 'todo' does not have access")
        print("  4. Wrong password")
        return 1

    print("✓ Connected to database")

    try:
        # List all tables
        print("\n" + "=" * 80)
        print("DATABASE TABLES")
        print("=" * 80)
        tables = list_tables(connection)

        if not tables:
            print("No tables found in database")
            return 0

        print(f"\nFound {len(tables)} table(s):")
        for table in tables:
            count = count_rows(connection, table)
            print(f"  - {table}: {count} row(s)")

        # Query main tables
        main_tables = [
            "ACCOUNTS",
            "TASKS",
            "ACCOUNT_SESSIONS",
            "ACCOUNT_STATUSES",
            "TASK_STATUSES",
            "TASK_PRIORITIES",
        ]

        for table_name in main_tables:
            if table_name.lower() in [t.lower() for t in tables]:
                # Get schema
                print(f"\n{'=' * 80}")
                print(f"SCHEMA: {table_name}")
                print("=" * 80)
                schema = get_table_schema(connection, table_name)
                if schema:
                    print(
                        f"{'Column':<30} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<15} {'Extra'}"
                    )
                    print("-" * 100)
                    for col in schema:
                        col_name, col_type, null, key, default, extra = col
                        default_str = str(default) if default is not None else "NULL"
                        print(
                            f"{col_name:<30} {col_type:<20} {null:<10} {key or '':<10} {default_str:<15} {extra or ''}"
                        )

                # Get data
                columns, rows = query_table(connection, table_name, limit=20)
                print_table_data(columns, rows, table_name)

        # Query password migration status
        print("\n" + "=" * 80)
        print("PASSWORD MIGRATION STATUS")
        print("=" * 80)
        cursor = connection.cursor()
        try:
            # Check if password_salt column exists
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'ACCOUNTS'
                AND COLUMN_NAME = 'password_salt'
            """
            )
            has_salt_column = cursor.fetchone()[0] > 0

            if has_salt_column:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_accounts,
                        SUM(CASE WHEN password_salt IS NOT NULL AND password_salt != '' THEN 1 ELSE 0 END) as migrated_accounts,
                        SUM(CASE WHEN password_salt IS NULL OR password_salt = '' THEN 1 ELSE 0 END) as legacy_accounts
                    FROM ACCOUNTS
                """
                )
                result = cursor.fetchone()
                if result:
                    total, migrated, legacy = result
                    print(f"\nTotal accounts: {total}")
                    print(f"  ✓ Migrated (hashed): {migrated}")
                    print(f"  ○ Legacy (plain text): {legacy}")
                    if total > 0:
                        pct = (migrated / total) * 100
                        print(f"  Migration progress: {pct:.1f}%")
            else:
                print("\n⚠ password_salt column does not exist yet")
                print("   Run database_migration.sql to add the column")
        except Error as e:
            print(f"Error checking migration status: {e}")
        finally:
            cursor.close()

    except Error as e:
        print(f"\nDatabase error: {e}")
        return 1
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ Connection closed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
