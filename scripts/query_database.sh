#!/bin/bash
# Database Query Script for Todo Webapp
# Usage: ./scripts/query_database.sh [mysql_root_password]

DB_USER="${1:-root}"
DB_NAME="todo"

echo "=========================================="
echo "DATABASE QUERY TOOL - Todo Webapp"
echo "=========================================="
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""
echo "Enter MySQL password when prompted..."
echo ""

mysql -u "$DB_USER" -p "$DB_NAME" << 'EOF'
SELECT '=== DATABASE TABLES ===' as '';
SHOW TABLES;

SELECT '' as '';
SELECT '=== ACCOUNTS TABLE SCHEMA ===' as '';
DESCRIBE ACCOUNTS;

SELECT '' as '';
SELECT '=== ACCOUNTS DATA (first 10 rows) ===' as '';
SELECT 
    account_id,
    username,
    first_name,
    last_name,
    CASE 
        WHEN password_salt IS NOT NULL AND password_salt != '' THEN 'Hashed'
        ELSE 'Plain Text'
    END as password_type,
    created_at,
    status_id
FROM ACCOUNTS 
LIMIT 10;

SELECT '' as '';
SELECT '=== PASSWORD MIGRATION STATUS ===' as '';
SELECT 
    COUNT(*) as total_accounts,
    SUM(CASE WHEN password_salt IS NOT NULL AND password_salt != '' THEN 1 ELSE 0 END) as migrated_accounts,
    SUM(CASE WHEN password_salt IS NULL OR password_salt = '' THEN 1 ELSE 0 END) as legacy_accounts,
    ROUND(SUM(CASE WHEN password_salt IS NOT NULL AND password_salt != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as migration_percentage
FROM ACCOUNTS;

SELECT '' as '';
SELECT '=== TASKS TABLE COUNT ===' as '';
SELECT COUNT(*) as total_tasks FROM TASKS;

SELECT '' as '';
SELECT '=== TASKS DATA (first 5 rows) ===' as '';
SELECT 
    task_id,
    account_id,
    LEFT(task_description, 50) as task_description,
    created_at,
    status_id,
    priority_id
FROM TASKS 
LIMIT 5;

SELECT '' as '';
SELECT '=== ACCOUNT_SESSIONS COUNT ===' as '';
SELECT COUNT(*) as total_sessions FROM ACCOUNT_SESSIONS;

SELECT '' as '';
SELECT '=== ACCOUNT_SESSIONS (recent 5) ===' as '';
SELECT 
    session_id,
    account_id,
    created_at,
    last_accessed_at
FROM ACCOUNT_SESSIONS 
ORDER BY last_accessed_at DESC 
LIMIT 5;

SELECT '' as '';
SELECT '=== ACCOUNT STATUSES ===' as '';
SELECT * FROM ACCOUNT_STATUSES;

SELECT '' as '';
SELECT '=== TASK STATUSES ===' as '';
SELECT * FROM TASK_STATUSES;

SELECT '' as '';
SELECT '=== TASK PRIORITIES ===' as '';
SELECT * FROM TASK_PRIORITIES;
EOF

echo ""
echo "=========================================="
echo "Query complete!"
echo "=========================================="
