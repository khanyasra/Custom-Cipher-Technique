# 🔐 DualCipher: Hybrid Keyword + Playfair Cipher with Attack Simulation

## 📘 Overview

**DualCipher** is a hybrid classical cryptography system that combines two traditional ciphers:

1. **Keyword Substitution Cipher**
2. **Playfair Cipher**

The system first applies **keyword-based substitution encryption**, followed by **Playfair cipher encryption** to provide an additional layer of obfuscation.  
This project also includes an **attack simulation module** that attempts to break the cipher using **frequency analysis** and **known-plaintext attacks**.

---

## ⚙️ Features

- 🔑 Dual encryption (Keyword + Playfair)
- 🔄 Full decryption (Playfair → Keyword)
- 📊 Attack simulation using:
  - Frequency analysis (via digraph scoring)
  - Hill-climbing heuristic search
  - Known-plaintext seeding for faster recovery
- 📈 Experimental framework for evaluating success rate and computational effort

---

## 🧩 Components

### 1. `DualCipher.cpp`
Implements the **encryption** and **decryption** pipeline.

- **Stage 1:** Keyword substitution
- **Stage 2:** Playfair cipher
- Supports case-insensitive input, auto normalization, and grid visualization.

**Usage:**
```bash
g++ -o DualCipher DualCipher.cpp
./DualCipher
```
### 2. `hill_climb_attack.py`
Performs a hill-climbing attack on ciphertext produced by the DualCipher.

- Explores substitution and Playfair key spaces
- Uses English digraph frequency scoring
- Supports optional known plaintext snippet
- Tracks runtime, success rate, and score
```bash
# Random hill-climb attack
python hillclimb_attack.py --cipher "NWILPEDTVOTSLV" --iter 50000 --restarts 5

# Known plaintext attack (faster convergence)
python hillclimb_attack.py --cipher "CIPHERTEXT_HERE" --iter 20000 --restarts 5 \
    --known "MYNAMEIS" --known_pos 0
```
### 3. `known_plain_attack.py`
A convenience wrapper that demonstrates known-plaintext attacks by calling the hill-climber with preset arguments.

```bash
python known_plain_attack.py --cipherfile cipher.txt --known "MYNAMEIS" --known_pos 0
```
