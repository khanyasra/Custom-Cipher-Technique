#include <bits/stdc++.h>
using namespace std;

class DualCipher {
private:
    string keyword;           // normalized keyword (uppercase)
    char playfairGrid[5][5];

    // Normalize: uppercase and keep only letters
    static string normalizeLetters(const string &s) {
        string out;
        out.reserve(s.size());
        for (char ch : s) {
            if (isalpha((unsigned char)ch)) out.push_back(toupper((unsigned char)ch));
        }
        return out;
    }

    // Build 26-letter substitution alphabet from keyword (keyword first, then remaining A..Z)
    string buildKeywordAlphabet(const string &rawKey) const {
        string key = rawKey;
        // uppercase
        for (char &c : key) c = toupper((unsigned char)c);

        string temp;
        temp.reserve(26 + key.size());
        // Append keyword characters first (remove duplicates)
        for (char c : key) {
            if (isalpha((unsigned char)c) && temp.find(c) == string::npos) temp.push_back(c);
        }
        // Append remaining A..Z
        for (char c = 'A'; c <= 'Z'; ++c) {
            if (temp.find(c) == string::npos) temp.push_back(c);
        }
        // temp length should be 26
        return temp;
    }

    // Build 5x5 playfair grid using keyword (J merged into I)
    void buildPlayfairGrid() {
        string key = "";
        // normalize keyword, map J->I, keep first occurrence only
        for (char ch : keyword) {
            char c = toupper((unsigned char)ch);
            if (c == 'J') c = 'I';
            if (isalpha((unsigned char)c) && key.find(c) == string::npos) key.push_back(c);
        }
        // fill remaining letters A..Z excluding J
        for (char c = 'A'; c <= 'Z'; ++c) {
            if (c == 'J') continue;
            if (key.find(c) == string::npos) key.push_back(c);
        }
        // populate grid
        int idx = 0;
        for (int r = 0; r < 5; ++r)
            for (int c = 0; c < 5; ++c)
                playfairGrid[r][c] = key[idx++];
    }

    // Find position of char in playfair grid (J treated as I)
    pair<int,int> findPosInGrid(char ch) const {
        if (ch == 'J') ch = 'I';
        for (int r = 0; r < 5; ++r)
            for (int c = 0; c < 5; ++c)
                if (playfairGrid[r][c] == ch) return {r, c};
        return {-1, -1};
    }

    // Prepare text for Playfair: uppercase, J->I, remove non-letters, insert X between identical letters in a digraph, pad with X
    static string prepareForPlayfair(const string &raw) {
        string cleaned;
        for (char ch : raw) {
            if (isalpha((unsigned char)ch)) {
                char c = toupper((unsigned char)ch);
                if (c == 'J') c = 'I';
                cleaned.push_back(c);
            }
        }
        string out;
        out.reserve(cleaned.size() + 4);
        for (size_t i = 0; i < cleaned.size(); ++i) {
            char a = cleaned[i];
            out.push_back(a);
            if (i + 1 < cleaned.size()) {
                char b = cleaned[i+1];
                if (a == b) {
                    out.push_back('X'); // insert separator
                } else {
                    out.push_back(b);
                    ++i; // consumed next char as part of pair
                }
            }
        }
        if (out.size() % 2 == 1) out.push_back('X');
        // Note: out contains digraphs as pairs of characters
        return out;
    }

    // Playfair encrypt for prepared text (assumes even length)
    string playfairEncryptPrepared(const string &prepared) {
        string cipher;
        cipher.reserve(prepared.size());
        for (size_t i = 0; i < prepared.size(); i += 2) {
            char a = prepared[i], b = prepared[i+1];
            auto p1 = findPosInGrid(a);
            auto p2 = findPosInGrid(b);
            int r1 = p1.first, c1 = p1.second;
            int r2 = p2.first, c2 = p2.second;
            if (r1 == r2) {
                cipher.push_back(playfairGrid[r1][(c1 + 1) % 5]);
                cipher.push_back(playfairGrid[r2][(c2 + 1) % 5]);
            } else if (c1 == c2) {
                cipher.push_back(playfairGrid[(r1 + 1) % 5][c1]);
                cipher.push_back(playfairGrid[(r2 + 1) % 5][c2]);
            } else {
                cipher.push_back(playfairGrid[r1][c2]);
                cipher.push_back(playfairGrid[r2][c1]);
            }
        }
        return cipher;
    }

    // Playfair decrypt (cipher length must be even)
    string playfairDecryptCipher(const string &cipher) {
        string plain;
        plain.reserve(cipher.size());
        for (size_t i = 0; i < cipher.size(); i += 2) {
            char a = cipher[i], b = cipher[i+1];
            auto p1 = findPosInGrid(a);
            auto p2 = findPosInGrid(b);
            int r1 = p1.first, c1 = p1.second;
            int r2 = p2.first, c2 = p2.second;
            if (r1 == r2) {
                plain.push_back(playfairGrid[r1][(c1 + 4) % 5]);
                plain.push_back(playfairGrid[r2][(c2 + 4) % 5]);
            } else if (c1 == c2) {
                plain.push_back(playfairGrid[(r1 + 4) % 5][c1]);
                plain.push_back(playfairGrid[(r2 + 4) % 5][c2]);
            } else {
                plain.push_back(playfairGrid[r1][c2]);
                plain.push_back(playfairGrid[r2][c1]);
            }
        }
        return plain;
    }

public:
    DualCipher() = default;

    // set keyword (normalize to uppercase letters only)
    void setKeyword(const string &k) {
        keyword.clear();
        for (char ch : k) if (isalpha((unsigned char)ch)) keyword.push_back(toupper((unsigned char)ch));
        buildPlayfairGrid();
    }

    // Keyword substitution encrypt: plaintext -> substitution using keyword alphabet
    string keywordEncrypt(const string &plain) const {
        string cleaned = normalizeLetters(plain);
        string map = buildKeywordAlphabet(keyword);
        const string alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        string out;
        out.reserve(cleaned.size());
        for (char c : cleaned) {
            size_t pos = alpha.find(c);
            if (pos != string::npos) out.push_back(map[pos]);
            else out.push_back(c);
        }
        return out;
    }

    // Keyword substitution decrypt: reverse map
    string keywordDecrypt(const string &cipher) const {
        string cleaned = normalizeLetters(cipher);
        string map = buildKeywordAlphabet(keyword);
        const string alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        string out;
        out.reserve(cleaned.size());
        for (char c : cleaned) {
            size_t pos = map.find(c);
            if (pos != string::npos) out.push_back(alpha[pos]);
            else out.push_back(c);
        }
        return out;
    }

    // Full encryption: Keyword -> Playfair
    string encrypt(const string &plaintext) {
        // Stage 1: keyword substitution
        string stage1 = keywordEncrypt(plaintext);
        // Stage 2: prepare for playfair and encrypt
        string prepared = prepareForPlayfair(stage1);
        string cipher = playfairEncryptPrepared(prepared);
        return cipher;
    }

    // Full decryption: Playfair -> Keyword
    string decrypt(const string &ciphertext) {
        // Stage 1: Playfair decrypt
        string stage1 = playfairDecryptCipher(ciphertext);
        // Stage 2: keyword decryption
        string plain = keywordDecrypt(stage1);
        return plain;
    }

    // helper to display playfair grid (debug)
    void showPlayfairGrid() const {
        for (int r = 0; r < 5; ++r) {
            for (int c = 0; c < 5; ++c) cout << playfairGrid[r][c] << ' ';
            cout << '\n';
        }
    }
};
int main() {
    DualCipher dc;
    string keyword, plaintext;

    cout << "Enter keyword (letters only): ";
    cin >> keyword;               // takes keyword (no spaces)
    dc.setKeyword(keyword);

    cin.ignore();                 // clear leftover newline

    cout << "Enter plaintext message: ";
    getline(cin, plaintext);      // allows spaces in message

    string ciphertext = dc.encrypt(plaintext);
    cout << "\nCiphertext: " << ciphertext << endl;

    string recovered = dc.decrypt(ciphertext);
    cout << "Recovered/ Decrypted text: " << recovered << endl;

    return 0;
}



