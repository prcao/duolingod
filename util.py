import unicodedata
from dragonmapper.transcriptions import accented_to_numbered
import re
import random
from pypinyin import pinyin

def remove_accents(old):
    """
    Removes common accent characters, lower form.
    Uses: regex.
    """
    new = old.lower()
    new = re.sub(r'[àáāǎ]', 'a', new)
    new = re.sub(r'[èéēě]', 'e', new)
    new = re.sub(r'[ìíīǐ]', 'i', new)
    new = re.sub(r'[òóǒō]', 'o', new)
    new = re.sub(r'[ùúǔüūǖǘǚǜ]', 'u', new)
    return new

def pinyin_equals(a, b):
    a = accented_to_numbered(a)
    b = accented_to_numbered(b)
    return a == b

def pinyin_index(list, py):
    for i in range(len(list)):
        if pinyin_equals(list[i], py):
            return i

    # couldn't find a match, just gonna have to go with a good guess
    
    list = [remove_accents(x) for x in list]
    py = remove_accents(py)
    indices = [i for i, x in enumerate(list) if x == py]

    if indices:
        r = random.choice(indices)
        print("Can't find a tonal match, removing accent marks", r)
        return r

    print("can't find a match at all, randomly choosing")
    return random.randint(0, len(list) - 1)

def get_pinyin(chinese_text):
    pinyins = pinyin(chinese_text)
    result = ''
    for py in pinyins:
        result += random.choice(py)

    return result