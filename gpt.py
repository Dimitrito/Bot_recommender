import json
import requests
import re
from config import OPENAI_API_KEY


def request_analysis(text):
    instruction = (
        "You are acting as an analyzer of user input for a smartphone e-commerce platform. "
        "Your task is to infer appropriate smartphone specifications based on the user's description. "
        "Fill in the following fields with a value or null if they were not mentioned in the request:\n"
        "brand_name, model, price, avg_rating, is_5g,\n"
        "processor_brand, num_cores, processor_speed,\n"
        "battery_capacity, fast_charging_available, fast_charging,\n"
        "ram_capacity, internal_memory,\n"
        "screen_size, refresh_rate, num_rear_cameras,\n"
        "os, primary_camera_rear, primary_camera_front,\n"
        "extended_memory_available, resolution_height, resolution_width.\n\n"
        f"User description:\n{text}\n\n"
        "Do not include any units in the values. "
        "Return only a valid JSON object with updated fields — no explanations, no extra text."
    )

    result = send_to_gpt(instruction)
    significant = {k: v for k, v in json.loads(result).items() if v is not None}
    return clean(significant)


def get_short_description(text, product):
    instruction = (
        "Надайте дуже стислий опис рекомендованого продукту, зосередившись на тому, що було важливим для користувача. "
        f"Запит користувача:\n{text}\n\n"
        f"Смартфон який треба зарекомендувати:\n{product}\n\n"
        "Завжди починай пояснення зі слів: \"За вашим запитом можу порекомендувати\". "
    )

    result = send_to_gpt(instruction)
    return result


def get_long_description(text, product):
    instruction = (
        "Надайте повний опис рекомендованого продукту, зосередившись на тому, що було важливим для користувача."
        f"Запит користувача:\n{text}\n\n"
        f"Смартфон який треба зарекомендувати:\n{product}\n\n"
        "Завжди починай пояснення зі слів: \"Більш детальна інформація про смарфтон:\n\". "
    )

    result = send_to_gpt(instruction)
    return result


def is_correct_request(text):
    instruction = (
        "Поверни лише число 1 або 0 і нічого більше. "
        "Повертай 1 - якщо запит відноситься до пошуку смарфону. "
        "Повертай 0 - у всіх інших випадках"
        "Наприклад: Мені потрібен смартфон с гарною камерою - це 1"
        "За умовчанням у тексті йдеться про смартфон"
        f"Запит користувача:\n{text}\n\n"
    )

    result = send_to_gpt(instruction)

    match = re.search(r'\b[01]\b', result)
    if match:
        return int(match.group())
    else:
        return 0


def send_to_gpt(instruction):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": instruction}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Помилка у відповіді: ", e)
        return None


def clean(data: dict) -> dict:
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, str):
            cleaned_str = re.sub(r'[^0-9.]', '', v)
            if cleaned_str == '':
                continue
            if '.' in cleaned_str:
                cleaned[k] = float(cleaned_str)
            else:
                cleaned[k] = int(cleaned_str)
        else:
            cleaned[k] = v
    return cleaned

