
"""
known_plain_attack.py
Demonstrates seeding the hill-climber with known plaintext info.
Usage example:
  python known_plain_attack.py --cipherfile cipher.txt --known "MYNAMEIS" --known_pos 0
"""

import argparse, subprocess, time, sys
# This is a thin wrapper that calls hillclimb_attack.py with known snippet arguments.
# Put both scripts in the same folder.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cipherfile", required=True)
    parser.add_argument("--known", required=True)
    parser.add_argument("--known_pos", type=int, default=0)
    parser.add_argument("--iter", type=int, default=20000)
    parser.add_argument("--restarts", type=int, default=5)
    args = parser.parse_args()

    cmd = ["python", "hillclimb_attack.py", "--infile", args.cipherfile,
           "--iter", str(args.iter), "--restarts", str(args.restarts),
           "--known", args.known, "--known_pos", str(args.known_pos)]
    print("Running command:", " ".join(cmd))
    p = subprocess.Popen(cmd)
    p.wait()
    print("Done.")

if __name__ == "__main__":
    main()
