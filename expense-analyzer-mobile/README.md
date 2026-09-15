# Expense Analyzer — мобильное приложение (React Native / Expo)

Тёмный минималистичный интерфейс из двух экранов:
1. **Мои траты** — ввод траты (дата, описание, сумма)
2. **Отчёт** — общая сумма, категории, недели и топ-5 трат

Категоризация выполняется backend на Flask. В неё добавлены словацкие магазины и сервисы, включая сети, часто встречающиеся в Кошице.

## Обычный запуск через Expo Go

### 1. Настрой адрес backend

Открой `src/config.js` и укажи IP компьютера в локальной сети:

```js
export const API_BASE_URL = "http://192.168.1.23:5000";
```

`localhost` и `127.0.0.1` на реальном телефоне использовать нельзя: это адрес самого телефона.

### 2. Установи зависимости

Один раз:

```bash
npm install
```

### 3. Запусти Expo

```bash
npm start
```

Если LAN не подключается, можно использовать:

```bash
npx expo start --tunnel
```

## Сборка настоящего Android APK без Expo Go

Проект настроен для **EAS Build**. Профиль `preview` создаёт устанавливаемый `.apk`.

### 1. Установи EAS CLI (один раз)

```bash
npm install --global eas-cli
```

### 2. Войди в Expo

```bash
eas login
```

### 3. Перейди в папку mobile

```bash
cd expense-analyzer-mobile
```

### 4. Собери APK

```bash
eas build --platform android --profile preview
```

После завершения EAS даст ссылку на готовый APK. Его можно скачать на Android-телефон и установить как обычное приложение.

Для production-профиля с APK:

```bash
eas build --platform android --profile production-apk
```

> EAS по умолчанию использует Android App Bundle (`.aab`) для production. Поэтому для прямой установки на телефон используется профиль `preview` или `production-apk` с `android.buildType: "apk"`.

### Важный момент про backend

Сам APK не запускает Flask-сервер. Для работы аналитики приложение всё равно должно иметь доступ к Flask API.

Для тестирования дома можно оставить адрес вида:

```text
http://192.168.1.23:5000
```

и держать `python api.py` запущенным на компьютере в той же локальной сети.

Для самостоятельной работы приложения без твоего компьютера backend нужно разместить на сервере с публичным HTTPS-адресом и затем указать этот URL в `src/config.js` перед сборкой APK.

## Backend

В `expense-analyzer-api`:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python api.py
```

Проверка:

```text
http://127.0.0.1:5000/api/health
```

Ожидаемый ответ:

```json
{"status": "ok"}
```

## Категоризация для Словакии / Кошице

Распознаются, в частности:

- **Продукты:** Kaufland, Lidl, Billa, Tesco, COOP Jednota, Fresh, Terno, Kraj, Koruna, Milk-Agro
- **Дрогерия/здоровье:** dm, dm drogerie markt, Teta, Dr.Max, BENU, lekáreň
- **Транспорт:** DPMK, Dopravný podnik mesta Košice, MHD, автобус, električka, Bolt, Uber
- **Еда/доставка:** Foodora, Wolt, Bolt Food, Bistro.sk, ресторан, pizza, burger, kebab
- **Топливо:** Slovnaft, OMV, Shell, бензин, nafta, čerpacia stanica
- Дополнительно: подписки, покупки, развлечения, жильё, коммунальные услуги, образование, спорт и путешествия.

Поддерживаются варианты слов с диакритикой и без неё, например `lekáreň` / `lekaren`.
