# Vigenere Cipher Cryptanalysis

This project attempts to break a ciphertext encrypted with the Vigenere
cipher. It estimates the key length, recovers one Caesar shift for each key
position, and uses those shifts to produce candidate plaintext.

The program works with uppercase English letters. Spaces, punctuation, and
numbers are removed from the input before analysis.

## Files

- [`vigenere_cryptanalysis.py`](./vigenere_cryptanalysis.py) contains the
  cryptanalysis and decryption functions.
- [`ciphertxt.txt`](./ciphertxt.txt) contains the ciphertext to analyze.

## How to run

Open a terminal in this directory and run:

```text
python vigenere_cryptanalysis.py
```

The script reads `ciphertxt.txt` from the current directory and prints all
results to the terminal. No output file is created.

## What the program does

### 1. Read and clean the ciphertext

`read_ciphertext(filename)` opens the selected file, converts its contents to
uppercase, and keeps only characters from `A` through `Z`. It raises an error
if the file contains no alphabetic ciphertext.

### 2. Calculate the Index of Coincidence

`index_of_coincidence(text)` measures how often two randomly selected letters
from a string are the same:

```text
IC = sum(f_i * (f_i - 1)) / (n * (n - 1))
```

Here, `f_i` is the frequency of a letter and `n` is the length of the text.
English-like text generally has a higher IC than uniformly random text.

`average_ic_for_period(text, period)` splits the ciphertext into `period`
cosets. For example, with a period of 3, it creates the letters at positions
`0, 3, 6, ...`, `1, 4, 7, ...`, and `2, 5, 8, ...`. It calculates the IC of
each coset and returns their average.

`analyze_periods(text, max_period=15)` tests key lengths from 1 through 15,
prints each average IC, and labels the result as English-like, a possible
candidate, or less English-like. Unless changed in the source, the period
with the highest average IC is selected automatically.

### 3. Perform Kasiski examination

`kasiski_examination(text, min_length=3, max_length=3)` searches for repeated
three-letter groups (polygrams). For every repeated group, it records:

- the positions where the group occurs;
- the distances between those positions; and
- factors from 2 through 15 that divide those distances.

If the same factors occur frequently, they may indicate possible key lengths.
The function prints up to the first 20 repeated groups and returns the factor
counts. These factors are printed as evidence for checking the automatically
selected period; they do not directly select the period in the current
program.

### 4. Recover the key shifts

`recover_shift(coset)` tests all 26 possible Caesar shifts for one coset. Each
shift is scored by comparing the shifted letter frequencies with the
approximate frequencies of letters in English. The shift with the highest
score is selected.

`recover_key(text, period)` applies `recover_shift` to every key position. It
prints the five highest-scoring shift candidates for each position, then
returns:

- `keyword`: the selected shifts represented as letters (`A` = shift 0,
  `B` = shift 1, and so on);
- `key_shifts`: the numeric shifts used during decryption.

### 5. Decrypt the ciphertext

`decrypt_vigenere(text, key_shifts)` decrypts each ciphertext letter using the
corresponding repeating key shift:

```text
P_i = (C_i - K_i) mod 26
```

The returned plaintext contains only uppercase letters because the input was
cleaned before decryption.

## Main program flow

`main()` performs the complete process in this order:

1. Reads and cleans `ciphertxt.txt`.
2. Runs the Kasiski examination.
3. Calculates average IC values for periods 1 through 15.
4. Selects the period with the highest average IC, unless `PERIOD` is set.
5. Recovers a key shift for each key position.
6. Decrypts the full ciphertext.
7. Prints the candidate key length, recovered keyword, and plaintext.

## Manually choosing a key length

At the top of the Python file, `PERIOD` is set to `None`, which enables
automatic selection. To test a key length suggested by the Kasiski results,
change it to an integer:

```python
PERIOD = 5
```

Run the script again after saving the change. The program will use period 5
instead of the automatically selected period.

## Output sections

The terminal output contains:

1. **Kasiski Examination** — repeated groups, positions, distances, and common
   distance factors.
2. **Average Index of Coincidence** — average IC values for candidate periods.
3. **Shift Correlation by Key Position** — selected shifts and the top five
   candidates for each key position.
4. **Final Results** — candidate key length, recovered keyword, and decrypted
   plaintext.

Because the period and key are estimated from letter frequencies, the result
is a candidate decryption and should be checked for readable English. 
