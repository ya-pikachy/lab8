# Лабораторная работа №8 — Картографические API

Индивидуальное задание **вариант 2**: маршрут между центрами двух геохешей.  
Город: **Омск** (аэропорт → центр города).

## Запуск локально

```bash
pip install -r requirements.txt
streamlit run app.py
```

```bash
python demo.py    # демонстрация 5 API
python main.py    # вариант 2 в консоли
```

## GitHub Pages

Приложение доступно по адресу:  
**https://ya-pikachy.github.io/lab8/**

> На GitHub Pages приложение работает через [stlite](https://github.com/whitphx/stlite) в браузере.  
> Запросы к внешним API (2ГИС, OSRM) могут быть ограничены CORS — для полной функциональности используйте локальный запуск.

## Стек

Streamlit · Folium · 2ГИС API · OSRM · pygeohash
