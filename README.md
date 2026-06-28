# BAS-IP Intercom for Home Assistant



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
