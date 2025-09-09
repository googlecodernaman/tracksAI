-- Initialize Railway Traffic Decision-Support System Database
-- This script sets up the database with initial configuration

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create initial database schema will be handled by SQLAlchemy migrations
-- This file is for any additional setup needed

-- Create indexes for better performance
-- (These will be created by the application, but can be added here for reference)

-- Example: Create time-series hypertable for system states
-- SELECT create_hypertable('system_states', 'timestamp');

-- Insert some sample data for development
-- (This will be handled by the application's seed data functionality)
