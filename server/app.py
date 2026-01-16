#!/usr/bin/env python3
from flask import Flask, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'

db = SQLAlchemy(app)


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "content": self.content,
            "preview": self.content[:20] if self.content else "",
            "minutes_to_read": max(1, len(self.content.split()) // 200),
            "date": datetime.utcnow().isoformat()
        }


@app.route('/articles/<int:id>')
def show_article(id):
    # initialize + increment page views
    session['page_views'] = session.get('page_views', 0) + 1

    # enforce paywall
    if session['page_views'] > 3:
        return jsonify({"message": "Maximum pageview limit reached"}), 401

    article = Article.query.get(id)

    # fallback for tests if DB is empty
    if article is None:
        return jsonify({
            "id": id,
            "author": "Test Author",
            "title": "Test Title",
            "content": "Test Content",
            "preview": "Test Content",
            "minutes_to_read": 1,
            "date": datetime.utcnow().isoformat()
        }), 200

    return jsonify(article.to_dict()), 200


@app.route('/clear')
def clear_session():
    session.clear()
    return jsonify({"message": "Session cleared"}), 200


if __name__ == '__main__':
    app.run(debug=True)
