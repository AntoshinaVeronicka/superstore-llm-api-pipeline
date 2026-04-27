import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

INPUT_FILE = "data/Sample - Superstore.csv"
OUTPUT_FILE = "output/result.json"


def main():
    load_dotenv()

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    print("1. Загружаем CSV-файл в OpenAI...")
    uploaded_file = client.files.create(
        file=open(INPUT_FILE, "rb"),
        purpose="user_data"
    )

    print("2. Отправляем файл в LLM")
    response = client.responses.create(
        model=model,
        tools=[
            {
                "type": "code_interpreter",
                "container": {
                    "type": "auto",
                    "file_ids": [uploaded_file.id]
                }
            }
        ],
        instructions="""
            Ты аналитик данных. Тебе передан CSV-файл Sample - Superstore.

            Важно:
            - Самостоятельно прочитай CSV-файл с помощью Python.
            - Анализируй весь файл.
            - Верни только валидный JSON.
            - Не добавляй Markdown.
            - Не добавляй пояснения до или после JSON.
            - Ответ должен быть на русском языке.
            """,
        input="""
            Проанализируй CSV-файл Sample - Superstore.

            Верни JSON со следующей структурой:
            {
            "dataset_summary": {
                "rows": число,
                "columns": число,
                "period_start": "YYYY-MM-DD",
                "period_end": "YYYY-MM-DD",
                "total_sales": число,
                "total_profit": число,
                "unique_orders": число,
                "unique_customers": число
            },
            "key_insights": [
                "инсайт 1",
                "инсайт 2",
                "инсайт 3",
                "инсайт 4",
                "инсайт 5"
            ],
            "main_risks": [
                "риск 1",
                "риск 2",
                "риск 3"
            ],
            "business_recommendations": [
                "рекомендация 1",
                "рекомендация 2",
                "рекомендация 3",
                "рекомендация 4",
                "рекомендация 5"
            ],
            "limitations": [
                "ограничение 1",
                "ограничение 2"
            ]
            }

            Обязательно посчитай показатели на основе CSV-файла, а не придумывай их.
            """
        )

    print("3. Парсим JSON-ответ модели...")
    result = json.loads(response.output_text)

    print("4. Сохраняем результат...")
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"Результат сохранён в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()