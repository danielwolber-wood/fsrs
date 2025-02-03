import sqlite3
from datetime import datetime
from typing import Optional, List

import fsrs
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter, HTTPException

app = FastAPI()

CARD_DB = "cards.db"

class CardCreateSchema(BaseModel):
    front_text: str
    back_text: str

class CardUpdateSchema(BaseModel):
    front_text: Optional[str]
    back_text: Optional[str]

class ReviewCreateSchema(BaseModel):
    card_id: int
    rating: int

@app.get("/hello")
def root() -> dict:
    return {"message": "Server is running", "status": "success"}

@app.post("/cards/create")
def create_card(
    new_card: CardCreateSchema,
) -> dict:
    """Create a new card and return its ID"""
    try:
        with sqlite3.connect(CARD_DB) as conn:
            base_card = fsrs.Card()
            print(new_card)
            print(base_card)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Cards (
                           card_id, 
                           state,
                           step, 
                           stability, 
                           difficulty, 
                           due, 
                           last_review, 
                           front_text, 
                           back_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                               base_card.card_id, 
                               base_card.state, 
                               base_card.step, 
                               base_card.stability, 
                               base_card.difficulty, 
                               datetime.isoformat(base_card.due), 
                               #datetime.isoformat(base_card.last_review), 
                               None, # last_review is None on cards which have just been created
                               new_card.front_text, 
                               new_card.back_text))
            conn.commit()
            return {"message": "Card created successfully", "status": "success", "data": base_card.card_id}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/cards")
def get_all_cards() -> dict:
    try:
        with sqlite3.connect(CARD_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Cards;")
            results = cursor.fetchall()
            dict_results = [dict(r) for r in results]
            return {"message": "Retrieval successful", "status": "success", "data": dict_results}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/cards/{card_id}")
def get_card_info(
        card_id: int
    ) -> dict:
    try:
        with sqlite3.connect(CARD_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Cards WHERE card_id = ?", (card_id,))
            results = cursor.fetchall()
            dict_results = [dict(r) for r in results]
            return {"message": "Data retrieved successfully", "status": "success", "data": dict_results}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.put("/update/{card_id}")
def update_card(
    card_update: CardUpdateSchema,
    card_id: int
) -> dict:
    """Update a card's front or back text"""
    try:
        with sqlite3.connect(CARD_DB) as conn:
            cursor = conn.cursor()
            if card_update.back_text is None:
                cursor.execute("UPDATE Cards SET front_text = ? WHERE card_id = ?", (card_update.front_text, card_id))
            elif card_update.front_text is None:
                cursor.execute("UPDATE Cards SET back_text = ? WHERE card_id = ?", (card_update.back_text, card_id))
            else:
                cursor.execute("UPDATE Cards SET back_text = ?, front_text = ? WHERE card_id = ?", (card_update.back_text, card_update.front_text, card_id))

            conn.commit()
            return {"message": "Card updated successfully", "status": "success"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.post("/reviews/create")
def create_review(
    review: ReviewCreateSchema,
) -> dict:
    """Log a review for a card"""

    try:
        with sqlite3.connect(CARD_DB) as conn:
        # get card from db
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Cards WHERE card_id = ?", (review.card_id, ))
            card_data = cursor.fetchone()

            # fsrs.Card looks like 
            # Card(card_id=1738555913641, state=1, step=0, stability=0.40255, difficulty=7.1949, due=2025-02-03 04:13:08.150801+00:00, last_review=2025-02-03 04:12:08.150801+00:00)
            # But in database, due and last_review are ISO datestrings
            if card_data["last_review"] is None:
                last_review = None
            else:
                last_review = datetime.fromisoformat(card_data["due"])
            print(card_data["due"])
            print(card_data["last_review"])
            card = fsrs.Card(
                    card_id=card_data["card_id"], 
                    state=card_data["state"], 
                    step=card_data["step"], 
                    stability = card_data["stability"], 
                    difficulty = card_data["difficulty"], 
                    due = datetime.fromisoformat(card_data["due"]), 
                    #last_review = datetime.fromisoformat(card_data["last_review"])
                    last_review = last_review
                    )

            scheduler = fsrs.Scheduler()
            card, review_log = scheduler.review_card(card, review.rating)

            cursor.execute("""
        UPDATE Cards 
        SET 
            state = ?,
            step = ?,
            stability = ?,
            difficulty = ?,
            due = ?,
            last_review = ?
        WHERE
            card_id = ?
        """, (
            card.state, 
            card.step, 
            card.stability, 
            card.difficulty, 
            datetime.isoformat(card.due), 
            datetime.isoformat(card.last_review), 
            card.card_id
                )
           )

            cursor.execute("INSERT INTO Reviews (card_id, rating, time, duration) VALUES (?, ?, ?, ?);", (review_log.card_id, review_log.rating, datetime.isoformat(review_log.review_datetime), None))
            conn.commit()
            return {"message": "Review successfully created", "status": "success"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/reviews/{card_id}")
def get_card_reviews(
    card_id: int
    ) -> dict:
    try:
        with sqlite3.connect(CARD_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Reviews WHERE card_id = ?", (card_id,))
            results = cursor.fetchall()
            dict_results = [dict(r) for r in results]
            return {"message": "Reviews retrieved successfully", "status": "success", "data": dict_results}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/reviews/")
def get_all_reviews() -> dict:
    try:
        with sqlite3.connect(CARD_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Reviews")
            results = cursor.fetchall()
            dict_results = [dict(r) for r in results]
            return {"message": "Reviews retrieved successfully", "status": "success", "data": dict_results}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/due")
def get_due_cards() -> dict:
    """Get all cards past their due date"""
    print('into due')
    try:
        with sqlite3.connect(CARD_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            print(datetime.now().isoformat())
            cursor.execute("SELECT * FROM Cards WHERE due < ?", (datetime.now().isoformat(), ))
            results = cursor.fetchall()
            print(f"results is {results}")
            dict_results = [dict(r) for r in results]
            print(f"dict_results is {dict_results}")
            return {"message": "retrieval successful", "status": "success", "data": dict_results}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

def init_db():
    try:
        with sqlite3.connect(CARD_DB) as conn:
            create_cards_statement = """
        CREATE TABLE IF NOT EXISTS Cards(
        card_id INT PRIMARY KEY,
        state INT,
        step INT,
        stability FLOAT,
        difficulty FLOAT,
        due TEXT,
        last_review TEXT,
        front_text TEXT,
        back_text TEXT);
            """
            create_reviews_statement = """
        CREATE TABLE IF NOT EXISTS Reviews(
        card_id INT,
        rating INT,
        time TEXT,
        duration TEXT,
        FOREIGN KEY (card_id) REFERENCES Cards(card_id));
            """
            cursor = conn.cursor()
            cursor.execute(create_cards_statement)
            cursor.execute(create_reviews_statement)
            conn.commit()
    except Exception as e:
        print(f'Startup error: {e}')

def main():
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    main()
