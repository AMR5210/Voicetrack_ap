# VoiceTrack Research App

A full-stack mobile application for tracking vocal health and speech patterns using AI-powered audio analysis.

## 🚀 Live Demo

- **API Base URL:** https://voicetrack-app.ue.r.appspot.com/api/
- **API Documentation:** https://voicetrack-app.ue.r.appspot.com/api/docs/
- **Admin Panel:** https://voicetrack-app.ue.r.appspot.com/admin/

## 🎯 Project Overview

This application supports research in communication science and health by enabling users to:
- Record and track voice samples over time
- Analyze audio features (pitch, tone, duration)
- Visualize trends and patterns
- Generate AI-powered insights

## 🛠️ Tech Stack

### Backend (✅ Deployed)
- **Framework:** Django 4.2 + Django REST Framework
- **Database:** PostgreSQL (Google Cloud SQL)
- **Storage:** Google Cloud Storage
- **Authentication:** JWT (JSON Web Tokens)
- **Audio Processing:** librosa, pydub
- **Deployment:** Google App Engine

### Mobile App (🚧 In Progress)
- **Framework:** React Native
- **Platforms:** iOS (TestFlight) + Android (Google Play)

### Cloud & DevOps
- **Platform:** Google Cloud Platform (GCP)
- **Services:** App Engine, Cloud SQL, Cloud Storage
- **CI/CD:** GitHub Actions (planned)
- **Version Control:** Git/GitHub

## 📋 Features

### Completed ✅
- User authentication (register, login, JWT tokens)
- RESTful API with 15+ endpoints
- User profile management
- Voice recording metadata storage
- Analysis results tracking
- Admin interface for data management
- Comprehensive API documentation (Swagger/OpenAPI)
- Production deployment on GCP
- CORS configuration for mobile apps

### In Progress 🚧
- Audio processing pipeline
- CI/CD pipeline with GitHub Actions

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user info

### Voice Recordings
- `GET /api/recordings/` - List user's recordings (paginated)
- `POST /api/recordings/` - Upload new recording
- `GET /api/recordings/{id}/` - Get recording details
- `PUT /api/recordings/{id}/` - Update recording
- `DELETE /api/recordings/{id}/` - Delete recording
- `GET /api/recordings/{id}/analysis/` - Get analysis results
- `POST /api/recordings/{id}/trigger_analysis/` - Trigger analysis
- `GET /api/recordings/stats/` - Get user statistics

### User Profile
- `GET /api/profile/me/` - Get current user profile
- `PUT /api/profile/{id}/` - Update profile

### Analysis
- `GET /api/analysis/` - List all analysis results
- `GET /api/analysis/{id}/` - Get specific analysis

### System
- `GET /api/health/` - API health check

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Node.js 16+ (for mobile app)
- Google Cloud Platform account


## 🏗️ Project Structure

```
VoiceTrack_App/
├── backend/                    # Django REST API
│   ├── voicetrack_backend/    # Project settings
│   ├── api/                   # REST API app
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # API routing
│   │   └── admin.py           # Admin configuration
│   ├── requirements.txt       # Python dependencies
│   ├── app.yaml              # GCP App Engine config
│   └── manage.py             # Django management
├── mobile/                    # React Native app (coming soon)
├── docs/                      # Documentation
│   ├── DEVELOPMENT.md
│   ├── PROGRESS.md
│   ├── AWS_SETUP.md
│   └── GIT_GUIDE.md
└── README.md

```

## 💼 Skills Demonstrated

### Backend Development
- Django web framework & Django REST Framework
- RESTful API design and implementation
- Database design and modeling with PostgreSQL
- JWT authentication and authorization
- File upload handling and validation
- API documentation with Swagger/OpenAPI

### Cloud & DevOps
- Google Cloud Platform (App Engine, Cloud SQL, Cloud Storage)
- Cloud deployment and configuration
- Environment management (development/production)
- Database migration strategies
- Production-ready configuration

### Database
- PostgreSQL setup and optimization
- Database schema design with proper relationships
- Query optimization with indexes
- Migration management

### Best Practices
- Git version control with meaningful commits
- Environment variable management
- Separation of concerns (MVC pattern)
- RESTful API conventions
- Comprehensive documentation

## 📊 Database Schema

### Models
- **User** - Django's built-in User model
- **UserProfile** - Extended user information
- **VoiceRecording** - Audio file metadata
- **AnalysisResult** - Audio analysis results

### Relationships
- User → UserProfile (One-to-One)
- User → VoiceRecording (One-to-Many)
- VoiceRecording → AnalysisResult (One-to-One)

## 🧪 Testing the Live API

### Using cURL
```bash
# Register a user
curl -X POST https://voicetrack-app.ue.r.appspot.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"demo123","password_confirm":"demo123","first_name":"Demo","last_name":"User"}'

# Login
curl -X POST https://voicetrack-app.ue.r.appspot.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Get current user (use token from login)
curl -X GET https://voicetrack-app.ue.r.appspot.com/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using the Interactive Docs
Visit https://voicetrack-app.ue.r.appspot.com/api/docs/ to test all endpoints interactively!

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Django's built-in security
- CORS configuration for mobile apps
- Environment-based configuration
- Secure database connections via unix sockets
- Input validation on all endpoints

## 📈 Future Enhancements

- [ ] Audio processing with librosa (pitch, intensity, speech rate analysis)
- [ ] Real-time audio visualization
- [ ] ML model for voice pattern recognition
- [ ] CI/CD pipeline with automated testing
- [ ] Comprehensive test coverage
- [ ] Performance monitoring and logging
- [ ] Rate limiting and API throttling

## 🙏 Acknowledgments

Built as a portfolio project to demonstrate full-stack development skills including:
- Backend API development with Django
- Cloud infrastructure management with GCP
- Database design and optimization
- Mobile application development (React Native)
- DevOps and deployment practices

---
