# Database Recovery Guide

This guide explains how to recreate the todo webapp database if it is lost or corrupted.

## Quick Recovery

If the database is completely lost, you can recreate it with one command:

```bash
# Option 1: Using root user
mysql -u root -p < scripts/create_database.sql

# Option 2: Using todo user (if it has CREATE DATABASE privileges)
mysql -u todo -ptodo < scripts/create_database.sql
```

## What Gets Recreated

The `create_database.sql` script will:

1. **Drop and recreate** the `todo` database
2. **Create all tables** with proper structure:
   - `ACCOUNT_STATUSES` - enabled/disabled statuses
   - `ACCOUNTS` - user accounts with password storage
   - `ACCOUNT_SESSIONS` - login session tracking
   - `TASK_STATUSES` - todo/in progress/done statuses
   - `TASK_PRIORITIES` - task priority levels
   - `TASKS` - user todo items

3. **Insert seed data**:
   - Reference data (statuses, priorities)
   - Sample admin account
   - Sample users
   - Sample tasks
   - Sample session

## Recovery Scenarios

### Scenario 1: Complete Database Loss

**Symptoms**: Database doesn't exist, all data lost

**Solution**:
```bash
cd /mnt/d/git/ai-playground
mysql -u root -p < scripts/create_database.sql
```

This creates a fresh database with sample data.

### Scenario 2: Corrupted Tables

**Symptoms**: Tables exist but schema is corrupted, data integrity issues

**Solution**:
```bash
# Drop and recreate
mysql -u root -p -e "DROP DATABASE IF EXISTS todo;"
mysql -u root -p < scripts/create_database.sql
```

### Scenario 3: Missing Columns

**Symptoms**: Tables exist but missing `password_salt` column

**Solution**:
```bash
# Just add the missing column
mysql -u root -p todo < ../AI\ SDLC/todowebapp/database_migration.sql
```

### Scenario 4: Backup and Restore

**Backup** (before making changes):
```bash
# Create backup
mysqldump -u root -p todo > todo_backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip todo_backup_*.sql
```

**Restore** (if needed):
```bash
# Decompress if needed
gunzip todo_backup_20241101_120000.sql.gz

# Restore
mysql -u root -p todo < todo_backup_20241101_120000.sql
```

## Verification

After recovery, verify the database:

```bash
# Method 1: Using the query script
./scripts/query_database.sh

# Method 2: Direct MySQL
mysql -u root -p todo -e "SELECT COUNT(*) FROM ACCOUNTS;"
mysql -u root -p todo -e "SELECT COUNT(*) FROM TASKS;"

# Method 3: Full verification
mysql -u root -p todo << 'EOF'
SHOW TABLES;
SELECT 'Accounts:' as '', COUNT(*) FROM ACCOUNTS;
SELECT 'Tasks:' as '', COUNT(*) FROM TASKS;
SELECT 'Sessions:' as '', COUNT(*) FROM ACCOUNT_SESSIONS;
EOF
```

## Expected Results After Recovery

- **ACCOUNT_STATUSES**: 2 rows (enabled, disabled)
- **ACCOUNTS**: 4 rows (admin + 3 sample users)
- **TASK_STATUSES**: 3 rows (todo, in progress, done)
- **TASK_PRIORITIES**: 4 rows (Eisenhower matrix priorities)
- **TASKS**: 2 sample tasks
- **ACCOUNT_SESSIONS**: 1 sample session

## Security Notes

**Important**: The sample passwords in `create_database.sql` are in **plain text** format. After recovery:

1. **Change admin password** through the application
2. **Test login** with sample accounts
3. **Migrate passwords** by logging in (triggers automatic migration)
4. **Verify migration**: Run query to check password_salt column

To check password migration status:
```sql
SELECT 
    COUNT(*) as total_accounts,
    SUM(CASE WHEN password_salt IS NOT NULL AND password_salt != '' THEN 1 ELSE 0 END) as migrated_accounts,
    SUM(CASE WHEN password_salt IS NULL OR password_salt = '' THEN 1 ELSE 0 END) as legacy_accounts
FROM ACCOUNTS;
```

## Troubleshooting

### "Access Denied" Error

**Problem**: MySQL user doesn't have privileges

**Solution**: Grant privileges or use root user
```sql
GRANT ALL PRIVILEGES ON todo.* TO 'todo'@'localhost';
FLUSH PRIVILEGES;
```

### "Database Already Exists" Error

**Problem**: Database wasn't dropped properly

**Solution**: Force drop it
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS todo;"
mysql -u root -p < scripts/create_database.sql
```

### "Table Already Exists" Error

**Problem**: Some tables weren't dropped

**Solution**: Drop the whole database
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS todo;"
mysql -u root -p < scripts/create_database.sql
```

## Related Files

- `scripts/create_database.sql` - Complete database creation script
- `scripts/query_database.sh` - Query database contents
- `scripts/query_database.py` - Python query tool
- `../AI SDLC/todowebapp/database_migration.sql` - Password migration script
- `../AI SDLC/todowebapp/web/META-INF/context.xml` - JNDI configuration

## Prevention

To prevent data loss:

1. **Regular backups**: Set up automated daily backups
2. **Version control**: Keep database scripts in git
3. **Testing**: Test recovery scripts regularly
4. **Documentation**: Document any schema changes
5. **Monitoring**: Monitor database health

## Support

For issues or questions:
- Check MySQL logs: `/var/log/mysql/error.log`
- Check application logs: Tomcat logs
- Verify JNDI configuration: `context.xml`
- Test connection: `mysql -u todo -ptodo todo -e "SELECT 1;"`

---

**Last Updated**: November 2024  
**Version**: 1.0
