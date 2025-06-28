# AGENTS Instructions

This file provides guidance for the Codex agent when working with this repository.

## Repository Overview

* **Halt! What's the Passphrase?** is a Python application that generates secure passphrases and passwords.
* There are no automated tests in this project. The GitHub workflow runs `flake8` and `pytest`, but the test step will be skipped if no tests are present.
* Dependencies are listed in `requirements.txt` (currently `colorama` and `requests`).
* Typical usage involves running `python hwtp.py` with various options as described in `README.md`.

## Guidelines for Codex

1. **Python Style**: Follow basic PEP 8 conventions (4‑space indentation, reasonable line lengths, etc.).
2. **Dependencies**: Run `python -m pip install -r requirements.txt` before executing scripts that require external packages.
3. **Testing**: There are no tests to run.
4. **File Scope**: This file applies to the entire repository. There are currently no nested `AGENTS.md` files.
5. **Prefer List Comprehensions, Dict Comprehensions, and Generators to Verbose Code**: Prefer Python list comprehensions, dictionary comprehensions, and generator expressions over multi-line loops or verbose code. This keeps the code concise, readable, and typically more efficient. Maintain identical functionality while reducing unnecessary lines, following the Python principle that code is read more often than it is written.
6. **Prefer `secrets` for Randomness**:
Always use Python’s built-in `secrets` module for generating random numbers, choices, or shuffles to ensure cryptographic-strength randomness. Only use the standard library `random` module if `secrets` does not provide the necessary functionality. If you must use `random`, clearly flag this in the proposed code so the repository maintainers can review or adjust it.