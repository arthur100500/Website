from flask import request, Blueprint
import logging
from requests import get
import json

blueprint = Blueprint('alisa', __name__,
                      template_folder='templates')
logging.basicConfig(level=logging.INFO)
sessionStorage = {}
sessionMaps = {}
ip = 'http://127.0.0.1:5000'


@blueprint.route('/alisa', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        global sessionMaps
        sessionMaps = get(ip + '/api/maps').json()
        sessionStorage[user_id] = {
            'suggests': [
                {'title': "Покажи мне все рекорды", 'hide': True},
                {'title': "Покажи последнюю новость", 'hide': True},
                {'title': "Покажи новость под номером", 'hide': True},
                {"title": "Покажи сайт", "url": ip, "hide": True},
                {'title': "Покажи мне рекорды на карте", 'hide': True}
            ]
        }
        sessionStorage['get_map'] = False
        sessionStorage['News'] = False
        res['response']['text'] = 'Привет! Чем могу помочь?'
        res['response']['buttons'] = sessionStorage[user_id]['suggests']

        return
    if sessionStorage['News'] and req['request']['original_utterance'].isdigit():
        sessionStorage['News'] = False
        id = req['request']['original_utterance']
        news = get(ip + '/api/news/' + id).json()['news']
        if news:
            res['response']['text'] = '{}\n{}\nАвтор-{}\nДата - {}'.format(news['title'],
                                                                           news['content'],
                                                                           news['user']['name'],
                                                                           news['created_date'])
        else:
            res['response']['text'] = 'Такой новости нет.'
        res['response']['buttons'] = sessionStorage[user_id]['suggests']
        return
    if 'сайт' in req['request']['original_utterance'].lower():
        res['response']['text'] = "Отличный сайт, что бы просто похвалить."
        res['response']['buttons'] = sessionStorage[user_id]['suggests']
        sessionStorage['get_map'] = False
        return
    if not sessionStorage['News'] and 'номером' in req['request']['original_utterance'].lower():
        sessionStorage['News'] = True
        res['response']['text'] = "Какая по счету запись?"
        return

    if "покажи последнюю новость" in req['request']['original_utterance'].lower():
        news = get(ip + '/api/news').json()['news']
        if news:
            res['response']['text'] = '{}\n{}\nАвтор-{}\nДата - {}'.format(news['title'],
                                                                           news['content'],
                                                                           news['user']['name'],
                                                                           news['created_date'])
        else:
            res['response']['text'] = "К сожалению новостей нет."
        res['response']['buttons'] = sessionStorage[user_id]['suggests']
        return

    if 'все рекорды' in req['request']['original_utterance'].lower():
        records = get(ip + '/api/records').json()['records']
        if not records:
            res['response']['text'] = 'Рекордов еще нет(('
            res['response']['buttons'] = sessionStorage[user_id]['suggests']
            return
        string = ''
        for i in records:
            string += f'Карта {i[0]["map_name"]}\n'
            for j in range(len(i)):
                name = get(f'{ip}/api/user/{i[j]["user_id"]}').json()['name']
                string += f"{j + 1} место) {name['name']} очков: {i[j]['points']}\n"
        res['response']['text'] = string
        res['response']['buttons'] = sessionStorage[user_id]['suggests'][1:]
        sessionStorage['get_map'] = False
        return
    if sessionStorage['get_map']:
        maps = get_maps(False)
        if maps and req['request']['original_utterance'].lower() in maps:
            user_map = req['request']['original_utterance'].lower()
            records = get(ip + '/api/records/' + user_map).json()['records'][:10]
            if not records:
                res['response']['text'] = "На этой карте нет рекордов."
                res['response']['buttons'] = sessionStorage[user_id]['suggests']
                res['response']['buttons'] = sessionStorage[user_id]['suggests'][:-1] + get_maps()
                return
            string = ''
            for i in range(len(records)):
                name = get(f"{ip}/api/user/{records[i]['user_id']}").json()['name']['name']
                string += f"№{i + 1}) {name}\nочков: {records[i]['points']}\n"
            res['response']['text'] = string
            res['response']['buttons'] = sessionStorage[user_id]['suggests'][:-1] + get_maps()
            return
    elif 'карт' in req['request']['original_utterance'].lower() and 'картах' not in \
            req['request']['original_utterance'].lower():
        maps = get_maps()
        if maps:
            sessionStorage['get_map'] = True
            res['response']['text'] = 'На какой карте вам показать рекорды?'
            res['response']['buttons'] = sessionStorage[user_id]['suggests'][:-1] + maps
        else:
            res['response']['text'] = 'Пока что карт еще нету((('
            res['response']['buttons'] = sessionStorage[user_id]['suggests']
        return

    res['response']['text'] = "Не понимаю о чем вы. Скажите плжалуйста по другому."
    res['response']['buttons'] = sessionStorage[user_id]['suggests']


def get_maps(flag=True):
    if 'maps' in sessionMaps.keys():
        maps = [name['name_map'] for name in sessionMaps['maps']]
        if flag:
            maps = [
                {'title': suggest, 'hide': True}
                for suggest in maps
            ]
    else:
        maps = False
    return maps
