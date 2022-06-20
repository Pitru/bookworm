from __init__ import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

authorship = db.Table('authorship',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

fav = db.Table('fav_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)  

wish = db.Table('wish_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    google_id = db.Column(db.String)
    cover_link = db.Column(db.String)
    book_reviews = db.relationship('Review')
    authorship = db.relationship('Author', secondary=authorship, lazy='subquery', back_populates='authorship')
    users_fav = db.relationship('User', secondary=fav, back_populates='fav_books')
    users_wish = db.relationship('User', secondary=wish, back_populates='wish_books')
    
    @hybrid_property
    def score(self):
        number_of_reviews =0
        for b in self.book_reviews:
            number_of_reviews+=1
        sum=0
        if number_of_reviews == 0:
            return 0
        for r in self.book_reviews:
            sum+=r.score
        avg = sum/number_of_reviews
        return avg
        
    @score.expression
    def score(cls):
        number_of_reviews =0
        for b in cls.book_reviews:
            number_of_reviews+=1
        sum=0
        if number_of_reviews == 0:
            return 0
        for r in cls.book_reviews:
            sum+=r.score
        avg = sum/number_of_reviews
        return avg 
    
    def __repr__(self):
        return self.title
    
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    authorship = db.relationship('Book', secondary=authorship, lazy='subquery', back_populates='authorship')
    def __repr__(self):
        return str(self.name)
        
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)
    fav_books = db.relationship('Book', secondary=fav, lazy='subquery', back_populates='users_fav')
    wish_books = db.relationship('Book', secondary=wish, lazy='subquery', back_populates='users_wish')
    def __repr__(self):
        return self.name
        
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    book = db.relationship("Book", back_populates='book_reviews')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    review_text = db.Column(db.String, nullable=True)
    
    def __repr__(self):
        return self.review_text

