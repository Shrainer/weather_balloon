#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime, time, os, re, telebot, subprocess, requests
from threading import Thread

#-----------------------------------------------------------
Telegram_self_id = 1111111
TelegramBot_token = 'TelegramBotToken'
node_mcu = "http://10.54.0.46"
#-----------------------------------------------------------

TelegramBot = telebot.TeleBot(TelegramBot_token, threaded=False)

@TelegramBot.message_handler(content_types=["text"])
def telebot_messages(message):
    try:
        cid = message.chat.id
        if message.chat.id == Telegram_self_id:

            commandfull = message.text
            command = commandfull.split('@')[0]

            if command == '/meteo':
                TelegramBot.send_message(cid, "Запрашиваю данные, жди")
                try:
                    resp = requests.get(node_mcu)
                    resp = resp.text
                    resp = resp.split(',')
                    MSG = "Температура: " + resp[0] + "°С\nВлажность: " + resp[1] + "%"
                except Exception as e:
                    MSG = "Получить данные не удалось"
                TelegramBot.send_message(cid, MSG)

    except Exception as e:
        return False

#--- Startup Message ---------------------------------------
with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    uptime_string = str(datetime.timedelta(seconds = uptime_seconds))

TelegramBot.send_message(ADMINIDA, "Сервис запущен. Uptime сервера- " + uptime_string.split('.')[0])

#---- Telegram Thread ---------------------------------------
class TeleBot_treath(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            try:
                TelegramBot.polling(none_stop=True)
            except Exception as e:
                time.sleep(15)

#---- Put Data To Grafana Thread ----------------------------
class Grafana_treath(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global node_mcu
        while True:
            try:
                grafana_req = requests.get(node_mcu)
                grafana_req = grafana_req.text
                grafana_req = grafana_req.split(',')
                data_field="METEO,host=DACHA temperature=" + grafana_req[0] + ",humidity=" + grafana_req[1]
                grafana_curl = 'curl -i -XPOST "http://localhost:8086/write?db=TVSHOW" --data-binary "' + data_field + '"'
                os.system(grafana_curl)
            except Exception as e:
                time.sleep(60)
            time.sleep(1800)

#-----------------------------------------------------------
TeleBot_main = TeleBot_treath()
Grafana_main = Grafana_treath()

TeleBot_main.start()
Grafana_main.start()

