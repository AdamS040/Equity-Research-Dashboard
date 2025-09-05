-- PostgreSQL initialization script for Equity Research Dashboard
-- This script runs when the PostgreSQL container is first created

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE equity_research'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'equity_research')\gexec

-- Connect to the database
\c equity_research;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types if needed
-- (Add any custom PostgreSQL types here)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE equity_research TO postgres;
