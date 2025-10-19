# SPF Study Coach

A Flask-based study application designed to help police officers prepare for MCQ and SAQ exams. Features intelligent spaced repetition, guided SAQ practice, and comprehensive cheat sheets.

## Features

- **MCQ Drills**: Quick 10-question practice sessions with instant feedback
- **SAQ Practice**: Structured answer practice with keyword-based grading
- **Cheat Sheets**: Interactive flashcards for quick reference
- **Progress Tracking**: Leitner box system for spaced repetition
- **Weak Area Focus**: Automatic identification and prioritization of weak topics
- **Modern UI**: Clean, responsive design with dark mode support

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Vercel Postgres
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Deployment**: Vercel

## Local Development

### Prerequisites

- Python 3.8+
- Vercel CLI (for deployment)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd spf-study-coach
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export SECRET_KEY="your-secret-key"
export POSTGRES_HOST="your-postgres-host"
export POSTGRES_DATABASE="your-database"
export POSTGRES_USER="your-username"
export POSTGRES_PASSWORD="your-password"
export POSTGRES_PORT="5432"
```

4. Run the application:
```bash
python api/index.py
```

## Vercel Deployment

### Prerequisites

- Vercel account
- Vercel CLI installed

### Steps

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables in Vercel dashboard:
   - `SECRET_KEY`: Random secret key for sessions
   - `POSTGRES_HOST`: Your Vercel Postgres host
   - `POSTGRES_DATABASE`: Your database name
   - `POSTGRES_USER`: Your database user
   - `POSTGRES_PASSWORD`: Your database password
   - `POSTGRES_PORT`: 5432

5. The database will be automatically initialized on first deployment.

## Database Schema

The application uses the following tables:

- `topics`: Study topics (BWC, SALUTE, etc.)
- `mcq`: Multiple choice questions
- `saq`: Short answer questions
- `flashcards`: Quick reference cards
- `progress`: User progress tracking
- `sessions`: Study session records

## Study Topics Covered

- **BWC**: Body Worn Camera procedures and exceptions
- **SALUTE**: Armed incident reporting format
- **AOJ**: Use of force principles and ACTive-PUNCH framework
- **NWD**: National Wanted Database checks
- **Scams**: Fraud and cheating offences (S415/416/420)
- **Roadblock**: Traffic enforcement procedures
- **Exhibits**: Evidence handling and chain of custody
- **Wildlife**: Animal incident response and AVS procedures
- **Constitutional Rights**: Article 9 and legal protections
- **Offensive Weapons**: S453 Penal Code and S6 CESOWA

## Usage

1. **Dashboard**: View weak areas and quick access to all features
2. **MCQ Drill**: Practice with 10 random questions, get instant feedback
3. **SAQ Practice**: Use the scaffold (Define → Interpret → Apply → Conclusion)
4. **Cheat Sheets**: Browse flashcards by topic for quick reference
5. **Review**: Focus on items with low accuracy for targeted improvement

## Keyboard Shortcuts

- **MCQ**: Press 1-4 to select answers, Enter to submit
- **SAQ**: Ctrl+Enter to grade, Ctrl+M to show model answer
- **General**: Escape to close modals, Ctrl+K for search

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please create an issue in the repository or contact the development team.
