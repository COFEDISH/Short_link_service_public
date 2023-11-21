from flask import Flask, render_template, request, redirect
import string
import random
import socket
import json
import datetime
app = Flask(__name__)
server_address = ('37.193.53.6', 6379)
statistic_address = ('37.193.53.6', 50015)

def generate_short_link(length=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/', methods=['GET', 'POST'])
def home():
    generated_link = None
    if request.method == 'POST':
        original_link = request.form['user_input']
        if len(original_link) < 110000:
            short_link = generate_short_link()

            # Сохраняем короткую ссылку в базе данных (здесь ваш запрос к собственной БД)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect(server_address)
                    s.sendall(f"--file shrtlnks.data --query 'HSET shrtlnks {short_link} {original_link}'".encode())
                    print("Message sent successfully.", original_link)
                    data = s.recv(1024)
                    print(f"Response from server: {data.decode()}")
                except ConnectionRefusedError:
                    print("Connection to the server failed.")

            # Возвращаем короткую ссылку
            generated_link = f"http://37.193.53.6:5000/{short_link}"

    return render_template('index.html', generated_link=generated_link)

@app.route('/<short_link>')
def redirect_to_original(short_link):
    if short_link == 'favicon.ico':
        return "Not Found"
    # Получаем оригинальную ссылку из базы данных (здесь ваш запрос к собственной БД)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        try:
            s.connect(server_address)
            s.sendall(f"--file shrtlnks.data --query 'HGET shrtlnks {short_link}'".encode())
            data = s.recv(1024)
            original_link = data.decode()
        except ConnectionRefusedError:
            print("Connection to the server failed.")
            return "Internal Server Error"

    # Перенаправление на оригинальную ссылку, если она существует
    if original_link != "LINK_NOT_FOUND":
        # Перенаправление на оригинальную ссылку, если она существует
        if original_link != "LINK_NOT_FOUND":
            ip_address = request.remote_addr  # IP-адрес клиента
            timestamp = datetime.datetime.now().isoformat()  # Текущее время

            # Упаковываем данные в JSON
            json_data = {
                "ip_address": ip_address,
                "timestamp": timestamp,
                "original_link": original_link,
                "short_link": short_link
            }

            # Переводим данные в строку JSON
            json_string = json.dumps(json_data)

            # Отправляем данные на указанный адрес
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as statistic:
                try:
                    statistic.connect(statistic_address)
                    statistic.sendall(json_string.encode())
                    print("Statistics sent successfully.")
                except ConnectionRefusedError:
                    print("Connection to the statistics server failed.")
                    return "Internal Server Error"


        return redirect(original_link)
    else:
        return "Ссылка не найдена"




if __name__ == '__main__':
    app.run(host='192.168.0.105', port=5000, debug=True)


