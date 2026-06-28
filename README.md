# BAS-IP Intercom for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/github/v/release/NagibinA/BAS-IP_AV-03BD)](https://github.com/NagibinA/BAS-IP_AV-03BD/releases)
[![license](https://img.shields.io/github/license/NagibinA/BAS-IP_AV-03BD)](https://github.com/NagibinA/BAS-IP_AV-03BD/blob/main/LICENSE)

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
| IP-адрес | IP-адрес панели BAS-IP | — |
| Пароль | Пароль от панели | 123456 |
| Порт | HTTP-порт | 80 |
| RTSP пароль | Пароль для RTSP-потока | 1234 |

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

## 🛠️ Сервисы

| Сервис | Описание | Параметры |
|--------|----------|-----------|
| basip.open_lock | Открыть дверь | — |
| basip.emergency_open | Аварийное открытие | lock_number, unlock_time |
| basip.emergency_close | Закрыть аварийный режим | lock_number |
| basip.reboot | Перезагрузить панель | — |
| basip.take_photo | Сделать снимок | — |
| basip.call_start | Начать звонок | number |
| basip.call_end | Завершить звонок | — |
| basip.set_language | Установить язык | language |
| basip.set_static_ip | Установить статический IP | ip_address, mask, gateway, dns |
| basip.enable_dhcp | Включить DHCP | — |

**Поддерживаемые языки:** English, Russian, Ukrainian, Spanish, Turkish, Deutsch, Italian, French

---

## 📝 Примеры автоматизаций

### Открыть дверь по NFC

```yaml
automation:
  alias: Открыть дверь по NFC
  trigger:
    platform: tag
    tag_id: 123456789
  action:
    service: basip.open_lock
```

### Сделать снимок при движении

```yaml
automation:
  alias: Снимок при движении
  trigger:
    platform: state
    entity_id: binary_sensor.motion_sensor
    to: on
  action:
    service: basip.take_photo
```

### Аварийное открытие на 5 секунд

```yaml
automation:
  alias: Аварийное открытие
  action:
    service: basip.emergency_open
    data:
      lock_number: 1
      unlock_time: 5000
```

### Сменить язык на русский

```yaml
automation:
  alias: Сменить язык
  action:
    service: basip.set_language
    data:
      language: Russian
```

### Установить статический IP

```yaml
automation:
  alias: Установить статический IP
  action:
    service: basip.set_static_ip
    data:
      ip_address: 192.168.1.100
      mask: 255.255.255.0
      gateway: 192.168.1.1
      dns: 8.8.8.8
```

### Перезагрузить панель

```yaml
automation:
  alias: Перезагрузить панель
  action:
    service: basip.reboot
```

---

## 📋 Поддерживаемые устройства

- BAS-IP AV-03BD
- BAS-IP AV-04BD
- Другие модели на API v1

---

## ❓ Устранение неполадок

### Камера не показывает видео

1. Проверьте RTSP пароль в настройках интеграции
2. В карточке камеры включите режим `camera_view: live`
3. Проверьте RTSP в VLC: `rtsp://user:1234@IP:8554/ch01`

### Не удается подключиться

1. Проверьте IP-адрес и пароль
2. Убедитесь, что панель доступна в сети
3. Проверьте логи Home Assistant

### Сенсоры не обновляются

- Интеграция обновляет данные каждые 60 секунд
- Проверьте соединение с панелью

---

## 📄 Лицензия

MIT License

---

## 🤝 Вклад в проект

1. Создайте [Issue](https://github.com/NagibinA/BAS-IP_AV-03BD/issues)
2. Сделайте [Pull Request](https://github.com/NagibinA/BAS-IP_AV-03BD/pulls)

---

**Автор:** [NagibinA](https://github.com/NagibinA)
