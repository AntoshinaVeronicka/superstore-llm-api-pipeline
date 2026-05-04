Проект реализует API-пайплайн для анализа датасета **Sample - Superstore** с помощью LLM.

В проекте есть два варианта анализа:

1. `analysis_from_summary.py` — локально считает сводку по датасету и отправляет в LLM только агрегированные данные. Этот вариант экономит токены, позволяет использовать более старую модель и подходит для получения бизнес-рекомендаций на основе уже подготовленных метрик. Минимальная модель для выполнения: `gpt-3.5-turbo`.
2. `analysis_from_full_csv.py` — загружает полный CSV-файл в OpenAI и просит LLM самостоятельно выполнить анализ данных через Code Interpreter. Минимальная модель для выполнения: `gpt-5-nano`.

## Используемый датасет

**Название датасета:** Sample - Superstore
Датасет содержит данные о заказах розничной компании: продажи, прибыль, скидки, клиенты, регионы, категории товаров и даты заказов.

Входной файл находится по пути:
```text
data/Sample - Superstore.csv
```

---

## Вариант 1: анализ по сводке

Скрипт:
```text
scripts/analysis_from_summary.py
```

Что делает:
* читает CSV-файл из папки `data`;
* локально считает основные метрики и агрегаты по датасету;
* формирует компактную JSON-сводку;
* отправляет сводку в LLM через API;
* получает бизнес-инсайты, риски и рекомендации;
* сохраняет результат в `output/result_from_summary.json`.

Этот вариант используется для экономии токенов: модель не получает весь CSV-файл, а работает только с заранее рассчитанной сводкой. Для выполнения можно использовать модель `gpt-3.5-turbo`.

Запуск:
```bash
python scripts/analysis_from_summary.py
```
---

## Вариант 2: анализ полного CSV

Скрипт:
```text
scripts/analysis_from_full_csv.py
```

Что делает:
* загружает полный CSV-файл в OpenAI через Files API;
* передаёт файл LLM-модели через Responses API;
* использует Code Interpreter, чтобы модель могла самостоятельно прочитать и проанализировать CSV;
* получает структурированный JSON-ответ;
* сохраняет результат в `output/result.json`.

Этот вариант даёт модели больше свободы для самостоятельного анализа, но требует больше токенов и ресурсов. Для выполнения нужна модель с поддержкой Code Interpreter, например `gpt-5-nano`.

Запуск:
```bash
python scripts/analysis_from_full_csv.py
```
---

## Структура проекта

```text
superstore-llm-api-pipeline/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── Sample - Superstore.csv
│
├── output/
│   ├── result.json
│   └── result_from_summary.json
│
└── scripts/
    ├── analysis_from_full_csv.py
    └── analysis_from_summary.py
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/AntoshinaVeronicka/superstore-llm-api-pipeline
cd superstore-llm-api-pipeline
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
```

### 3. Активировать виртуальное окружение

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

### 5. Создать файл `.env`

Создайте файл `.env` в корне проекта на основе `.env.example`.

Пример `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-nano
```
