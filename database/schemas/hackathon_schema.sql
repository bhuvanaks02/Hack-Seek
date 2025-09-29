-- HackSeek Database Schema Documentation
-- This file documents the database structure and relationships

-- ================================================================
-- USERS TABLE
-- ================================================================
-- Stores user account information
/*
Table: users
Columns:
  - id: UUID primary key
  - email: Unique user email address
  - password_hash: Bcrypt hashed password
  - first_name: User's first name
  - last_name: User's last name
  - profile_picture_url: URL to user's profile picture
  - is_active: Whether the account is active
  - is_verified: Whether the email is verified
  - created_at: Account creation timestamp
  - updated_at: Last update timestamp

Indexes:
  - idx_users_email: On email column for login queries
  - idx_users_is_active: On is_active for filtering active users

Relationships:
  - One-to-many with user_favorites
  - One-to-many with search_logs
  - One-to-many with chat_sessions
*/

-- ================================================================
-- HACKATHONS TABLE
-- ================================================================
-- Central table storing all hackathon information from various platforms
/*
Table: hackathons
Columns:
  - id: UUID primary key
  - title: Hackathon name/title
  - description: Full description
  - short_description: Brief summary (max 1000 chars)
  - organizer: Organization/company hosting the hackathon
  - website_url: Main hackathon website
  - registration_url: Direct registration link
  - image_url: Hackathon logo/banner image
  - start_date: Event start date/time
  - end_date: Event end date/time
  - registration_deadline: Last date to register
  - location: Physical location (if applicable)
  - is_online: Whether it's a virtual event
  - is_hybrid: Whether it's both online and offline
  - participation_fee: Cost to participate
  - prize_money: Total prize pool amount
  - max_participants: Maximum number of participants
  - difficulty_level: Target skill level (Beginner/Intermediate/Advanced/All)
  - categories: Array of theme categories (e.g., ['AI', 'Web Development'])
  - technologies: Array of suggested technologies (e.g., ['React', 'Python'])
  - source_platform: Where this was scraped from
  - source_id: Original ID from source platform
  - source_url: Original URL from source platform
  - is_active: Whether this hackathon is still relevant
  - scraped_at: When this data was last updated
  - created_at: First time this hackathon was recorded
  - updated_at: Last modification time

Indexes:
  - idx_hackathons_start_date: For date-based queries
  - idx_hackathons_registration_deadline: For deadline filtering
  - idx_hackathons_source_platform: For platform-specific queries
  - idx_hackathons_categories: GIN index for array searches
  - idx_hackathons_technologies: GIN index for array searches
  - idx_hackathons_location: For location-based searches
  - idx_hackathons_is_online: For filtering online events
  - idx_hackathons_difficulty_level: For skill level filtering
  - idx_hackathons_is_active: For filtering active hackathons
  - idx_hackathons_full_text: Full-text search on title and description

Constraints:
  - unique_source_hackathon: Prevents duplicate entries from same source
  - difficulty_level check: Ensures valid difficulty levels

Relationships:
  - One-to-many with user_favorites
  - One-to-many with search_logs (clicked_hackathon_id)
*/

-- ================================================================
-- USER_FAVORITES TABLE
-- ================================================================
-- Junction table for users saving hackathons
/*
Table: user_favorites
Columns:
  - id: UUID primary key
  - user_id: Reference to users table
  - hackathon_id: Reference to hackathons table
  - created_at: When the favorite was added

Indexes:
  - idx_user_favorites_user_id: For user-specific queries
  - idx_user_favorites_hackathon_id: For hackathon popularity queries

Constraints:
  - unique_user_favorite: Prevents duplicate favorites
  - Foreign key constraints with CASCADE delete

Relationships:
  - Many-to-one with users
  - Many-to-one with hackathons
*/

-- ================================================================
-- SEARCH_LOGS TABLE
-- ================================================================
-- Analytics table for tracking user searches and behavior
/*
Table: search_logs
Columns:
  - id: UUID primary key
  - user_id: Reference to users (nullable for anonymous users)
  - search_query: What the user searched for
  - search_filters: JSON object containing applied filters
  - results_count: Number of results returned
  - clicked_hackathon_id: Which result they clicked (if any)
  - session_id: Session identifier
  - ip_address: User's IP address
  - user_agent: Browser/client information
  - created_at: Search timestamp

Indexes:
  - idx_search_logs_user_id: For user analytics
  - idx_search_logs_created_at: For time-based analytics

Relationships:
  - Many-to-one with users (nullable)
  - Many-to-one with hackathons (clicked_hackathon_id, nullable)
*/

-- ================================================================
-- CHAT_SESSIONS TABLE
-- ================================================================
-- Manages AI chatbot conversation sessions
/*
Table: chat_sessions
Columns:
  - id: UUID primary key
  - user_id: Reference to users (nullable for anonymous sessions)
  - session_token: Unique session identifier
  - is_active: Whether session is still active
  - created_at: Session start time
  - last_activity_at: Last message timestamp

Indexes:
  - idx_chat_sessions_user_id: For user session queries
  - idx_chat_sessions_session_token: For session lookup

Relationships:
  - Many-to-one with users (nullable)
  - One-to-many with chat_messages
*/

-- ================================================================
-- CHAT_MESSAGES TABLE
-- ================================================================
-- Stores individual messages in chatbot conversations
/*
Table: chat_messages
Columns:
  - id: UUID primary key
  - session_id: Reference to chat_sessions
  - message_type: Type of message (user/assistant/system)
  - content: Message text content
  - metadata: Additional message data (JSON)
  - created_at: Message timestamp

Indexes:
  - idx_chat_messages_session_id: For conversation retrieval
  - idx_chat_messages_created_at: For chronological ordering

Constraints:
  - message_type check: Ensures valid message types

Relationships:
  - Many-to-one with chat_sessions
*/

-- ================================================================
-- SCRAPING_JOBS TABLE
-- ================================================================
-- Tracks web scraping operations for monitoring and debugging
/*
Table: scraping_jobs
Columns:
  - id: UUID primary key
  - platform: Which platform was scraped
  - status: Job status (pending/running/completed/failed/cancelled)
  - started_at: When scraping began
  - completed_at: When scraping finished
  - hackathons_scraped: Number of hackathons processed
  - errors_encountered: Number of errors during scraping
  - error_details: JSON object with error information
  - created_at: Job creation time

Indexes:
  - idx_scraping_jobs_platform: For platform-specific monitoring
  - idx_scraping_jobs_status: For status-based queries
  - idx_scraping_jobs_created_at: For chronological monitoring

Constraints:
  - status check: Ensures valid job statuses
*/

-- ================================================================
-- VIEWS
-- ================================================================

-- active_hackathons: Shows all currently active hackathons
-- upcoming_hackathons: Shows hackathons with open registration
-- featured_hackathons: Shows high-value hackathons sorted by prize money

-- ================================================================
-- TRIGGERS
-- ================================================================

-- update_updated_at_column(): Updates updated_at timestamp on row changes
-- update_chat_session_activity(): Updates chat session activity on new messages

-- ================================================================
-- SAMPLE QUERIES
-- ================================================================

-- Find upcoming AI hackathons:
/*
SELECT * FROM hackathons
WHERE 'AI' = ANY(categories)
AND start_date > CURRENT_TIMESTAMP
AND is_active = TRUE
ORDER BY start_date ASC;
*/

-- Get user's favorite hackathons:
/*
SELECT h.* FROM hackathons h
JOIN user_favorites uf ON h.id = uf.hackathon_id
WHERE uf.user_id = 'user-uuid-here'
ORDER BY uf.created_at DESC;
*/

-- Full-text search:
/*
SELECT *, ts_rank(to_tsvector('english', title || ' ' || COALESCE(description, '')),
                  plainto_tsquery('english', 'search term')) as rank
FROM hackathons
WHERE to_tsvector('english', title || ' ' || COALESCE(description, ''))
      @@ plainto_tsquery('english', 'search term')
AND is_active = TRUE
ORDER BY rank DESC;
*/