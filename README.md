# SamGeo-WebUI

## Описание

**SamGeo-WebUI** — это простой веб-интерфейс для сегментации геопространственных данных с помощью нейросетевой модели. Проект позволяет загружать TIFF изображения или работать с картой, обрабатывать изображения на сервере, просматривать и экспортировать результаты через сайт. Интерфейс построен на базе Vue.js, а серверная часть реализована на Python. Решение позволяет быстро сегментировать снимки дистанционного зондирования в пару кликов.

## Содержание

- [Установка](#установка)
- [Запуск](#запуск)

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Reape4er/SamGeo-WebUI.git
   cd SamGeo-WebUI
   ```

2. Установите зависимости для backend (Python):
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   pip install -r requirements.txt
   ```

3. Установите зависимости для frontend (Vue.js):
   ```bash
   cd frontend
   npm install
   ```

## Запуск

1. Запустите backend:
   ```bash
   python app.py
   ```
   или используйте:
   ```bash
   uvicorn app:app --reload
   ```

2. Запустите frontend:
   ```bash
   cd frontend
   npm run serve
   ```

3. Откройте браузер и перейдите по адресу, указанному в консоли frontend.
