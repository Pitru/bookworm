from models import *
from __init__ import db

def get_latest_reviews():
    return db.session.query(Review).order_by(Review.date.desc())[:3]

def get_best_books():
    all_books = db.session.query(Book).all()
    scores_for_books = [round(b.score,2) for b in all_books]
    books_and_scores = zip(scores_for_books, all_books)
    sort_books = sorted(books_and_scores, key=lambda t:t[0], reverse=True)
    books_with_score = [b[1] for b in sort_books if b[0] != 0]
    return books_with_score[:6]