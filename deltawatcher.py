import requests
import json
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from flask import Flask, request

def getLastTitle(name):
    res = requests.get(f'https://otvet.mail.ru/go-proxy/answer_json?q={name}&num=1&sf=0&sort=date')
    js = json.loads(res.text)
    return f"{js['results'][0]['question']}"

def getTitles():
    print(getLastTitle('Deltarune'))
    print(getLastTitle('Undertale'))
    print(getLastTitle('Дельтарун'))
    print(getLastTitle('Андертейл'))
    print(getLastTitle('Андертеил'))


def getLastBluesky():
    res = requests.get(f'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=did%3Aplc%3Avshnclkqqguyg6xcz6q7g65k&filter=posts_and_author_threads&includePins=false&limit=1')
    js = json.loads(res.text)
    return js['feed'][0]['post']['record']['text']

def checkForNewsletter():
    response = requests.get("https://toby.fangamer.com/newsletters/")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(class_='text-yellow-300')
        return elements[2].decode_contents().strip()

def init():
    cred = credentials.Certificate('secret.json')
    firebase_admin.initialize_app(cred)



fcm_token = '...'

def send_to_android(text, title, ty):

    message = messaging.Message(
    data={
        'text': text, # Your text variable
        'title': title,
        'type': ty
    },
    token=fcm_token, # The registration token of the device
    )
    
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print('Error sending message:', e)


@app.route('/api/save_token', methods=['POST'])
def handle_message():
    data = request.json  # Получаем данные от Android
    print("Получено сообщение:", data)
    
    # Здесь можно сохранить данные в БД или выполнить другие действия
    response = {"status": "success", "message": "Данные получены!"}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Сервер доступен на всех интерфейсах

