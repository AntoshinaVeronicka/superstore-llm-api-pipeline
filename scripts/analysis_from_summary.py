import os
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


INPUT_FILE = "data/Sample - Superstore.csv"
OUTPUT_FILE = "output/result_from_summary.json"
CSV_ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin1")


def read_csv_with_fallback(path):

    last_error = None

    for encoding in CSV_ENCODINGS:
        try:
            df = pd.read_csv(path, encoding=encoding)
            print(f"   CSV прочитан с кодировкой {encoding}")
            return df
        except UnicodeDecodeError as error:
            last_error = error

    raise UnicodeDecodeError(
        last_error.encoding,
        last_error.object,
        last_error.start,
        last_error.end,
        f"Не удалось прочитать CSV в кодировках: {', '.join(CSV_ENCODINGS)}"
    )


def make_summary(df):

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    numeric_cols = ["Sales", "Profit", "Quantity", "Discount"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Order Date", "Sales", "Profit", "Quantity", "Discount"])

    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),

        "period": {
            "start": str(df["Order Date"].min().date()),
            "end": str(df["Order Date"].max().date())
        },

        "main_metrics": {
            "total_sales": round(float(df["Sales"].sum()), 2),
            "total_profit": round(float(df["Profit"].sum()), 2),
            "total_quantity": int(df["Quantity"].sum()),
            "unique_orders": int(df["Order ID"].nunique()),
            "unique_customers": int(df["Customer ID"].nunique())
        },

        "data_quality": {
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "negative_profit_rows": int((df["Profit"] < 0).sum()),
            "high_discount_rows_70_plus": int((df["Discount"] >= 0.7).sum())
        },

        "sales_profit_by_category": (
            df.groupby("Category")[["Sales", "Profit"]]
            .sum()
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        ),

        "sales_profit_by_region": (
            df.groupby("Region")[["Sales", "Profit"]]
            .sum()
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        ),

        "sales_profit_by_segment": (
            df.groupby("Segment")[["Sales", "Profit"]]
            .sum()
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        ),

        "worst_subcategories_by_profit": (
            df.groupby("Sub-Category")[["Sales", "Profit"]]
            .sum()
            .round(2)
            .sort_values("Profit")
            .head(5)
            .reset_index()
            .to_dict(orient="records")
        ),

        "top_loss_rows": (
            df.sort_values("Profit")
            .head(5)[
                [
                    "Order ID",
                    "Order Date",
                    "Region",
                    "Category",
                    "Sub-Category",
                    "Sales",
                    "Quantity",
                    "Discount",
                    "Profit"
                ]
            ]
            .assign(**{
                "Order Date": lambda x: x["Order Date"].dt.strftime("%Y-%m-%d")
            })
            .to_dict(orient="records")
        )
    }

    return summary


def ask_llm(summary):

    client = OpenAI()

    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    prompt = f"""
        Ты аналитик данных. Проанализируй сводку по датасету Sample Superstore.
        Верни ответ СТРОГО в формате JSON без Markdown.
        JSON должен иметь такую структуру:
        {{
        "dataset_summary": "...",
        "key_insights": ["...", "...", "..."],
        "main_risks": ["...", "...", "..."],
        "business_recommendations": ["...", "...", "...", "...", "..."],
        "limitations": ["...", "..."]
        }}
        Используй только данные из сводки. Не выдумывай числа.
        Сводка данных:
        {json.dumps(summary, ensure_ascii=False, indent=2)}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Ты возвращаешь только валидный JSON на русском языке."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    text = response.choices[0].message.content
    return json.loads(text)


def save_json(data, path):

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    load_dotenv()

    print("1. Читаю CSV-файл...")
    df = read_csv_with_fallback(INPUT_FILE)

    print("2. Считаю сводку по данным...")
    summary = make_summary(df)

    print("3. Отправляю сводку в LLM через API...")
    result = ask_llm(summary)

    print("4. Сохраняю результат в JSON...")
    save_json(result, OUTPUT_FILE)

    print(f"Готово! Результат сохранён в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
