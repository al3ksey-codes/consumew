import random
import string
import openai
import config


def generate_random_string(length, case_type):
# Гласные с весами для частотности
    vowels_list = ['а'] * 10 + ['е'] * 10 + ['о'] * 10 + ['и'] * 5 + ['у'] * 5 + ['ы'] * 5 + ['э'] * 2 + ['ю'] * 2 + [
        'я'] * 2 + ['ё'] * 1

    # Согласные
    consonants_list = list('бвгджзклмнпрстфхцчшщ')

    # Приставки, суффиксы, окончания
    prefixes = ['по', 'на', 'с', 'за', 'пере', 'при', 'у', 'под', 'над']
    suffixes = ['ник', 'ость', 'тель', 'ец', 'ок', 'ик']
    endings = ['а', 'о', 'е', 'ь', 'й', 'я', '']

    # Множества для проверки
    vowels = set(vowels_list)
    consonants = set(consonants_list)
    soft_sign = 'ь'

    # Генерация слога
    def generate_syllable():
        if random.random() < 0.1:  # 10% — только гласная
            return random.choice(vowels_list)
        elif random.random() < 0.6:  # 60% — согласная + гласная
            return random.choice(consonants_list) + random.choice(vowels_list)
        else:  # 30% — согласная + гласная + согласная
            return random.choice(consonants_list) + random.choice(vowels_list) + random.choice(consonants_list)

    # Генерация слова
    def generate_word():
        word = ''

        # Приставка (20% шанс)
        if random.random() < 0.2:
            word += random.choice(prefixes)

        # Корень: 2-3 слога
        num_syllables = random.randint(2, 3)
        for _ in range(num_syllables):
            word += generate_syllable()

        # Суффикс (30% шанс)
        if random.random() < 0.3:
            word += random.choice(suffixes)

        # Окончание с учётом последнего символа
        if word[-1] == soft_sign:
            pass  # Не добавляем окончание после мягкого знака
        elif word[-1] in consonants:
            # После согласной — любое окончание, кроме "й"
            possible_endings = [e for e in endings if e != 'й']
            word += random.choice(possible_endings)
        elif word[-1] in vowels:
            # После гласной — любое окончание, кроме "ь"
            possible_endings = [e for e in endings if e != 'ь']
            word += random.choice(possible_endings)

        # Преобразуем в заглавные буквы
        word = word.upper()

        return word
    return generate_word()


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
