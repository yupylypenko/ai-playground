-- ============================================================================
-- Database Creation Script for Todo Webapp
-- ============================================================================
-- This script creates the complete database schema from scratch
-- Run this if you need to recreate the database or it has been lost
--
-- Usage:
--   mysql -u root -p < scripts/create_database.sql
--   OR
--   mysql -u todo -ptodo < scripts/create_database.sql
-- ============================================================================

-- Create database (drop if exists)
DROP DATABASE IF EXISTS todo;
CREATE DATABASE todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE todo;

-- ============================================================================
-- Table: ACCOUNT_STATUSES
-- Purpose: Reference table for account status (enabled/disabled)
-- ============================================================================
CREATE TABLE ACCOUNT_STATUSES (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default statuses
INSERT INTO ACCOUNT_STATUSES (status_id, status) VALUES
    (1, 'enabled'),
    (2, 'disabled');

-- ============================================================================
-- Table: ACCOUNTS
-- Purpose: User account information with secure password storage
-- ============================================================================
CREATE TABLE ACCOUNTS (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NULL,  -- For SHA-256 hashed passwords
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_id INT NOT NULL DEFAULT 1,
    FOREIGN KEY (status_id) REFERENCES ACCOUNT_STATUSES(status_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create index on username for faster lookups
CREATE INDEX idx_username ON ACCOUNTS(username);

-- Create index on password_salt if it will be queried
-- CREATE INDEX idx_password_salt ON ACCOUNTS(password_salt);

-- ============================================================================
-- Table: ACCOUNT_SESSIONS
-- Purpose: Track user login sessions (accounting/AAA)
-- ============================================================================
CREATE TABLE ACCOUNT_SESSIONS (
    session_id VARCHAR(255) PRIMARY KEY,
    account_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES ACCOUNTS(account_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create index on account_id for faster session lookups
CREATE INDEX idx_account_id ON ACCOUNT_SESSIONS(account_id);

-- ============================================================================
-- Table: TASK_STATUSES
-- Purpose: Reference table for task status (todo/in progress/done)
-- ============================================================================
CREATE TABLE TASK_STATUSES (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default task statuses
INSERT INTO TASK_STATUSES (status_id, status) VALUES
    (1, 'todo'),
    (2, 'in progress'),
    (3, 'done');

-- ============================================================================
-- Table: TASK_PRIORITIES
-- Purpose: Reference table for task priorities (Eisenhower Matrix)
-- ============================================================================
CREATE TABLE TASK_PRIORITIES (
    priority_id INT PRIMARY KEY AUTO_INCREMENT,
    priority VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default priorities (Eisenhower Matrix)
INSERT INTO TASK_PRIORITIES (priority_id, priority) VALUES
    (1, 'important & urgent'),
    (2, 'important but not urgent'),
    (3, 'not important but urgent'),
    (4, 'not important and not urgent');

-- ============================================================================
-- Table: TASKS
-- Purpose: User todo tasks with status and priority tracking
-- Note: No delete operation - tasks persist forever per requirements
-- ============================================================================
CREATE TABLE TASKS (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    task_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP NULL,
    last_updated TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    status_id INT NOT NULL DEFAULT 1,
    priority_id INT NOT NULL DEFAULT 4,
    FOREIGN KEY (account_id) REFERENCES ACCOUNTS(account_id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES TASK_STATUSES(status_id) ON DELETE RESTRICT,
    FOREIGN KEY (priority_id) REFERENCES TASK_PRIORITIES(priority_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create index on account_id for faster task lookups
CREATE INDEX idx_account_id ON TASKS(account_id);

-- Create index on status_id for filtering by status
CREATE INDEX idx_status_id ON TASKS(status_id);

-- Create index on deadline for sorting by deadline
CREATE INDEX idx_deadline ON TASKS(deadline);

-- ============================================================================
-- Sample Data Insertion
-- ============================================================================

-- Insert admin account (plain text password for initial setup)
-- In production, this should be hashed using PasswordUtil
INSERT INTO ACCOUNTS (username, first_name, last_name, password, password_salt, status_id) VALUES
    ('admin', 'Administrator', 'User', 'password', NULL, 1);

-- Insert some sample users (plain text passwords - should be migrated)
INSERT INTO ACCOUNTS (username, first_name, last_name, password, password_salt, status_id) VALUES
    ('john@example.com', 'John', 'Johnsson', 'oneword', NULL, 2),
    ('eric@example.com', 'Eric', 'Ericsson', 'twoword', NULL, 1),
    ('ana@example.com', 'Ana', 'Mary', 'threeword', NULL, 1);

-- Insert sample tasks
INSERT INTO TASKS (account_id, task_description, created_at, deadline, status_id, priority_id) VALUES
    (2, 'Buy pencils.', '2019-05-06 17:40:03', '2019-05-07 17:40:03', 2, 1),
    (3, 'Buy books.', '2019-05-07 7:40:03', '2019-05-07 17:40:03', 2, 1);

-- Insert sample session
INSERT INTO ACCOUNT_SESSIONS (session_id, account_id, created_at, last_accessed_at) VALUES
    ('asd1gh', 1, '2019-05-06 17:40:03', '2019-05-06 18:00:03');

-- ============================================================================
-- Verification Queries
-- ============================================================================

SELECT 'Database creation completed!' as status;
SELECT '' as '';
SELECT 'Table counts:' as '';
SELECT 'ACCOUNT_STATUSES' as table_name, COUNT(*) as row_count FROM ACCOUNT_STATUSES
UNION ALL
SELECT 'ACCOUNTS', COUNT(*) FROM ACCOUNTS
UNION ALL
SELECT 'TASK_STATUSES', COUNT(*) FROM TASK_STATUSES
UNION ALL
SELECT 'TASK_PRIORITIES', COUNT(*) FROM TASK_PRIORITIES
UNION ALL
SELECT 'TASKS', COUNT(*) FROM TASKS
UNION ALL
SELECT 'ACCOUNT_SESSIONS', COUNT(*) FROM ACCOUNT_SESSIONS;

SELECT '' as '';
SELECT 'Sample accounts:' as '';
SELECT account_id, username, first_name, last_name, 
       CASE WHEN password_salt IS NOT NULL THEN 'Hashed' ELSE 'Plain Text' END as password_type,
       status_id 
FROM ACCOUNTS;

-- ============================================================================
-- Next Steps:
-- ============================================================================
-- 1. Verify all tables were created successfully
-- 2. Run database_migration.sql if you want to ensure password_salt column exists
-- 3. Update passwords to use hashed format using the application's login flow
-- 4. Configure Tomcat with JNDI datasource in context.xml
-- 5. Deploy the application
-- ============================================================================
