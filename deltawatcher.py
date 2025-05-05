import requests
import json
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import socket
import threading
import time


def getLastTitle(name):
    res = requests.get(f'https://otvet.mail.ru/go-proxy/answer_json?q={name}&num=1&sf=0&sort=date')
    js = json.loads(res.text)
    return [js['results'][0]['question'],js['results'][0]['url']]

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

def send_to_android(title,text, ty,link):
    if fcm_token == '...':
        return False
    
    message = messaging.Message(
    data={
        'text': text, # Your text variable
        'title': title,
        'type': ty,
        'link': link
    },
    token=fcm_token, # The registration token of the device
    )
    
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
        return True
    except Exception as e:
        print('Error sending message:', e)
        return False


class SocketServerThread(threading.Thread):
    def __init__(self, host='0.0.0.0', port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.daemon = True  # Автоматическое завершение при выходе из main

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(1)
        print(f"[Сервер] Запущен на {self.host}:{self.port}")

        while self.running:
            try:
                client, addr = server.accept()
                print(f"[Сервер] Подключен клиент: {addr}")
                
                data = client.recv(1024).decode('utf-8')
                print(f"[Сервер] Получены данные: {data}")
                global fcm_token
                if len(fcm_token)>50:
                    fcm_token = data
                    print("токен обновлен!")
                client.send("OK".encode('utf-8'))
                client.close()
                
            except Exception as e:
                if self.running:
                    print(f"[Сервер] Ошибка: {e}")

        server.close()
        print("[Сервер] Остановлен")

    def stop(self):
        self.running = False
        # Создаем фейковое подключение чтобы выйти из accept()
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                (self.host, self.port))
        except:
            pass

server_thread = SocketServerThread()
server_thread.start()

init()

lastDelta = ""
lastUnder = ""
lastDeltaRus = ""
lastUnderRus1 = ""
lastUnderRus2 = ""

lastBluesky = ""
lastNewsletter = ""

while True:

    if fcm_token == "...":
        continue
    try:
        a = getLastTitle('Deltarune')
        
        if a != lastDelta:
            lastDelta = a;
            print("new Delta!")
            if not send_to_android('Новый вопрос!', a[0], 'delta',a[1]):
                lastDelta = ''
            
        
        a = getLastTitle('Undertale')
        if a != lastUnder:
            lastUnder = a;
            print("new Under!")
            if not send_to_android('Новый вопрос!', a[0], 'under',a[1]):
                lastUnder=''
            
        a = getLastTitle('Дельтарун')
        if a != lastDeltaRus:
            lastDeltaRus = a;
            print("new Дельта!")
            if not send_to_android('Новый вопрос!', a[0], 'deltarus',a[1]):
                lastDeltaRus=''
            
        a = getLastTitle('Андертейл')
        if a != lastUnderRus1:
            lastUnderRus1 = a;
            print("new тейл!")
            if not send_to_android('Новый вопрос!', a[0], 'underus1',a[1]):
                lastUnderRus1=''
            
        a = getLastTitle('Андертеил')
        if a != lastUnderRus2:
            lastUnderRus2 = a;
            print("new теил!")
            if not send_to_android('Новый вопрос!', a[0], 'underus2',a[1]):
                lastUnderRus2=''

        a = getLastBluesky()
        if a != lastBluesky:
            lastBluesky = a;
            print("new Bluesky!")
            if not send_to_android('Новый пост от Тоби!', a, 'bskytoby','https://bsky.app/profile/tobyfox.undertale.com'):
                lastBluesky = ''

        a = checkForNewsletter()
        if a != lastNewsletter:
            lastNewsletter = a;
            print("news Letter!")
            if not send_to_android('НОВОЕ ПИСЬМО!!!', a, 'newslet','https://mail.yandex.ru/#inbox'):
                lastNewsletter=''
    except Exception as e:
        print(f"ERROR! {e}")
    time.sleep(5)
        

