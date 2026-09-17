# Behavioral & Preference Analysis Web Application

A Flask-based web application that analyzes users' responses and preferences through NLP-based emotional analysis and interactive questionnaire modules.

## Features

- User registration and login
- Secure password hashing
- Session-based authentication
- Emotional maturity and communication analysis
- VADER-based sentiment analysis
- Dynamic preference questionnaires
- Personalized profile generation
- Lifestyle & Shopping analysis
- Cars & Mobility analysis
- Books & Reading analysis
- Movies & Entertainment analysis
- Hobbies & Interests analysis
- Score visualization using progress bars
- User-specific assessment history
- SQLite database for persistent data storage
- Responsive frontend using Bootstrap

## Modules

### 1. Emotional Maturity

Users describe a real-life situation involving criticism, failure, disagreement, or a difficult decision.

The application analyzes the response using VADER sentiment analysis and rule-based scoring to calculate:

- Positivity
- Negativity
- Neutrality
- Empathy
- Impulsiveness
- Emotional Stability
- Communication Style
- Estimated Mental Maturity Age

### 2. Lifestyle & Shopping

Analyzes preferences related to:

- Practicality
- Trends
- Product quality

### 3. Cars & Mobility

Analyzes preferences related to:

- Practicality
- Comfort
- Performance

### 4. Books & Reading

Analyzes preferences related to:

- Imagination
- Learning
- Reading consistency

### 5. Movies & Entertainment

Analyzes preferences related to:

- Story
- Emotion
- Adventure

### 6. Hobbies & Interests

Analyzes preferences related to:

- Creativity
- Learning
- Social interaction

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap 5

### Backend
- Python
- Flask

### Database
- SQLite
- SQLAlchemy

### Authentication
- Flask-Login
- Werkzeug password hashing

### NLP
- VADER Sentiment Analysis

## Project Structure

```text
Behavioral-Preference-Analysis/
│
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── dashboard.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── questionnaire.html
    ├── result.html
    ├── history.html
    └── section_placeholder.html