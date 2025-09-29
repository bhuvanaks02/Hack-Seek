-- HackSeek Database Initialization Script
-- This script creates the initial database structure

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_picture_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create hackathons table
CREATE TABLE IF NOT EXISTS hackathons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    short_description VARCHAR(1000),
    organizer VARCHAR(255),
    website_url TEXT,
    registration_url TEXT,
    image_url TEXT,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    registration_deadline TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    is_online BOOLEAN DEFAULT FALSE,
    is_hybrid BOOLEAN DEFAULT FALSE,
    participation_fee DECIMAL(10,2) DEFAULT 0.00,
    prize_money DECIMAL(12,2),
    max_participants INTEGER,
    difficulty_level VARCHAR(50) CHECK (difficulty_level IN ('Beginner', 'Intermediate', 'Advanced', 'All')),
    categories TEXT[], -- Array of category strings
    technologies TEXT[], -- Array of technology strings
    source_platform VARCHAR(100), -- 'Devpost', 'Unstop', 'MLH', 'HackerEarth', etc.
    source_id VARCHAR(255), -- ID from the source platform
    source_url TEXT, -- Original URL from source platform
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_source_hackathon UNIQUE (source_platform, source_id)
);

-- Create user_favorites table for user saved hackathons
CREATE TABLE IF NOT EXISTS user_favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hackathon_id UUID NOT NULL REFERENCES hackathons(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate favorites
    CONSTRAINT unique_user_favorite UNIQUE (user_id, hackathon_id)
);

-- Create search_logs table for analytics and AI training
CREATE TABLE IF NOT EXISTS search_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    search_query TEXT NOT NULL,
    search_filters JSONB,
    results_count INTEGER,
    clicked_hackathon_id UUID REFERENCES hackathons(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_sessions table for AI chatbot conversations
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB, -- Store additional message metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create scraping_jobs table for tracking scraper runs
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    hackathons_scraped INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    error_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_hackathons_start_date ON hackathons(start_date);
CREATE INDEX IF NOT EXISTS idx_hackathons_registration_deadline ON hackathons(registration_deadline);
CREATE INDEX IF NOT EXISTS idx_hackathons_source_platform ON hackathons(source_platform);
CREATE INDEX IF NOT EXISTS idx_hackathons_categories ON hackathons USING GIN(categories);
CREATE INDEX IF NOT EXISTS idx_hackathons_technologies ON hackathons USING GIN(technologies);
CREATE INDEX IF NOT EXISTS idx_hackathons_location ON hackathons(location);
CREATE INDEX IF NOT EXISTS idx_hackathons_is_online ON hackathons(is_online);
CREATE INDEX IF NOT EXISTS idx_hackathons_difficulty_level ON hackathons(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_hackathons_is_active ON hackathons(is_active);
CREATE INDEX IF NOT EXISTS idx_hackathons_full_text ON hackathons USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_hackathon_id ON user_favorites(hackathon_id);

CREATE INDEX IF NOT EXISTS idx_search_logs_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_token ON chat_sessions(session_token);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_platform ON scraping_jobs(platform);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_created_at ON scraping_jobs(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_hackathons_updated_at ON hackathons;
CREATE TRIGGER update_hackathons_updated_at
    BEFORE UPDATE ON hackathons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to update last_activity_at for chat sessions
CREATE OR REPLACE FUNCTION update_chat_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET last_activity_at = CURRENT_TIMESTAMP
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to update chat session activity on new messages
DROP TRIGGER IF EXISTS update_chat_session_activity_trigger ON chat_messages;
CREATE TRIGGER update_chat_session_activity_trigger
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_session_activity();

-- Insert default admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, is_verified)
VALUES (
    'admin@hackseek.dev',
    crypt('admin123', gen_salt('bf')),
    'Admin',
    'User',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW active_hackathons AS
SELECT * FROM hackathons
WHERE is_active = TRUE
AND (end_date IS NULL OR end_date > CURRENT_TIMESTAMP)
ORDER BY start_date ASC;

CREATE OR REPLACE VIEW upcoming_hackathons AS
SELECT * FROM hackathons
WHERE is_active = TRUE
AND start_date > CURRENT_TIMESTAMP
AND (registration_deadline IS NULL OR registration_deadline > CURRENT_TIMESTAMP)
ORDER BY start_date ASC;

CREATE OR REPLACE VIEW featured_hackathons AS
SELECT * FROM hackathons
WHERE is_active = TRUE
AND prize_money > 0
AND (end_date IS NULL OR end_date > CURRENT_TIMESTAMP)
ORDER BY prize_money DESC, start_date ASC;

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hackseek_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hackseek_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO hackseek_user;