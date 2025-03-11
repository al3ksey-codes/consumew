import random
import string
import openai
import config


def generate_random_string(length, case_type):
    """
    Generates a random string based on a combined character set.
    Available characters include English letters, Cyrillic letters, digits,
    special characters, and spaces.
    """
    english = string.ascii_letters
    digits = string.digits
    specials = "!@#$%^&*()"
    space = " "
    # A basic set of Cyrillic letters (upper and lower case)
    cyrillic = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" + "абвгдежзийклмнопрстуфхцчшщъыьэюя"

    all_chars = english + digits + specials + space + cyrillic

    result = ''.join(random.choice(all_chars) for _ in range(length))

    if case_type == "uppercase":
        return result.upper()
    elif case_type == "lowercase":
        return result.lower()
    elif case_type == "camel":
        # Alternate uppercase and lowercase characters.
        return ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(result))
    else:
        return result


def generate_data_openai(prompt):
    """
    Uses the OpenAI API to generate text based on the given prompt.
    Make sure you have set your API key in the configuration.
    """
    openai.api_key = config.CONFIG.get("OPENAI_API_KEY", "")
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.7,
        )
        text = response.choices[0].text.strip()
        return text
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Error generating data"
