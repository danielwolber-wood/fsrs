
# FSRS Flashcard API

A RESTful API for managing flashcards using the Free Spaced Repetition Scheduler (FSRS) algorithm for optimal learning efficiency.

## Overview

This API provides a backend service for flashcard applications, implementing the FSRS algorithm to schedule card reviews based on user performance. The system tracks card metadata, review history, and automatically schedules future reviews to maximize memory retention with minimal review sessions.

## Features

- Create and manage flashcards with front and back content
- Intelligent review scheduling using the FSRS algorithm
- Track review history and performance
- Query cards due for review
- Update existing card content

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite
- **Scheduler**: FSRS (Free Spaced Repetition Scheduler)
- **Language**: Python 3

## Installation

1. Clone the repository
```bash
git clone https://github.com/danielwolber-wood/fsrs
cd fsrs
```

2. Set up a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install fastapi uvicorn fsrs pydantic sqlite3
```

## Running the Application

Start the server with:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /hello`: Check if the server is running

### Cards
- `POST /cards/create`: Create a new flashcard
- `GET /cards`: Retrieve all flashcards
- `GET /cards/{card_id}`: Get a specific card by ID
- `PUT /update/{card_id}`: Update a card's content
- `GET /due`: Get all cards due for review

### Reviews
- `POST /reviews/create`: Submit a review for a card
- `GET /reviews/{card_id}`: Get all reviews for a specific card
- `GET /reviews/`: Get all reviews in the system

## Data Models

### Card Create Schema
```python
{
    "front_text": "Question text",
    "back_text": "Answer text"
}
```

### Card Update Schema
```python
{
    "front_text": "Updated question text",  # Optional
    "back_text": "Updated answer text"      # Optional
}
```

### Review Create Schema
```python
{
    "card_id": 123456789,
    "rating": 4  # Rating from 1-4 based on FSRS rating system
}
```

## FSRS Rating System

The API uses the FSRS standard rating system:
- `1`: "Again" - Complete failure to recall
- `2`: "Hard" - Significant effort to recall
- `3`: "Good" - Some effort to recall
- `4`: "Easy" - Perfect recall with no effort

## Database Schema

### Cards Table
- `card_id`: Unique identifier for the card
- `state`: Current state in the FSRS system
- `step`: Current step in the learning process
- `stability`: How stable the memory is
- `difficulty`: How difficult the card is
- `due`: When the card is due for review (ISO date string)
- `last_review`: When the card was last reviewed (ISO date string)
- `front_text`: The question or prompt text
- `back_text`: The answer text

### Reviews Table
- `card_id`: Reference to the card
- `rating`: The rating given during review (1-4)
- `time`: When the review occurred (ISO date string)
- `duration`: How long the review took (can be null)

## Usage Examples

### Creating a new card
```bash
curl -X POST "http://localhost:8000/cards/create" \
     -H "Content-Type: application/json" \
     -d '{"front_text": "What is FSRS?", "back_text": "Free Spaced Repetition Scheduler"}'
```

### Getting cards due for review
```bash
curl -X GET "http://localhost:8000/due"
```

### Submitting a review
```bash
curl -X POST "http://localhost:8000/reviews/create" \
     -H "Content-Type: application/json" \
     -d '{"card_id": 1738555913641, "rating": 3}'
```

## Troubleshooting

If you encounter database errors, check:
1. The `cards.db` file has proper permissions
2. The database was initialized correctly
3. The sqlite3 version is compatible with your system

## License

MIT License

Copyright (c) 2025 Daniel Wood

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
