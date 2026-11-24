-- AuthX Cybersecurity Registration Portal Database Schema
-- Run this script in your MySQL server to set up the database and tables.

CREATE DATABASE IF NOT EXISTS authx_db;
USE authx_db;

CREATE TABLE IF NOT EXISTS hackathon_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_type ENUM('mfa', 'thread') NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    leader_name VARCHAR(255) NOT NULL,
    leader_email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(100) NOT NULL,
    github_link VARCHAR(255) NOT NULL,
    experience_level VARCHAR(100) NOT NULL,
    track_selection VARCHAR(100) NOT NULL,
    team_members TEXT NOT NULL, -- JSON array of squad members
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
