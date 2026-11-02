import math
from collections import Counter

from huffman import build_tree, build_codes, metrics, encode, decode

RAW_TEXT = (
    "Информация в цифровых системах передаётся и хранится в виде последовательностей символов. "
    "Чем реже встречается символ, тем больше информации он несёт, и тем длиннее может быть его код. "
    "Метод Хаффмана строит префиксный код, в котором частые буквы получают короткие кодовые слова, "
    "а редкие — длинные. Средняя длина такого кода не может быть меньше энтропии источника, "
    "но отличается от неё менее чем на один бит на символ. "
    "Для обычного русского текста энтропия на символ заметно ниже, чем у равномерного кода, "
    "поэтому сжатие по Хаффману позволяет уменьшить объём данных."
)

KEEP_SPACES = True
KEEP_PUNCTUATION = False
LOWERCASE = True


def prepare(text):
    if LOWERCASE:
        text = text.lower()
    result = []
    for ch in text:
        if ch.isalpha():
            result.append(ch)
        elif ch == " " and KEEP_SPACES:
            result.append(ch)
        elif KEEP_PUNCTUATION and not ch.isalnum():
            result.append(ch)
    return "".join(result)


def pack_bits(bits):
    padded = bits + "0" * (-len(bits) % 8)
    return bytes(int(padded[i:i + 8], 2) for i in range(0, len(padded), 8))


def show(ch):
    return "␣" if ch == " " else ch


def main():
    text = prepare(RAW_TEXT)
    print("Параметры: пробелы — учитываются, регистр — приведён к нижнему, знаки препинания — удалены")
    print(f"Длина текста: {len(text)} символов\n")

    freqs = dict(Counter(text))
    tree = build_tree(freqs)
    codes = build_codes(tree)
    l_avg, h, eta = metrics(freqs, codes)
    total = len(text)

    print("10.1. Таблица частот и кодов")
    print(f"{'Симв.':<7}{'n':<6}{'p':<9}{'Код':<14}{'l'}")
    for s in sorted(codes, key=lambda x: (-freqs[x], x)):
        print(f"{show(s):<7}{freqs[s]:<6}{freqs[s] / total:<9.4f}{codes[s]:<14}{len(codes[s])}")
    print(f"Уникальных символов: {len(freqs)}\n")

    print("10.2. Показатели")
    print(f"H(X)     = {h:.4f} бит/символ")
    print(f"L̄        = {l_avg:.4f} бит/символ")
    print(f"η = H/L̄  = {eta:.4f} ({eta * 100:.2f} %)")
    print(f"R = L̄-H  = {l_avg - h:.4f} бит/символ")
    print(f"R = 1-η  = {1 - eta:.4f} ({(1 - eta) * 100:.2f} %)")
    print(f"log2(N)  = {math.log2(len(freqs)):.4f} бит/символ (равномерный код)\n")

    bits = encode(text, codes)
    assert decode(bits, tree) == text
    packed = pack_bits(bits)
    utf8_size = len(text.encode("utf-8"))
    fixed_bits = math.ceil(math.log2(len(freqs))) * total

    print("10.3. Сравнение объёма")
    print(f"UTF-8:                     {utf8_size} байт ({utf8_size * 8} бит)")
    print(f"Равномерный код ({math.ceil(math.log2(len(freqs)))} бит):  {math.ceil(fixed_bits / 8)} байт ({fixed_bits} бит)")
    print(f"Поток Хаффмана:            {len(bits)} бит")
    print(f"Упакованный в байты:       {len(packed)} байт (добавлено {len(packed) * 8 - len(bits)} бит заполнения)")
    print(f"Степень сжатия (UTF-8 / Хаффман): {utf8_size / len(packed):.3f}")
    print(f"Экономия: {(1 - len(packed) / utf8_size) * 100:.2f} %")
    print("Проверка decode(encode(text)) == text: True")


if __name__ == "__main__":
    main()
