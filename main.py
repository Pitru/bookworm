from flask import Blueprint, redirect, render_template, url_for, request, flash
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from __init__ import db
from api_connection import search_book, search_in_googlebooks
from utils import *
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', books=get_best_books(), reviews=get_latest_reviews(), main_page=True)

@main.route('/profile')
@login_required
def profile():
    reviews = current_user.reviews
    favs = current_user.fav_books
    wishes = current_user.wish_books
    return render_template('profile/profile.html', user=current_user, 
                           reviews=reviews, favs=favs, wishes=wishes)

@main.route('/profile/change_password')
@login_required
def profile_change_password():
    return render_template('/profile/password.html')

@main.route('/profile/change_password', methods=['POST'])
@login_required
def profile_change_password_post():
    old = request.form.get('old_password')
    new1 = request.form.get('new_password1')
    new2 = request.form.get('new_password2')
    if not check_password_hash(current_user.password, old):
        flash('Incorrect old password')
        return redirect(url_for('main.profile_change_password'))
    if not new1 or not new2:
        flash('New password can not be empty')
        return redirect(url_for('main.profile_change_password'))
    if new1 != new2:
        flash('New passswords are not same')
        return redirect(url_for('main.profile_change_password'))
    current_user.password = (generate_password_hash(new1, method='sha256'))
    db.session.commit()
    
    return redirect(url_for('main.profile'))

@main.route('/profile/edit')
@login_required
def profile_edit():
    return render_template('profile/editprofile.html', user=current_user)

@main.route('/profile/edit', methods=['POST'])
@login_required
def profile_edit_post():
    name = request.form.get('name')
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user == current_user or not user:
        current_user.name = name
        current_user.email = email
        db.session.commit()
        
        return redirect(url_for('main.profile'))
    else:
        flash("You can not set other user's email")
        return redirect(url_for('main.profile_edit'))

@main.route('/book/<id>')
def book(id):
    if not Book.query.filter_by(google_id=id).first():
        book_data = search_book(id)
        book = Book(title = book_data['title'], 
                        description = book_data['description'],
                        google_id = book_data['id'], 
                        cover_link = book_data['cover'])
        
        for author in book_data['authors']:
            if not Author.query.filter_by(name = author).first():
                new_author = Author(name=author)
                db.session.add(new_author)
                book.authorship.append(new_author)
            else:
                book.authorship.append(Author.query.filter_by(name = author).first())
                
        db.session.add(book)
        db.session.commit()
    else:
        book = Book.query.filter_by(google_id=id).first()
    book_data={}
    book_data['id'] = book.google_id
    book_data['title'] = book.title
    book_data['authors'] = book.authorship
    book_data['description'] = book.description
    book_data['cover'] = book.cover_link
    if current_user.is_authenticated:
        user_has_review = bool(Review.query.filter_by(user_id=current_user.id, book_id=book.id).first())
        in_favs = current_user in book.users_fav
        in_wishes = current_user in book.users_wish
        user_options = True
    else:
        user_has_review = False
        in_favs = False
        in_wishes = False
        user_options = False
    return render_template('book.html', book=book_data, has_review=user_has_review, 
                           in_fav_list = in_favs, in_wish_list=in_wishes, user_options=user_options)

@main.route('/book/<id>/review')
@login_required
def add_review(id):
    book = Book.query.filter_by(google_id=id).first()
    rev = Review.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    if rev:
        return render_template('review.html', book=book, score=rev.score, text=rev.review_text, delete=True)
    else:
        return render_template('review.html', book=book)


@main.route('/book/<id>/review', methods=['GET','POST'])
@login_required
def add_review_post(id):
    book = Book.query.filter_by(google_id=id).first()
    if not request.form.get('score'):
        flash("Review needs to has filled score")
        return render_template('review.html', book=book)
    
    rev = Review.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    score = float(request.form.get('score'))
    review_text = request.form.get('text')
    if not rev:
        rev = Review(book_id=book.id, user_id=current_user.id, score=score, review_text=review_text)
        db.session.add(rev)
    else:
        rev.score = score
        rev.review_text = review_text
    db.session.commit()
    
    return redirect(url_for('main.book', id=book.google_id))
 
@main.route('/book/<id>/review/delete', methods=['GET'])
@login_required
def review_delete(id):
    book = Book.query.filter_by(google_id=id).first()
    rev = Review.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    db.session.delete(rev)
    db.session.commit()
    return redirect(url_for('main.book', id=id))
    
@main.route('/add_to_favourites/<id>')
@login_required
def add_to_favourites(id):
    book = Book.query.filter_by(google_id=id).first()
    
    if book in current_user.fav_books:
        current_user.fav_books.remove(book)
    else:
        current_user.fav_books.append(book)
    db.session.commit()

    return redirect(url_for('main.book', id=book.google_id))

@main.route('/add_to_wish/<id>')
@login_required
def add_to_wishes(id):
    book = Book.query.filter_by(google_id=id).first()
    
    if book in current_user.wish_books:
        current_user.wish_books.remove(book)
    else:
        current_user.wish_books.append(book)
    db.session.commit()

    return redirect(url_for('main.book', id=book.google_id))


@main.route('/search', methods=['GET', 'POST'])
def search_get():
    if request.method == 'POST':
        query = request.form['q']
    elif request.method == 'GET':
        query = request.args.get('q')
    return render_template('search.html', books = search_in_googlebooks(query), last_search=query)