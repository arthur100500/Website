from flask import Blueprint, jsonify, request
from data import db_session
from data.news import News

blueprint = Blueprint('news_api', __name__,
                      template_folder='templates')


@blueprint.route('/api/news')
def get_news():
    session = db_session.create_session()
    news = session.query(News).all()
    if not news:
        return jsonify({'news': False})
    return jsonify(
        {
            'news':
                news[-1].to_dict(only=('title', 'content', 'user.name', 'created_date'))
        }
    )


@blueprint.route('/api/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    session = db_session.create_session()
    news = session.query(News).all()
    if not 0 < news_id <= len(news):
        return jsonify({'news': False})
    return jsonify(
        {
            'news': news[news_id - 1].to_dict(only=('title', 'content',
                                                    'user.name', 'created_date'))
        }
    )


@blueprint.route('/api/news', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    news = News(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id']
    )
    session.add(news)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        return jsonify({'error': 'Not found'})
    session.delete(news)
    session.commit()
    return jsonify({'success': 'OK'})
