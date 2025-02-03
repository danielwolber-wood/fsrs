import curses
import sys
import random 
import argparse
import textwrap
import requests
from datetime import datetime, timezone
from pathlib import Path
import random 


import requests

def create_card(host, port, front_text, back_text):
    url = f'http://{host}:{port}/cards/create'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "front_text": front_text,
        "back_text": back_text
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()  # Assuming the response is JSON

def get_card(host, port, card_id):
    url = f'http://{host}:{port}/cards/{card_id}'
    response = requests.get(url)
    return response.json()  # Assuming the response is JSON

def get_reviews(host, port):
    url = f'http://{host}:{port}/reviews'
    response = requests.get(url)
    return response.json()  # Assuming the response is JSON

def get_review(host, port, review_id):
    url = f'http://{host}:{port}/reviews/{review_id}'
    response = requests.get(url)
    return response.json()  # Assuming the response is JSON

def get_due_cards(host, port):
    url = f'http://{host}:{port}/due'
    response = requests.get(url)
    return response.json()  # Assuming the response is JSON


def get_all_cards(host, port):
    url = f'http://{host}:{port}/cards'
    response = requests.get(url)
    return response.json()  # Assuming the response is JSON

def get_due_cards_manual(host, port):
    all_cards = get_all_cards(host, port)
    #print(due)
    cards = all_cards["data"]

    all_cards = get_all_cards(host, port)
    all_cards = all_cards["data"]
    #print(all_cards)

    due_cards = list()

    for card in all_cards:
        #print(card)
        due_date = card["due"]
        native_datetime = datetime.fromisoformat(due_date)
        #print(native_datetime)
        if native_datetime < datetime.now(timezone.utc):
            due_cards.append(card)

    return due_cards


def create_review(host, port, card_id, rating):
    url = f'http://{host}:{port}/reviews/create'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "card_id": card_id,
        "rating": rating
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()  # Assuming the response is JSON

def update_card(host, port, card_id, front_text, back_text):
    url = f'http://{host}:{port}/update/{card_id}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "card_id": card_id,
        "front_text": front_text,
        "back_text": back_text
    }
    response = requests.put(url, json=payload, headers=headers)
    return response.json()  # Assuming the response is JSON



def display_flashcard(stdscr, front, back):
    height, width = stdscr.getmaxyx()

    def display_text(text, start_y):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            wrapped = textwrap.wrap(line, width-4)  # -4 for margins
            for j, wrap_line in enumerate(wrapped):
                y = start_y + i + j
                if y < height-3:  # Leave room for prompt
                    stdscr.addstr(y, (width-len(wrap_line))//2, wrap_line)

    stdscr.clear()
    display_text(front, height//3)
    stdscr.refresh()

    while stdscr.getch() != ord(' '):
        pass

    stdscr.clear()
    display_text(back, height//3)
    stdscr.addstr(height-2, 2, "Again (1)\t Hard (2) \t Good (3) \t Easy (4)")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in [ord("1")]:
            return 1
        elif key in [ord("2")]:
            return 2
        elif key in [ord("3")]:
            return 3
        elif key in [ord("4")]:
            return 4

def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=8000)
    args = parser.parse_args()

    host = args.host
    port = args.port

    curses.curs_set(0)
    stdscr.nodelay(1)

    due_cards = get_due_cards_manual(host, port)

    while due_cards:
        chosen_card = random.choice(due_cards)
        front_text = chosen_card["front_text"]
        back_text = chosen_card["back_text"]
        card_id = chosen_card["card_id"]

        card_rating = display_flashcard(stdscr=stdscr, front=front_text, back=back_text)
        response = create_review(host, port, card_id, card_rating)

        due_cards = get_due_cards_manual(host, port)
        #cards = due["data"]

if __name__ == "__main__":
    curses.wrapper(main)
    #test()
