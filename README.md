# 🛑 Halt! What's the Passphrase?

<img src="HWTP.jpg" alt="Halt! What's the Passphrase?" width="300">

**Halt! What's the Passphrase?** (HWTP) is a passphrase and password generator written in Python with a command-line interface (CLI) powered by `argparse`.

---

## 🚀 Features

- Generate memorable passphrases or secure passwords
- Rich CLI options for customization
- Optional integration with [Have I Been Pwned](https://haveibeenpwned.com/) to check for compromised passwords
- Fun, nerdy, and secure
- Quickly view cached wordlists with `-lw`
- Choose which cached dictionary to use with `-d`

---

## 🎮 Fun With Passphrases

Generate a single passphrase:
```bash
python hwtp.py pp
```

Generate 20 colorized passphrases:
```bash
python hwtp.py pp -co -n 20
```

Smush 5 words together per passphrase:
```bash
python hwtp.py pp -co -n 20 -nw 5
```

Use the Augenbaum method with parameter `5@`:
```bash
python hwtp.py pp -co -n 20 -au 5@
```

Generate 32-character passphrases:
```bash
python hwtp.py pp -co -n 20 -c 32
```

Use a specific cached dictionary:
```bash
python hwtp.py pp -d eff_short_wordlist
```

Pad the passphrase with a custom string:
```bash
python hwtp.py pp -co -pad m0nk3y! 3
```

Customize the partition range (advanced):
```bash
python hwtp.py pp --start-n 8 --end-n 40
```

Display help:
```bash
python hwtp.py pp -h
```

Use Wikipedia as a source with verbose output:
```bash
python hwtp.py pp -co -w -v
```

Wikipedia + multiple passphrases:
```bash
python hwtp.py pp -co -w -n 10
```

Check a passphrase against breaches:
```bash
python hwtp.py pp -co -pwn
```

Check a specific password:
```bash
python hwtp.py pwn f00tl00se
```

---

## 🔐 Fun With Passwords

Colorized, 20 passwords with lots of filters:
```bash
python hwtp.py pw -co -nc -n 20 -no l u s -v
```

10-character passwords, tightly controlled:
```bash
python hwtp.py pw -co -nc -n 20 -c 10 -v -no l -md 4 -ms 4 -a -x -b
```

Bookended, balanced, and secure:
```bash
python hwtp.py pw -co -nc -ms 3 -md 3 -b -n 20 -c 8 -v
```

Check generated passwords against known breaches:
```bash
python hwtp.py pw -co -pwn
```

🔴 Example of a configuration that **won't work**:
```bash
python hwtp.py pw -co -nc -ms 4 -md 4 -b -n 20 -c 8 -v
```

Limit character sets with exclusions:
```bash
python hwtp.py pw -co -n 10 -no u l d -sd '@ # $ _ & ( ) / : ; ! ? - ='
```

Or whitelist specific special characters:
```bash
python hwtp.py pw -co -n 10 -no u l d -so '@ # $ ='
```

### Dictionary Utilities

List cached wordlists:
```bash
python hwtp.py -lw
```

Process a single dictionary with a custom partition range:
```bash
python hwtp.py utils process -d mywords.txt --start-n 8 --end-n 40
```
Adjust minimum and maximum word lengths:
```bash
python hwtp.py utils process -d mywords.txt -minw 3 -maxw 8
```

Process all dictionaries in `wordlists/`:
```bash
python hwtp.py utils process-all --start-n 8 --end-n 40
```
With custom word lengths for every dictionary:
```bash
python hwtp.py utils process-all -minw 3 -maxw 8
```

Generate a standalone partitions file:
```bash
python hwtp.py utils part -o partitions.json --start-n 8 --end-n 40
```
You can also set word length bounds when generating partitions:
```bash
python hwtp.py utils part -o partitions.json -minw 3 -maxw 8
```

### Dictionary JSON Format

Processed dictionaries are stored in `cache/` using a single JSON file:

```json
{
  "metadata": {
    "language": "English",
    "has_partitions": true,
    "min_word_length": 4,
    "max_word_length": 9
  },
  "wordlengths": {
    "4": ["haze", "iris"],
    "5": ["brisk", "noble"]
  },
  "partitions": {
    "8": [[4,4], [8]]
  }
}
```
The `partitions` section is optional and only included when available.

---

## 📦 Installation

Clone this repo and run:
```bash
pip install -r requirements.txt
```
This will install the required packages `colorama` and `requests`.

Or simply use the Python file directly if dependencies are already met.

---

## 🛠 Requirements

- Python 3.6+
- `colorama`
- `requests`

---

## 🧠 License

MIT License – do with it what you will, and may your passphrases not end up in HaveIBeenPwned 💪

---

## 🙌 Contributions Welcome!

Feel free to fork, PR, or raise issues!

---

## 📫 Contact

[Your GitHub Profile or Email]
