# Contributing to HackSeek

Thank you for your interest in contributing to HackSeek! This document outlines the guidelines and best practices for contributing to this project.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/hack-seek.git
   cd hack-seek
   ```

2. **Environment Setup**
   ```bash
   # Copy environment file
   cp .env.example .env
   # Update .env with your API keys

   # Quick setup using script
   ./scripts/dev-setup.sh  # Linux/Mac
   # or
   ./scripts/dev-setup.bat  # Windows
   ```

3. **Start Development Environment**
   ```bash
   make dev-start
   # or
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Verify Setup**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - PgAdmin: http://localhost:5050 (run `make admin` first)

## 📝 Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes
- Run linting: `make lint` or `flake8 . && mypy .`
- Format code: `make format` or `black .`

### TypeScript/React (Frontend)
- Use TypeScript for all new files
- Follow ESLint configuration
- Use functional components with hooks
- Props should be typed with interfaces
- Run linting: `npm run lint`
- Format code: `npm run lint -- --fix`

### SQL (Database)
- Use lowercase for keywords
- Use snake_case for table and column names
- Always use meaningful constraint names
- Include comments for complex queries

## 🗂️ Project Structure

### Backend (`/backend`)
```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   ├── utils/        # Utility functions
│   └── main.py       # FastAPI application
├── tests/            # Test files
└── requirements.txt  # Python dependencies
```

### Frontend (`/frontend`)
```
frontend/
├── src/
│   ├── components/   # Reusable React components
│   ├── pages/        # Next.js pages
│   ├── hooks/        # Custom React hooks
│   ├── utils/        # Utility functions
│   └── styles/       # CSS/styling files
├── public/           # Static assets
└── package.json      # Node.js dependencies
```

### Scraper (`/scraper`)
```
scraper/
├── scrapers/         # Platform-specific scrapers
├── utils/            # Scraping utilities
└── main.py           # Scraper orchestrator
```

## 🧪 Testing

### Running Tests
```bash
# All tests
make test

# Backend only
cd backend && pytest -v

# Frontend only
cd frontend && npm test

# Specific test file
pytest backend/tests/test_hackathons.py -v
```

### Writing Tests
- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

### Test Structure
```python
def test_feature_should_behavior_when_condition():
    # Arrange
    setup_data()

    # Act
    result = function_under_test()

    # Assert
    assert result.expected_outcome
```

## 🔄 Git Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates

### Commit Messages
Follow conventional commits format:
```
type(scope): brief description

Detailed description if needed

- Bullet point 1
- Bullet point 2

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process
1. Create feature branch from `main`
2. Make changes following style guidelines
3. Add/update tests
4. Update documentation
5. Run full test suite
6. Create pull request with descriptive title and description
7. Address code review feedback
8. Squash commits before merge

## 🏗️ Architecture Guidelines

### Backend Principles
- Use dependency injection for services
- Separate business logic from API routes
- Implement proper error handling
- Use async/await for I/O operations
- Follow RESTful API conventions

### Frontend Principles
- Components should be reusable and modular
- Use custom hooks for shared logic
- Implement proper error boundaries
- Use TypeScript strictly
- Follow React best practices

### Database Guidelines
- Use migrations for schema changes
- Index frequently queried columns
- Use appropriate foreign key constraints
- Normalize data appropriately
- Document complex queries

## 🔍 Code Review Process

### For Contributors
- Keep PRs small and focused
- Write clear commit messages
- Include tests for new features
- Update documentation
- Self-review before requesting review

### For Reviewers
- Check code quality and style
- Verify test coverage
- Look for security issues
- Consider performance implications
- Provide constructive feedback

## 🚀 Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create release tag
6. Deploy to staging
7. Test in staging environment
8. Deploy to production
9. Monitor for issues

## 📊 Performance Guidelines

### Backend
- Use database indexes appropriately
- Implement caching where beneficial
- Use async operations for I/O
- Monitor API response times
- Implement rate limiting

### Frontend
- Optimize bundle size
- Use code splitting
- Implement lazy loading
- Optimize images
- Monitor Core Web Vitals

### Database
- Use explain plans for complex queries
- Monitor query performance
- Use connection pooling
- Implement proper indexing strategy

## 🔒 Security Guidelines

- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper authentication/authorization
- Validate all user inputs
- Use HTTPS in production
- Keep dependencies updated
- Follow OWASP security principles

## 📚 Documentation

- Update README.md for major changes
- Document API changes in OpenAPI spec
- Add inline code comments for complex logic
- Update architecture diagrams
- Write user guides for new features

## ❓ Getting Help

- Check existing issues before creating new ones
- Use discussions for questions
- Tag maintainers for urgent issues
- Provide minimal reproducible examples
- Include system information when reporting bugs

## 🎯 Areas for Contribution

- **Web Scrapers**: Add new hackathon platforms
- **AI Features**: Improve chatbot responses
- **UI/UX**: Enhance user interface
- **Performance**: Optimize database queries
- **Testing**: Increase test coverage
- **Documentation**: Improve guides and examples
- **Mobile**: React Native mobile app
- **Integrations**: Calendar, notification systems

## 📞 Contact

For questions or discussions, please:
- Open an issue on GitHub
- Start a discussion in the Discussions tab
- Email: [your-email@example.com]

Thank you for contributing to HackSeek! 🚀