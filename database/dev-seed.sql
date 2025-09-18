-- Development seed data for HackSeek
-- This file contains sample data for testing and development

-- Sample hackathons with diverse data
INSERT INTO hackathons (id, title, description, start_date, end_date, location, prize_money, registration_url, platform, tags, difficulty_level, max_team_size, created_at, updated_at) VALUES
('dev-hack-1', 'Local Dev Hackathon', 'A beginner-friendly hackathon for local developers to showcase their skills', '2024-12-01 09:00:00', '2024-12-03 18:00:00', 'Online', 5000, 'https://example.com/dev-hack-1', 'devpost', '["web development", "mobile", "beginner"]', 'beginner', 4, NOW(), NOW()),

('dev-hack-2', 'AI Challenge 2024', 'Build innovative AI solutions to solve real-world problems', '2024-12-15 10:00:00', '2024-12-17 20:00:00', 'San Francisco, CA', 10000, 'https://example.com/ai-challenge', 'unstop', '["artificial intelligence", "machine learning", "data science"]', 'intermediate', 5, NOW(), NOW()),

('dev-hack-3', 'Web3 Innovation Hack', 'Create the next generation of blockchain applications', '2025-01-05 08:00:00', '2025-01-07 22:00:00', 'New York, NY', 15000, 'https://example.com/web3-hack', 'devfolio', '["blockchain", "web3", "cryptocurrency", "defi"]', 'advanced', 3, NOW(), NOW()),

('dev-hack-4', 'Sustainability Tech Challenge', 'Develop technology solutions for environmental challenges', '2024-11-20 09:00:00', '2024-11-22 17:00:00', 'Seattle, WA', 8000, 'https://example.com/sustainability-hack', 'mlh', '["sustainability", "environment", "green tech"]', 'intermediate', 6, NOW(), NOW()),

('dev-hack-5', 'Mobile Gaming Jam', '48-hour mobile game development competition', '2024-12-08 12:00:00', '2024-12-10 12:00:00', 'Austin, TX', 3000, 'https://example.com/mobile-gaming-jam', 'hackerearth', '["mobile games", "unity", "game development"]', 'beginner', 2, NOW(), NOW()),

('dev-hack-6', 'FinTech Revolution', 'Build the future of financial technology', '2025-01-12 09:00:00', '2025-01-14 18:00:00', 'London, UK', 20000, 'https://example.com/fintech-hack', 'devpost', '["fintech", "payments", "banking", "api"]', 'advanced', 4, NOW(), NOW()),

('dev-hack-7', 'Healthcare Innovation Challenge', 'Technology solutions for better healthcare', '2024-12-20 10:00:00', '2024-12-22 16:00:00', 'Boston, MA', 12000, 'https://example.com/healthcare-hack', 'unstop', '["healthcare", "medtech", "telemedicine"]', 'intermediate', 5, NOW(), NOW()),

('dev-hack-8', 'Open Source Contribution Weekend', 'Contribute to major open source projects', '2024-11-30 14:00:00', '2024-12-01 20:00:00', 'Online', 2000, 'https://example.com/opensource-weekend', 'github', '["open source", "git", "collaboration"]', 'beginner', 1, NOW(), NOW())

ON CONFLICT (id) DO NOTHING;

-- Sample user data for testing authentication and user features
INSERT INTO users (id, email, username, first_name, last_name, password_hash, is_verified, created_at, updated_at) VALUES
('user-1', 'john.doe@example.com', 'johndoe', 'John', 'Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeflzQp1vMTyXhZjy', true, NOW(), NOW()),
('user-2', 'jane.smith@example.com', 'janesmith', 'Jane', 'Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeflzQp1vMTyXhZjy', true, NOW(), NOW()),
('user-3', 'dev.user@example.com', 'devuser', 'Dev', 'User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeflzQp1vMTyXhZjy', false, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Sample user preferences for testing personalization
INSERT INTO user_preferences (user_id, preferred_locations, preferred_tags, difficulty_levels, max_prize_range, email_notifications, created_at, updated_at) VALUES
('user-1', '["Online", "San Francisco, CA", "New York, NY"]', '["web development", "mobile", "ai"]', '["beginner", "intermediate"]', 10000, true, NOW(), NOW()),
('user-2', '["Online", "Boston, MA", "Seattle, WA"]', '["blockchain", "fintech", "healthcare"]', '["intermediate", "advanced"]', 25000, true, NOW(), NOW()),
('user-3', '["Online"]', '["open source", "game development"]', '["beginner"]', 5000, false, NOW(), NOW())
ON CONFLICT (user_id) DO NOTHING;

-- Sample bookmarks for testing user interaction
INSERT INTO bookmarks (user_id, hackathon_id, created_at) VALUES
('user-1', 'dev-hack-1', NOW()),
('user-1', 'dev-hack-2', NOW()),
('user-2', 'dev-hack-3', NOW()),
('user-2', 'dev-hack-6', NOW()),
('user-3', 'dev-hack-5', NOW()),
('user-3', 'dev-hack-8', NOW())
ON CONFLICT (user_id, hackathon_id) DO NOTHING;

-- Sample search queries for testing analytics
INSERT INTO search_queries (query_text, user_id, results_count, created_at) VALUES
('AI hackathons in California', 'user-1', 3, NOW() - INTERVAL '2 days'),
('Blockchain events 2024', 'user-2', 5, NOW() - INTERVAL '1 day'),
('Beginner friendly hackathons', 'user-3', 8, NOW() - INTERVAL '3 hours'),
('Web development challenges', 'user-1', 4, NOW() - INTERVAL '1 hour')
ON CONFLICT DO NOTHING;

-- Sample platform statistics for testing scraper metrics
INSERT INTO platform_stats (platform_name, total_hackathons, last_scraped, success_rate, avg_response_time, created_at, updated_at) VALUES
('devpost', 156, NOW() - INTERVAL '30 minutes', 0.95, 1.2, NOW(), NOW()),
('unstop', 89, NOW() - INTERVAL '45 minutes', 0.92, 1.8, NOW(), NOW()),
('devfolio', 67, NOW() - INTERVAL '1 hour', 0.88, 2.1, NOW(), NOW()),
('mlh', 34, NOW() - INTERVAL '2 hours', 0.98, 0.9, NOW(), NOW()),
('hackerearth', 78, NOW() - INTERVAL '1.5 hours', 0.91, 1.5, NOW(), NOW())
ON CONFLICT (platform_name) DO UPDATE SET
    total_hackathons = EXCLUDED.total_hackathons,
    last_scraped = EXCLUDED.last_scraped,
    success_rate = EXCLUDED.success_rate,
    avg_response_time = EXCLUDED.avg_response_time,
    updated_at = NOW();