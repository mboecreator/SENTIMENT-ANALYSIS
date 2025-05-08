# Sentiment Analysis System

A web-based sentiment analysis system that uses pretrained Twitter models to analyze text sentiment and emotions.

## Features

- User authentication (login/register)
- Real-time text sentiment analysis
- Emotion detection
- Batch processing capabilities
- Detailed analytics and reports
- Modern and responsive UI

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd sentiment-analysis
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
sentiment-analysis/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── init_db.py          # Database initialization script
├── requirements.txt    # Project dependencies
├── static/             # Static files (CSS, JS, images)
│   └── css/
│       └── style.css   # Stylesheet
└── templates/          # HTML templates
    ├── index.html      # Login page
    ├── register.html   # Registration page
    ├── dashboard.html  # User dashboard
    ├── about.html      # About page
    ├── services.html   # Services page
    └── contact.html    # Contact page
```

## Usage

1. Register a new account or login with existing credentials
2. On the dashboard, you can:
   - Analyze single text inputs
   - Upload files for batch processing
   - View analysis history
   - Generate reports

## Security Features

- Password hashing using Werkzeug
- Session management
- CSRF protection
- Input validation
- Secure password requirements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 