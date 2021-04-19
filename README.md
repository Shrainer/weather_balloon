# Метеозонд

Проект решает задачу мониторинга температуры и влажности на удаленной площадке, в моем случае на даче.
Для этого был собран метеозонд, который достаточно подключить к питанию.

![Alt text](https://github.com/shrainer/weather_balloon/blob/main/img/baloon.png "Telegram Bot")

Для проекта были использованы:
 1. Контроллер <b>ESP8266 NodeMCU</b>
 2. Датчик температуры и влажности <b>DHT22</b>
 3. Резистор на <b>10кОм</b>
 4. Одноплатный компьютер <b>Raspberry Pi</b>
 5. Кроссплатформенный мессенджер <b>Telegram</b>

## Сценарии применения:

| Telegram  | Grafana |
| ------------- | ------------- |
| ![Alt text](https://github.com/shrainer/weather_balloon/blob/main/img/screen_1.jpg "Telegram Bot")  | ![Alt text](https://github.com/shrainer/weather_balloon/blob/main/img/weather_photo.jpg "Grafana")  |



## Схема взаимодействия компонентов:

![Alt text](https://github.com/shrainer/weather_balloon/blob/main/img/meteo_flow.png "Meteo Flow")
<br>
<br>
## ESP8266 NodeMCU + DHT22:
![Alt text](https://github.com/shrainer/weather_balloon/blob/main/img/nodemcu_dht22.png "NodeMCU")

Передача данных происходит через однопроводный протокол, требующий точной синхронизации.<br>
Для получения данных используется библиотека <b>DHTesp</b>.<br>
Для подключения к WiFi - библиотека <b>ESP8266WiFi</b>.<br>
Для Web сервера - библиотека <b>ESP8266WebServer</b>.<br>
Скетч для NodeMCU в файле https://github.com/shrainer/weather_balloon/blob/main/nodemcu.ino
<br>

## Raspberry Pi + Python + Grafana:

На одноплатном компьютере запущен скрипт bot.py, демонизированный с помощью [Supervisor](http://supervisord.org/).<br>
Скрипт выполняет следующие функции:<br><br>
Слушает команды в Telegram. В случае получения команды <b>/meteo</b> получает данные с NodeMCU и отправляет их в чат.
``` python
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
```

Раз в 30 минут получает данные с NodeMCU и отправляет их в базу данных InfluxDB, откуда они визуализируются с помощью Grafana.
``` python
try:
    grafana_req = requests.get(node_mcu)
    grafana_req = grafana_req.text
    grafana_req = grafana_req.split(',')
    data_field="METEO,host=DACHA temperature=" + grafana_req[0] + ",humidity=" + grafana_req[1]
    grafana_curl = 'curl -i -XPOST "http://localhost:8086/write?db=TVSHOW" --data-binary "' + data_field + '"'
    os.system(grafana_curl)
time.sleep(1800)
```
<br>
Весь скрипт для Raspberry в файле https://github.com/shrainer/weather_balloon/blob/main/bot.py
<br>
