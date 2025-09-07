# Hack-Seek
HackSeek is a full-stack web application that helps developers discover hackathons worldwide through intelligent filtering and AI-powered chatbot assistance. Find hackathons that match your location, date preferences, skill level, and interests.
## 🌟 Features

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



## 🏗️ Architecture

**Frontend**: Next.js + React + TypeScript  
**Backend**: Python FastAPI + PostgreSQL  
**AI**: Claude API with local model fallback  
**Scraping**: Python + BeautifulSoup/selenium + Scrapy  
**Deployment**: Docker containers



## 📁 Project Structure

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