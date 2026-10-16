import string
from collections import Counter, defaultdict

ALPHABET = string.ascii_uppercase
N = 26

ENGLISH = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702,
    0.02228, 0.02015, 0.06094, 0.06966, 0.00153,
    0.00772, 0.04025, 0.02406, 0.06749, 0.07507,
    0.01929, 0.00095, 0.05987, 0.06327, 0.09056,
    0.02758, 0.00978, 0.02360, 0.00150, 0.01974,
    0.00074
]

PERIOD = None

def read_ciphertext(filename):
    with open(filename,"r",encoding="utf-8") as file:
        text = file.read().upper()

    text = "".join(ch for ch in text if ch in ALPHABET)

    if not text:
        raise ValueError("No alphabet ciphertext found")

    return text

def index_of_coincidence(text):
    n = len(text)

    if n < 2:
        return 0.0

    counts = Counter(text)

    numerator = sum(
        count * (count - 1)
        for count in counts.values()
    )

    return numerator / (n * (n - 1))


def kasiski_examination(text, min_length=3, max_length=3):
    factor_counts = Counter()
    repeated_patterns = []

    for size in range(min_length, max_length + 1):
        positions = defaultdict(list)

    for i in range(len(text) - size + 1):
        gram = text[i:i + size]
        positions[gram].append(i)

    for gram, places in positions.items():
        if len(places) < 2: 
            continue

        distances = []

        for i in range(len(places)):
            for j in range(i + 1, len(places)):
                distance = places[j] - places[i]
                distances.append(distance)

                for factor in range(2, 16):
                    if distance % factor == 0:
                        factor_counts[factor] += 1

        repeated_patterns.append((gram, places, distances))
    
    print("\n=== KASISKI EXAMINATION ===")

    if not repeated_patterns:
        print("No repeated polygrams found.")
    else:
        for gram, places, distances in repeated_patterns[:20]:
            print(
                f"{gram}: positions={places}, "
                f"distances={distances}"
            )

        if len(repeated_patterns) > 20:
            print("Only the first 20 repeated patterns are shown.")

    print("\nCommon distance factors:")
    for factor, count in factor_counts.most_common():
        print(f"Factor {factor}: {count} occurrence(s)")

    return factor_counts


def average_ic_for_period(text, period):
    cosets = [text[j::period] for j in range(period)]

    values = [index_of_coincidence(coset) for coset in cosets]

    return sum(values) / len(values), values


def analyze_periods(text, max_period=15):
    results = {}

    print("\n=== AVERAGE INDEX OF COINCIDENCE ===")
    print(f"{'Period':<10}{'Average IC':<15}{'Interpretation'}")

    for period in range(1, max_period + 1):
        avg_ic, _ = average_ic_for_period(text, period)
        results[period] = avg_ic

        if avg_ic >= 0.060:
            note = "English-like"
        elif avg_ic >= 0.050:
            note = "Possible candidate"
        else:
            note = "Less English-like"

        print(f"{period:<10}{avg_ic:<15.5f}{note}")

    return results

def recover_shift(coset):
    counts = Counter(ord(ch) - ord("A") for ch in coset)
    n = len(coset)

    scores = []

    for shift in range(26):
        score = sum(
            counts[c] * ENGLISH[(c - shift) % 26]
            for c in range(26)
        ) / n

        scores.append((shift, score))

    best_shift, best_score = max(scores, key=lambda item: item[1])

    return best_shift, best_score, scores


def recover_key(text, period):
    key_shifts = []
    print("\n=== SHIFT CORRELATION BY KEY POSITION ===")

    for j in range(period):
        coset = text[j::period]

        shift, score, scores = recover_shift(coset)
        key_shifts.append(shift)

        print(f"\nKey position {j + 1}, coset length {len(coset)}")
        print(f"Selected shift: {shift} ({ALPHABET[shift]})")
        print(f"Maximum correlation: {score:.5f}")

        print("Top 5 candidate shifts:")
        for candidate, value in sorted(
            scores, key=lambda item: item[1], reverse=True
        )[:5]:
            print(f"  {candidate:2d} ({ALPHABET[candidate]}): {value:.5f}")

    keyword = "".join(ALPHABET[k] for k in key_shifts)

    return keyword, key_shifts


def decrypt_vigenere(text, key_shifts):
    plaintext = []

    for i, ch in enumerate(text):
        c = ord(ch) - ord("A")
        k = key_shifts[i % len(key_shifts)]
        p = (c - k) % 26
        plaintext.append(ALPHABET[p])

    return "".join(plaintext)


def main():
    filename = "ciphertxt.txt"
    ciphertext = read_ciphertext(filename)

    print("=== VIGENERE CRYPTANALYSIS ===")
    print(f"Ciphertext length: {len(ciphertext)} letters")

    # (a) Repeated polygrams and distance factors
    factor_counts = kasiski_examination(ciphertext)

    # (b) Average IC for periods 1 through 15
    ic_results = analyze_periods(ciphertext)

    # Select a period automatically or set PERIOD manually.
    if PERIOD is None:
        selected_period = max(ic_results, key=ic_results.get)
        print(
            "\nAutomatic IC choice:",
            selected_period,
            "(verify against Kasiski factors and the IC table)"
        )
    else:
        selected_period = PERIOD
        print("\nUsing manually selected period:", selected_period)

    # (c) Recover key shifts using cross-correlation
    keyword, key_shifts = recover_key(
        ciphertext, selected_period
    )

    # (d) Decrypt the full ciphertext
    plaintext = decrypt_vigenere(ciphertext, key_shifts)

    print("\n=== FINAL RESULTS ===")
    print("Candidate key length:", selected_period)
    print("Recovered keyword:", keyword)
    print("Decrypted plaintext:")
    print(plaintext)


if __name__ == "__main__":
    main()