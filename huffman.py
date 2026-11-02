import heapq
import math
from collections import Counter
from itertools import count


class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.symbol is not None


def build_tree(freqs):
    if not freqs:
        raise ValueError("Словарь частот пуст")
    tie = count()
    heap = [(f, next(tie), Node(f, symbol=s)) for s, f in sorted(freqs.items())]
    heapq.heapify(heap)

    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = Node(f1 + f2, left=n1, right=n2)
        heapq.heappush(heap, (parent.freq, next(tie), parent))

    return heap[0][2]


def build_codes(tree):
    if tree.is_leaf():
        return {tree.symbol: "0"}

    codes = {}
    stack = [(tree, "")]
    while stack:
        node, prefix = stack.pop()
        if node.is_leaf():
            codes[node.symbol] = prefix
        else:
            stack.append((node.right, prefix + "1"))
            stack.append((node.left, prefix + "0"))
    return codes


def metrics(freqs, codes):
    total = sum(freqs.values())
    probs = {s: f / total for s, f in freqs.items()}
    l_avg = sum(probs[s] * len(codes[s]) for s in freqs)
    h = -sum(p * math.log2(p) for p in probs.values() if p > 0) + 0.0
    eta = h / l_avg if l_avg > 0 else 0.0
    return l_avg, h, eta


def encode(text, codes):
    return "".join(codes[ch] for ch in text)


def decode(bits, tree):
    if tree.is_leaf():
        return tree.symbol * len(bits)

    result = []
    node = tree
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            result.append(node.symbol)
            node = tree
    return "".join(result)


def run(text):
    freqs = dict(Counter(text))
    tree = build_tree(freqs)
    codes = build_codes(tree)
    l_avg, h, eta = metrics(freqs, codes)
    bits = encode(text, codes)
    decoded = decode(bits, tree)

    print(f"Сообщение: {text}")
    print(f"Частоты:   {freqs}")
    print(f"\n{'Символ':<8}{'p':<10}{'Код':<8}{'l'}")
    total = sum(freqs.values())
    for s in sorted(codes, key=lambda x: (len(codes[x]), x)):
        print(f"{s:<8}{freqs[s] / total:<10.4f}{codes[s]:<8}{len(codes[s])}")
    print(f"\nL̄ = {l_avg:.4f} бит/символ")
    print(f"H(X) = {h:.4f} бит/символ")
    print(f"η = H/L̄ = {eta:.4f}")
    print(f"\nЗакодировано: {bits} ({len(bits)} бит)")
    print(f"Декодировано: {decoded}")
    print(f"decode(encode(text)) == text: {decoded == text}\n")
    assert decoded == text


if __name__ == "__main__":
    run("ABCADE")
    print("--- Один уникальный символ ---")
    run("AAAA")
