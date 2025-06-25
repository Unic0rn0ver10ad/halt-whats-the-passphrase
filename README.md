# 🛑 Halt! What's the Passphrase?

<img src="HWTP.jpg" alt="Halt! What's the Passphrase?" width="300">

**Halt! What's the Passphrase?** (HWTP) is a passphrase and password generator written in Python with a command-line interface (CLI) powered by `argparse`.

---

## 🚀 Features

- Generate memorable passphrases or secure passwords
- Rich CLI options for customization
- Optional integration with [Have I Been Pwned](https://haveibeenpwned.com/) to check for compromised passwords
- Fun, nerdy, and secure
- Quickly view cached dictionaries with `-ld`

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

List cached dictionaries:
```bash
python hwtp.py -ld
```
Each processed dictionary produces a `<name>_data.json` file in the `cache/` directory.

Process a single dictionary with a custom partition range:
```bash
python hwtp.py utils process -d mywords.txt --start-n 8 --end-n 40
```

Process all dictionaries in `wordlists/`:
```bash
python hwtp.py utils process-all --start-n 8 --end-n 40
```

Generate a standalone partitions file:
```bash
python hwtp.py utils part -o partitions.json --start-n 8 --end-n 40
```

---

## 📦 Installation

Clone this repo and run:
```bash
pip install -r requirements.txt
```

Or simply use the Python file directly if dependencies are already met.

---

## 🛠 Requirements

- Python 3.6+
- Optional: `requests` (for Wikipedia and pwned lookup features)

---

## 🧠 License

MIT License – do with it what you will, and make your passwords strong 💪

---

## 📸 Screenshot or Demo (Optional)

> _You can add a GIF or screenshot here showing HWTP in action using a tool like [asciinema](https://asciinema.org/) or a static terminal snapshot._

---

## 🙌 Contributions Welcome!

Feel free to fork, PR, or raise issues!

---

## 📫 Contact

[Your GitHub Profile or Email]

---

> _“Halt! What's the passphrase?” — every good secret door keeper, probably._
