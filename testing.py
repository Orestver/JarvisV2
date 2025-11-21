import re, datetime


def words_to_number(text) -> int | None:
    num_words = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }

    multipliers = {
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000
    }
    text = text.lower().replace("-", " ")
    words = text.split()

    total = 0
    current = 0
    
    for w in words:
        if w in num_words:
            current += num_words[w]
        elif w in multipliers:
            if current == 0:
                current = 1
            current *= multipliers[w]
            total += current
            current = 0
        else:
            return None  # невідоме слово
    return total + current

def extract_time(text):
    num_words = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }

    multipliers = {
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000
    }
    text = text.lower()

    # 1. if already in numbers 12.30 or 12:30
    match = re.search(r"(\d{1,2})[.:](\d{1,2})", text)
    if match:
        hh, mm = match.groups()
        return f"{int(hh):02d}:{int(mm):02d}"

    # if in words
    words = text.split()

    number_words = []
    for w in words:
        if w in num_words or w in multipliers:
            number_words.append(w)

    if not number_words:
        return None

    #if only houres
    if len(number_words) == 1:
        hh = words_to_number(number_words[0])
        return f"{hh:02d}:00"

    if len(number_words) >= 2:
        hh = words_to_number(number_words[0])
        mm = words_to_number(" ".join(number_words[1:]))
        return f"{hh:02d}:{mm:02d}"

    return None


def str_to_time(time_str: str) -> datetime.time:
    hour, minute = map(int, time_str.split(":"))
    return datetime.time(hour, minute)

print(extract_time("set the timer to twelve oclock"))