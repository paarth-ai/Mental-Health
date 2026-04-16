# Mental Health Survey Application

A comprehensive Django-based mental wellness platform for tracking mental health metrics, managing user activities, and connecting patients with healthcare professionals.

## 🎯 Features

- **User Authentication**: Secure signup/login system for patients and healthcare professionals
- **Mental Health Surveys**: Interactive survey forms to assess mental wellness indicators
- **Activity Tracking**: Log and track physical activities and wellness exercises
- **Thought Journal**: Personal journaling feature for mental health reflection
- **Doctor Dashboard**: Healthcare professionals can view patient profiles and provide suggestions
- **Location-Based Services**: Track user locations and find nearby psychiatrists
- **Results Analytics**: Visualize survey results and mental health indicators
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Django 6.0.4
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Hosting**: Vercel (Production)
- **Authentication**: Django built-in auth
- **Static Files**: WhiteNoise

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (venv)

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/paarth-ai/Mental-Health.git
   cd Mental-Health
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**:
   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
├── mental_health_survey/        # Main Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # URL routing
│   ├── wsgi.py / asgi.py       # Server configs
│   └── middleware.py            # Custom middleware
├── wellness/                     # Main Django app
│   ├── models.py                # Database models
│   ├── views.py                 # View logic
│   ├── forms.py                 # Form definitions
│   ├── urls.py                  # App URL routing
│   ├── indicators.py            # Survey indicators
│   ├── migrations/              # Database migrations
│   └── templates/               # HTML templates
├── static/                       # Static files (CSS, JS)
├── templates/                    # Base templates
├── manage.py                     # Django CLI
└── requirements.txt              # Python dependencies
```

## 🗄️ Database Models

- **User & Authentication**: Built-in Django User model
- **UserProfile**: Extended user information with location
- **SurveyResponse**: User survey responses and mental health data
- **ThoughtEntry**: User journal entries
- **PhysicalActivity**: Activity tracking and preferences
- **DoctorProfile**: Healthcare professional profiles
- **PatientDoctorAssignment**: Doctor-patient relationships
- **MedicalResult**: Medical test results

## 🔐 Environment Variables

Create a `.env` file in the project root (development only):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://...  # For production PostgreSQL
```

## 🌐 Production Deployment

The application is configured to:
- Use PostgreSQL when `DATABASE_URL` is set (Vercel)
- Fallback to SQLite in `/tmp` on Vercel
- Use local SQLite in development

### Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

## 📝 API Endpoints

- `/` - Home page
- `/signup/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/survey/` - Take mental health survey
- `/results/` - View survey results
- `/activities/` - Activity tracking
- `/thought-journal/` - Thought journal
- `/doctor-dashboard/` - Doctor view (staff only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit and push
5. Open a pull request

## 📄 License

This project is open source. See [LICENSE](LICENSE) for details.

## 👥 Author

**Paarth AI** - Mental Health Survey Platform Developer

---

**Live Demo**: [https://mental-health-mscp.vercel.app](https://mental-health-mscp.vercel.app)

For issues and feature requests, please use the [GitHub Issues](https://github.com/paarth-ai/Mental-Health/issues) page.
