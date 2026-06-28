# BAS-IP Intercom for Home Assistant
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-18BCF2?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![BAS-IP](https://img.shields.io/badge/BAS--IP-D12023?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAxNS40NSI+PHBhdGggZmlsbD0iIzAwMCIgZD0iTTEuMjUgMTEuOTJMMTAuMTQgMy4wMmMuNC0uNTMuOS0xLjAxIDEuNDItMS40MmwuMzYtLjM2Yy0uMTgtLjE0LS4zOC0uMjQtLjU4LS4zNkwuODkgMTEuMzNjLjEyLjIxLjIzLjQuMzYuNTl6TTQuMDggMTQuNTNsNC43Ni00Ljc0Yy0uMDYtLjI1LS4xMi0uNS0uMTYtLjc3bC01LjE4IDUuMTdjLjE4LjEyLjM4LjI0LjU4LjM0ek05LjYyIDExLjY2IDYuMDMgMTUuMjVjLjI2LjA2LjU0LjEuODEuMTRsMy4xNy0zLjE3Yy0uMTQtLjE4LS4yNi0uMzYtLjM5LS41NnpNLjYxIDEwLjc2TDEwLjc1LjYyYy0uMjMtLjEtLjQ0LS4xOC0uNjgtLjI0TC4zNyAxMC4wN2MuMDcuMjIuMTYuNDYuMjQuNjl6TTEwLjM5IDEyLjc0bC0yLjcyIDIuNzJoLjA2Yy4zIDAgLjYzLS4wMi45My0uMDZsMi4xNy0yLjE3Yy0uMTYtLjE3LS4zLS4zMy0uNDQtLjQ5ek0xMS4zIDEzLjY0bC0xLjU2IDEuNTZjLjUzLS4xNCAxLjA1LS4zNSAxLjUzLS41OGwuNTQtLjU0Yy0uMTgtLjE3LS4zNi0uMy0uNTEtLjQ0ek01LjM1IDE1LjA3bDMuOTctMy45N2MtLjEtLjIyLS4yLS40Mi0uMjgtLjY1bC00LjM4IDQuMzZjLjIzLjEuNDYuMi42OS4yNnpNOC41NiA3LjMxIDIuNDggMTMuMzhjLjE2LjE0LjMyLjMuNS40Mmw1LjU5LTUuNTljMC0uMTYtLjAyLS4zNS0uMDItLjV6TTAgNy43M2w3LjcyLTcuNzNjLS4zNSAwLS42Ny4wMi0xLjAxLjA4TC4wNiA2Ljc0Qy4wMiA3LjA2IDAgNy4zOCAwIDcuNzN6TS4xOCA5LjM2TDkuMzYuMThjLS4yNi0uMDYtLjU0LS4xLS44LS4xMkwuMDQgOC41NWMuMDUuMjguMDguNTQuMTQuODF6TTUuNjIuM2MtLjU0LjE0LTEuMDcuMzctMS41Ny42M0wuOTMgNC4wNWMtLjI3LjUtLjQ5IDEuMDMtLjYzIDEuNTZ6TTkuMDMgNUwxLjYgMTIuNDVjLjE0LjE4LjI4LjM1LjQyLjVsNi42NC02LjY1Yy4wOC0uNDUuMi0uODcuMzctMS4zek0xNi4yNSA1LjM0Yy0xLjMxIDAtMi4zNiAxLjA3LTIuMzggMi4zOCAwIDEuMzEgMS4wNyAyLjM4IDIuMzggMi4zOCAxLjMxIDAgMi4zOC0xLjA3IDIuMzgtMi4zOCAwLTEuMzEtMS4wNy0yLjM4LTIuMzgtMi4zOHptMCA0Yy0uODkgMC0xLjYxLS43Mi0xLjYxLTEuNjEgMC0uODkuNzItMS42MSAxLjYxLTEuNjEuOTEgMCAxLjYxLjcyIDEuNjEgMS42MSAwIC44OS0uNzIgMS42MS0xLjYxIDEuNjF6Ii8+PGNpcmNsZSBjeD0iMTYuNjgiIGN5PSI3LjkiIHI9Ii43OSIgZmlsbD0iIzAwMCIvPjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTE2LjI3IDBjNC4yNiAwIDcuNzMgMy40NSA3LjczIDcuNzMgMCA0LjI3LTMuNDUgNy43Mi03LjczIDcuNzItNC4yNiAwLTcuNzItMy40NS03LjcyLTcuNyAwLTQuMjggMy40NS03Ljc1IDcuNzItNy43NXptMCAzLjE1YzIuNTIgMCA0LjU4IDIuMDMgNC41OCA0LjU4IDAgMi41NC0yLjA2IDQuNTUtNC41OCA0LjU1LTIuNTIuMDItNC41OC0yLjAzLTQuNTgtNC41NSAwLTIuNTIgMi4wNC00LjU4IDQuNTgtNC41OHoiLz48L3N2Zz4=&logoColor=white)](https://bas-ip.ru/)


Интеграция для управления IP-домофоном BAS-IP через Home Assistant.

---

## 📥 Установка

### Через HACS

1. Откройте **HACS** → три точки → **Custom repositories**
2. Добавьте репозиторий: `https://github.com/NagibinA/BAS-IP_AV-03BD`
3. Выберите категорию: **Integration**
4. Нажмите **Add**
5. Найдите **BAS-IP Intercom** → **Install**
6. Перезапустите Home Assistant

### Ручная установка

1. Скачайте последний релиз из [Releases](https://github.com/NagibinA/BAS-IP_AV-03BD/releases)
2. Распакуйте архив и скопируйте папку `basip` в `/config/custom_components/`
3. Перезапустите Home Assistant

---

## ⚙️ Настройка

1. Перейдите в **Настройки** → **Устройства и сервисы**
2. Нажмите **+ Добавить интеграцию**
3. Найдите **BAS-IP Intercom**
4. Введите параметры:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| IP-адрес | IP-адрес панели BAS-IP | 192.168.190 |
| Пароль | Пароль от панели | 123456 |
| Порт | HTTP-порт | 80 |
| RTSP пароль | Пароль для RTSP-потока | - |

---

## 🎯 Возможности

- 🔓 Открытие замка
- 🚨 Аварийное открытие и закрытие
- 📷 RTSP поток (задержка ~2-3 сек)
- 📸 Снимок с камеры
- 📊 27 датчиков состояния
- 🔄 Перезагрузка панели

---

## 🎯 Запланировано

- 🌍 Смена языка интерфейса
- 🌐 Настройка сети (статический IP / DHCP)
- 📞 Исходящие SIP-звонки

---

## 📊 Датчики

| Датчик | Описание |
|--------|----------|
| Device Info | Модель, прошивка, серийный номер |
| Network Settings | IP, маска, шлюз, DNS |
| MAC Address | MAC-адрес |
| NTP Server | NTP-сервер |
| DST Settings | Перевод времени |
| Timezone | Часовой пояс |
| Management Server | Настройки Link |
| SIP Status | Статус SIP |
| SIP Settings | Настройки SIP |
| Device Time | Время устройства |
| Language | Текущий язык |
| Video Resolution | Разрешение камеры |
| RTSP Settings | Настройки RTSP |
| Volume | Громкость |
| Relay Settings | Настройки реле |
| Mode | Режим работы |
| Lock Type | Тип замка |
| Master Card | Мастер-карта |
| Access Code | Код доступа |


---


## 📋 Поддерживаемые устройства

- BAS-IP AV-03BD
- Другие модели на API v1

---


## 📄 Лицензия

MIT License


**Автор:** [NagibinA](https://github.com/NagibinA)
