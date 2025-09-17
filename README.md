# Hack-Seek
HackSeek is a full-stack web application that helps developers discover hackathons worldwide through intelligent filtering and AI-powered chatbot assistance. Find hackathons that match your location, date preferences, skill level, and interests.
##  Features

### Core Features
- **Smart Search**: Filter hackathons by location, date, prize money, and themes
- **AI Chatbot**: Natural language queries to find perfect hackathons
- **Global Coverage**: Scrapes hackathons from major platforms worldwide
- **Real-time Updates**: Automated scraping keeps data fresh
- **Calendar Integration**: Export hackathons to Google Calendar



### Data Sources
- **Hackathon Platforms**: Devpost, Unstop, Devfolio, MLH, HackerEarth
- **Event Platforms**: Luma, Eventbrite, Meetup
- **Social Media**: Twitter/X hackathon announcements
- **Tech Communities**: Reddit, Discord, Slack communities



##  Architecture

**Frontend**: Next.js + React + TypeScript  
**Backend**: Python FastAPI + PostgreSQL  
**AI**: Claude API with local model fallback  
**Scraping**: Python + BeautifulSoup/selenium + Scrapy  
**Deployment**: Docker containers



##  Project Structure

hackseek/
├── frontend/                
│   ├── src/
│   │   ├── components/       
│   │   ├── pages/        
│   │   ├── hooks/     
│   │   ├── utils/         
│   │   └── styles/         
│   ├── public/            
│   └── package.json
│
├── backend/                
│   ├── app/
│   │   ├── api/       
│   │   ├── models/      
│   │   ├── services/     
│   │   ├── utils/          
│   │   └── main.py        
│   ├── tests/             
│   └── requirements.txt
│
├── scraper/                
│   ├── scrapers/       
│   │   ├── devpost.py
│   │   ├── unstop.py
│   │   ├── mlh.py
│   │   └── social_media.py
│   ├── utils/            
│   ├── scheduler.py      
│   └── main.py           
│
├── database/              
│   ├── migrations/       
│   ├── schemas/        
│   └── init.sql          # Initial database setup
│
├── docker-compose.yml    
├── .env.example         
└── README.md     



### Prerequisites
- Docker & Docker Compose
- Git

### Development Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd hackseek

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```


### Manual Setup (without Docker)
```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend setup
cd frontend
npm install
npm run dev

# Database setup
# Install PostgreSQL and create database
# Run migrations from database/migrations/
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

### AI API Configuration (Fallback Strategy)
- **GEMINI_API_KEY**: Primary AI API
- **GROQ_API_KEY**: Secondary fallback AI API (14,400 free requests/day)
- **OLLAMA_ENDPOINT**: Local AI fallback (http://localhost:11434) - for development/testing
- **CLAUDE_API_KEY**: Production fallback when website goes public
- **OPENAI_API_KEY**: Final fallback for public deployment

### Database & Services
- **DATABASE_URL**: PostgreSQL connection string
- **TWITTER_BEARER_TOKEN**: For social media scraping
- **SMTP_HOST**: Email server (e.g., smtp.gmail.com)
- **SMTP_PORT**: Email port (587 for Gmail)
- **SMTP_USER**: Email username
- **SMTP_PASSWORD**: Email app password

### API Fallback Flow
1. **Development**: Gemini → Groq → Ollama (local)
2. **Production**: Gemini → Groq → Claude/OpenAI (when public)



##  Contributing

This is a personal learning project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

##  License

MIT License - see LICENSE file for details