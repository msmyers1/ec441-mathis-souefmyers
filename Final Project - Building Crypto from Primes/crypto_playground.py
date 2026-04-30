#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   Nothing to Hide: Building Crypto from Prime Numbers       ║
║   Diffie-Hellman Key Exchange + RSA from Scratch            ║
║   EC 441 · Mathis Souef-Myers · Prof. Carruthers · S26     ║
╚══════════════════════════════════════════════════════════════╝

A step-by-step, interactive walkthrough of two foundational
cryptographic protocols using small primes so you can see
every number at every stage.

Run:  python3 crypto_playground.py

No dependencies beyond the Python 3 standard library.
"""

import random
import math
import time
import sys
import os

# ─── Terminal Colors ──────────────────────────────────────

class C:
    """ANSI color codes for pretty terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    ULINE   = "\033[4m"

    # Foreground
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

    # Background
    BG_DARK = "\033[48;5;236m"
    BG_BLUE = "\033[48;5;24m"
    BG_GREEN = "\033[48;5;22m"
    BG_RED  = "\033[48;5;52m"

    @staticmethod
    def disable():
        for attr in dir(C):
            if attr.isupper() and not attr.startswith("_"):
                setattr(C, attr, "")


# Disable colors if not a TTY
if not sys.stdout.isatty():
    C.disable()


# ─── Utility Functions ────────────────────────────────────

def slow_print(text, delay=0.01):
    """Print text character by character for dramatic effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def banner(text, color=C.CYAN):
    """Print a boxed banner."""
    width = max(len(line) for line in text.split("\n")) + 4
    print(f"\n{color}{'═' * width}")
    for line in text.split("\n"):
        print(f"  {C.BOLD}{line}{C.RESET}{color}")
    print(f"{'═' * width}{C.RESET}\n")


def step(num, title):
    """Print a numbered step header."""
    print(f"\n  {C.CYAN}{C.BOLD}Step {num}{C.RESET} {C.GRAY}│{C.RESET} {C.WHITE}{C.BOLD}{title}{C.RESET}")
    print(f"  {C.GRAY}{'─' * 50}{C.RESET}")


def show_val(label, value, color=C.GREEN):
    """Print a labeled value."""
    print(f"    {C.GRAY}{label:<24}{C.RESET} {color}{C.BOLD}{value}{C.RESET}")


def show_math(expression, color=C.YELLOW):
    """Print a math expression."""
    print(f"    {color}{expression}{C.RESET}")


def box_line(visible_text, width, color_text="", border="│"):
    """Build a box line with correct padding despite ANSI codes.
    visible_text: the text without any ANSI codes (used for width calc)
    color_text: the actual text with ANSI codes to print
    width: inner width between border characters
    """
    if not color_text:
        color_text = visible_text
    pad = width - len(visible_text)
    return f"    {border}  {color_text}{' ' * max(0, pad - 2)}{border}"


def pause(msg="Press Enter to continue (q to quit)..."):
    """Wait for user input. Quit if 'q' is entered."""
    try:
        resp = input(f"\n  {C.DIM}{msg}{C.RESET}").strip().lower()
        if resp == "q":
            print(f"\n  {C.GRAY}Thanks for exploring! Goodbye.{C.RESET}\n")
            sys.exit(0)
    except EOFError:
        pass


def is_prime(n):
    """Simple primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def find_primitive_root(p):
    """Find a primitive root modulo p."""
    if p == 2:
        return 1
    phi = p - 1
    # Find prime factors of phi
    factors = set()
    n = phi
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)

    for g in range(2, p):
        if all(pow(g, phi // f, p) != 1 for f in factors):
            return g
    return None


def mod_inverse(e, phi):
    """Extended Euclidean algorithm to find modular inverse."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        return gcd, y1 - (b // a) * x1, x1

    _, x, _ = extended_gcd(e % phi, phi)
    return (x % phi + phi) % phi


def gcd(a, b):
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


# ─── Diffie-Hellman ───────────────────────────────────────

def diffie_hellman():
    """Interactive Diffie-Hellman key exchange demo."""

    banner("DIFFIE-HELLMAN KEY EXCHANGE\nTwo parties agree on a shared secret\nover an insecure channel")

    print(f"  {C.WHITE}The Scenario:{C.RESET}")
    print(f"  {C.GRAY}Tifa and Aerith want to establish a shared secret key.")
    print(f"  Cloud is eavesdropping on every message they send.")
    print(f"  They've never met and have no pre-shared secrets.{C.RESET}")
    print()
    print(f"  {C.YELLOW}The Magic:{C.RESET} {C.GRAY}Diffie-Hellman lets them do it anyway,")
    print(f"  using the one-way nature of modular exponentiation.{C.RESET}")

    pause()

    # ── Step 1: Public Parameters ──
    step(1, "Agree on public parameters")

    print(f"    {C.GRAY}Tifa and Aerith publicly agree on:{C.RESET}")
    print(f"    {C.GRAY}  • p = a large prime number")
    print(f"    {C.GRAY}  • g = a primitive root mod p{C.RESET}")
    print()

    # Let user pick or use defaults
    print(f"  {C.WHITE}Choose prime size:{C.RESET}")
    print(f"    {C.CYAN}[1]{C.RESET} Small  (p ≈ 23)     — see every number")
    print(f"    {C.CYAN}[2]{C.RESET} Medium (p ≈ 541)    — harder to brute force")
    print(f"    {C.CYAN}[3]{C.RESET} Large  (p ≈ 7919)   — impractical to crack by hand")
    print(f"    {C.CYAN}[4]{C.RESET} Custom — enter your own prime")

    try:
        choice = input(f"\n  {C.DIM}Pick [1/2/3/4]: {C.RESET}").strip()
    except EOFError:
        choice = "1"

    if choice == "2":
        p = 541
    elif choice == "3":
        p = 7919
    elif choice == "4":
        try:
            p = int(input(f"  {C.DIM}Enter a prime number: {C.RESET}").strip())
            if not is_prime(p):
                print(f"  {C.RED}Not prime! Using 23 instead.{C.RESET}")
                p = 23
        except (ValueError, EOFError):
            p = 23
    else:
        p = 23

    g = find_primitive_root(p)

    show_val("p (prime modulus)", p, C.CYAN)
    show_val("g (primitive root)", g, C.CYAN)
    print()
    print(f"    {C.GRAY}These are PUBLIC — Cloud can see them too.{C.RESET}")

    pause()

    # ── Step 2: Private Keys ──
    step(2, "Each party picks a PRIVATE secret")

    a = random.randint(2, p - 2)  # Tifa's secret
    b = random.randint(2, p - 2)  # Aerith's secret

    print(f"    {C.BLUE}Tifa{C.RESET} secretly picks:  {C.BOLD}a = {a}{C.RESET}")
    print(f"    {C.GREEN}Aerith{C.RESET} secretly picks:  {C.BOLD}b = {b}{C.RESET}")
    print()
    print(f"    {C.RED}Cloud{C.RESET} does NOT know a or b.")

    pause()

    # ── Step 3: Public Values ──
    step(3, "Compute and exchange PUBLIC values")

    A = pow(g, a, p)
    B = pow(g, b, p)

    print(f"    {C.BLUE}Tifa{C.RESET} computes:")
    show_math(f"A = g^a mod p = {g}^{a} mod {p} = {A}")
    print()
    print(f"    {C.GREEN}Aerith{C.RESET} computes:")
    show_math(f"B = g^b mod p = {g}^{b} mod {p} = {B}")
    print()
    print(f"    They exchange A and B publicly.")
    print()

    W = 48  # inner width
    print(f"    ┌{'─' * W}┐")
    l1_vis = f"  Tifa  ──── A = {A} ────▶  Aerith"
    l1_clr = f"  {C.BLUE}Tifa{C.RESET}  ──── {C.YELLOW}A = {A}{C.RESET} ────▶  {C.GREEN}Aerith{C.RESET}"
    print(box_line(l1_vis, W, l1_clr))
    l2_vis = f"  Tifa  ◀── B = {B} ─────  Aerith"
    l2_clr = f"  {C.BLUE}Tifa{C.RESET}  ◀── {C.YELLOW}B = {B}{C.RESET} ─────  {C.GREEN}Aerith{C.RESET}"
    print(box_line(l2_vis, W, l2_clr))
    l3_vis = f"     👁  Cloud sees: p={p}, g={g}, A={A}, B={B}"
    l3_clr = f"    {C.RED}👁  Cloud sees: p={p}, g={g}, A={A}, B={B}{C.RESET}"
    print(box_line(l3_vis, W, l3_clr))
    print(f"    └{'─' * W}┘")

    pause()

    # ── Step 4: Shared Secret ──
    step(4, "Each party computes the SHARED SECRET")

    s_alice = pow(B, a, p)
    s_bob = pow(A, b, p)

    print(f"    {C.BLUE}Tifa{C.RESET} computes:  s = B^a mod p")
    show_math(f"s = {B}^{a} mod {p} = {s_alice}")
    print()
    print(f"    {C.GREEN}Aerith{C.RESET} computes:    s = A^b mod p")
    show_math(f"s = {A}^{b} mod {p} = {s_bob}")
    print()

    if s_alice == s_bob:
        print(f"    {C.BG_GREEN} {C.WHITE}{C.BOLD} ✓ MATCH! Shared secret = {s_alice} {C.RESET}")
    else:
        print(f"    {C.BG_RED} {C.WHITE}{C.BOLD} ✗ MISMATCH — something went wrong {C.RESET}")

    print()
    print(f"    {C.GRAY}Why it works:  B^a = (g^b)^a = g^(ab) = (g^a)^b = A^b  (mod p)")
    print(f"    Both sides compute g^(ab) mod p without ever sending a or b.{C.RESET}")

    pause()

    # ── Step 5: Cloud's Perspective ──
    step(5, "Cloud's perspective — the Discrete Log Problem")

    print(f"    {C.RED}Cloud{C.RESET} knows: p = {p}, g = {g}, A = {A}, B = {B}")
    print(f"    {C.RED}Cloud{C.RESET} needs: a or b")
    print(f"    {C.RED}Cloud{C.RESET} must solve: {g}^a ≡ {A} (mod {p})  →  a = ?")
    print()

    # Brute force it for small primes to show the work
    if p <= 100:
        print(f"    {C.YELLOW}Brute-forcing (only feasible for tiny primes):{C.RESET}")
        for test_a in range(1, p):
            result = pow(g, test_a, p)
            marker = ""
            if result == A:
                marker = f"  {C.GREEN}◄ FOUND a = {test_a}!{C.RESET}"
            if test_a <= 10 or result == A:
                print(f"      {C.GRAY}{g}^{test_a:>3} mod {p} = {result:>5}{C.RESET}{marker}")
            elif test_a == 11:
                print(f"      {C.GRAY}  ...{C.RESET}")
        print()
        print(f"    {C.GRAY}With p = {p}, brute force checks only {p - 1} values.")
        print(f"    With p = 2048-bit prime, there are ~10^{616} possibilities.")
        print(f"    No known efficient algorithm exists. That's the security.{C.RESET}")
    else:
        print(f"    {C.GRAY}With p = {p}, brute force needs up to {p-1} attempts.")
        print(f"    Real DH uses 2048+ bit primes where brute force is")
        print(f"    computationally infeasible (billions of years).{C.RESET}")

    pause()
    return s_alice


# ─── RSA ──────────────────────────────────────────────────

def rsa_demo():
    """Interactive RSA encryption and digital signatures demo."""

    banner("RSA — RIVEST, SHAMIR, ADLEMAN\nAsymmetric encryption & digital signatures\nfrom two prime numbers")

    print(f"  {C.WHITE}The Idea:{C.RESET}")
    print(f"  {C.GRAY}RSA relies on the fact that multiplying two primes is easy,")
    print(f"  but factoring their product back into primes is hard.{C.RESET}")
    print()
    print(f"  {C.GRAY}We generate a public/private key pair. Anyone can encrypt")
    print(f"  with the public key; only the private key can decrypt.{C.RESET}")

    pause()

    # ── Step 1: Choose Primes ──
    step(1, "Choose two distinct primes p and q")

    print(f"  {C.WHITE}Choose prime size:{C.RESET}")
    print(f"    {C.CYAN}[1]{C.RESET} Tiny   (p,q < 30)    — see all the math")
    print(f"    {C.CYAN}[2]{C.RESET} Small  (p,q < 100)   — slightly harder")
    print(f"    {C.CYAN}[3]{C.RESET} Medium (p,q < 500)   — big enough for text")
    print(f"    {C.CYAN}[4]{C.RESET} Custom — enter your own primes")

    try:
        choice = input(f"\n  {C.DIM}Pick [1/2/3/4]: {C.RESET}").strip()
    except EOFError:
        choice = "1"

    small_primes = [p for p in range(3, 500) if is_prime(p)]

    if choice == "2":
        pool = [p for p in small_primes if p < 100]
    elif choice == "3":
        pool = [p for p in small_primes if 50 < p < 500]
    elif choice == "4":
        try:
            p_in = int(input(f"  {C.DIM}Enter prime p: {C.RESET}").strip())
            q_in = int(input(f"  {C.DIM}Enter prime q: {C.RESET}").strip())
            if not (is_prime(p_in) and is_prime(q_in) and p_in != q_in):
                print(f"  {C.RED}Invalid! Using defaults.{C.RESET}")
                pool = [p for p in small_primes if p < 30]
                p_in = q_in = None
            else:
                pool = None
        except (ValueError, EOFError):
            pool = [p for p in small_primes if p < 30]
            p_in = q_in = None
    else:
        pool = [p for p in small_primes if p < 30]
        p_in = q_in = None

    if choice == "4" and pool is None:
        p, q = p_in, q_in
    else:
        p = random.choice(pool)
        q = random.choice([x for x in pool if x != p])

    show_val("p", p, C.CYAN)
    show_val("q", q, C.CYAN)
    print()
    print(f"    {C.RED}These are SECRET. Destroy after key generation.{C.RESET}")

    pause()

    # ── Step 2: Compute n and φ(n) ──
    step(2, "Compute n = p × q and φ(n) = (p-1)(q-1)")

    n = p * q
    phi_n = (p - 1) * (q - 1)

    show_math(f"n = p × q = {p} × {q} = {n}")
    show_math(f"φ(n) = (p-1)(q-1) = {p-1} × {q-1} = {phi_n}")
    print()
    show_val("n (public modulus)", n, C.GREEN)
    show_val("φ(n) (kept secret)", phi_n, C.RED)
    print()
    print(f"    {C.GRAY}n is public — but factoring it back to p and q is the hard part.")
    print(f"    For n = {n}, it's trivial. For 2048-bit n, it takes longer than")
    print(f"    the age of the universe with current algorithms.{C.RESET}")

    pause()

    # ── Step 3: Choose e ──
    step(3, "Choose public exponent e")

    print(f"    {C.GRAY}e must satisfy: 1 < e < φ(n) and gcd(e, φ(n)) = 1{C.RESET}")
    print()

    # Find valid e values
    valid_e = [e for e in range(3, phi_n) if gcd(e, phi_n) == 1]

    # Show a few candidates
    print(f"    {C.GRAY}Candidates (showing first 8 coprime to φ(n) = {phi_n}):{C.RESET}")
    for i, e_cand in enumerate(valid_e[:8]):
        marker = f"  {C.GREEN}◄ common choice{C.RESET}" if e_cand in (3, 17, 65537) else ""
        print(f"      e = {e_cand:>5}   gcd({e_cand}, {phi_n}) = {gcd(e_cand, phi_n)}{marker}")

    # Pick e (prefer 65537 if valid, else 17, else smallest)
    if 65537 in valid_e:
        e = 65537
    elif 17 in valid_e:
        e = 17
    else:
        e = valid_e[0]

    print()
    show_val("e (public exponent)", e, C.GREEN)
    print()
    print(f"    {C.GRAY}In practice, e = 65537 is almost always used (efficient")
    print(f"    because it's 10000000000000001 in binary — fast modular exp).{C.RESET}")

    pause()

    # ── Step 4: Compute d ──
    step(4, "Compute private exponent d = e⁻¹ mod φ(n)")

    d = mod_inverse(e, phi_n)

    print(f"    {C.GRAY}We need d such that: e × d ≡ 1 (mod φ(n))")
    print(f"    Using the Extended Euclidean Algorithm:{C.RESET}")
    print()
    show_math(f"e × d ≡ 1 (mod φ(n))")
    show_math(f"{e} × d ≡ 1 (mod {phi_n})")
    show_math(f"d = {d}")
    print()
    print(f"    {C.GRAY}Verify: {e} × {d} = {e * d} = {(e * d) // phi_n} × {phi_n} + {(e * d) % phi_n}  ✓{C.RESET}")
    print()
    show_val("d (PRIVATE exponent)", d, C.RED)

    pause()

    # ── Step 5: Key Summary ──
    step(5, "Key Pair Summary")

    W = 46
    print(f"    ┌{'─' * W}┐")
    pub_vis = f"  PUBLIC KEY   (e, n) = ({e}, {n})"
    pub_clr = f"  {C.GREEN}{C.BOLD}PUBLIC KEY{C.RESET}   (e, n) = ({e}, {n})"
    print(box_line(pub_vis, W, pub_clr))
    prv_vis = f"  PRIVATE KEY  (d, n) = ({d}, {n})"
    prv_clr = f"  {C.RED}{C.BOLD}PRIVATE KEY{C.RESET}  (d, n) = ({d}, {n})"
    print(box_line(prv_vis, W, prv_clr))
    print(f"    └{'─' * W}┘")
    print()
    print(f"    {C.GRAY}Public key is shared with everyone.")
    print(f"    Private key is kept secret by the owner.{C.RESET}")

    pause()

    # ── Step 6: Encryption / Decryption ──
    step(6, "Encryption & Decryption")

    max_msg = n - 1
    print(f"    {C.GRAY}Message must be an integer m where 0 ≤ m < n = {n}{C.RESET}")
    print()

    try:
        msg_input = input(f"  {C.DIM}Enter a number to encrypt (1–{max_msg}), or press Enter for random: {C.RESET}").strip()
        if msg_input:
            m = int(msg_input)
            if m < 1 or m >= n:
                print(f"  {C.RED}Out of range! Using random.{C.RESET}")
                m = random.randint(2, min(max_msg, 100))
        else:
            m = random.randint(2, min(max_msg, 100))
    except (ValueError, EOFError):
        m = random.randint(2, min(max_msg, 100))

    print()
    show_val("Plaintext m", m, C.WHITE)

    # Encrypt
    c = pow(m, e, n)
    print()
    print(f"    {C.GREEN}Encrypt{C.RESET} with public key (e={e}, n={n}):")
    show_math(f"c = m^e mod n = {m}^{e} mod {n} = {c}")
    show_val("Ciphertext c", c, C.YELLOW)

    # Decrypt
    m_dec = pow(c, d, n)
    print()
    print(f"    {C.RED}Decrypt{C.RESET} with private key (d={d}, n={n}):")
    show_math(f"m = c^d mod n = {c}^{d} mod {n} = {m_dec}")
    show_val("Recovered plaintext", m_dec, C.WHITE)

    if m == m_dec:
        print(f"\n    {C.BG_GREEN} {C.WHITE}{C.BOLD} ✓ Decryption successful! {m} → {c} → {m_dec} {C.RESET}")
    else:
        print(f"\n    {C.BG_RED} {C.WHITE}{C.BOLD} ✗ ERROR — decryption failed {C.RESET}")

    pause()

    # ── Step 7: Digital Signatures ──
    step(7, "Digital Signatures — proving authenticity")

    print(f"    {C.GRAY}Signing is RSA in reverse: encrypt with PRIVATE key,")
    print(f"    anyone can verify with the PUBLIC key.{C.RESET}")
    print()

    # Sign
    msg_to_sign = m
    show_val("Message to sign", msg_to_sign, C.WHITE)

    sig = pow(msg_to_sign, d, n)
    print()
    print(f"    {C.RED}Sign{C.RESET} with private key (d={d}):")
    show_math(f"σ = m^d mod n = {msg_to_sign}^{d} mod {n} = {sig}")
    show_val("Signature σ", sig, C.MAGENTA)

    # Verify
    verified = pow(sig, e, n)
    print()
    print(f"    {C.GREEN}Verify{C.RESET} with public key (e={e}):")
    show_math(f"m' = σ^e mod n = {sig}^{e} mod {n} = {verified}")

    if verified == msg_to_sign:
        print(f"\n    {C.BG_GREEN} {C.WHITE}{C.BOLD} ✓ Signature valid! Message is authentic. {C.RESET}")
    else:
        print(f"\n    {C.BG_RED} {C.WHITE}{C.BOLD} ✗ Signature invalid! Message was tampered with. {C.RESET}")

    print()
    print(f"    {C.GRAY}In practice, we sign a hash of the message (SHA-256),")
    print(f"    not the message itself. This is faster and avoids")
    print(f"    the m < n size restriction.{C.RESET}")

    pause()

    # ── Step 8: Attacker's Perspective ──
    step(8, "Attacker's perspective — the Factoring Problem")

    print(f"    {C.RED}Cloud{C.RESET} knows the public key: (e={e}, n={n})")
    print(f"    {C.RED}Cloud{C.RESET} must find d to decrypt.")
    print(f"    {C.RED}Cloud{C.RESET} needs φ(n) — which requires factoring n.")
    print()

    if n < 10000:
        print(f"    {C.YELLOW}Brute-force factoring n = {n}:{C.RESET}")
        attempts = 0
        for factor in range(2, int(n**0.5) + 1):
            attempts += 1
            if n % factor == 0:
                print(f"      {C.GRAY}Attempt {attempts}: {n} ÷ {factor} = {n // factor}  {C.GREEN}◄ FOUND!{C.RESET}")
                print(f"      {C.GRAY}n = {factor} × {n // factor}{C.RESET}")
                break
            elif attempts <= 5 or factor == int(n**0.5):
                print(f"      {C.GRAY}Attempt {attempts}: {n} ÷ {factor} = {n / factor:.2f}  ✗{C.RESET}")
            elif attempts == 6:
                print(f"      {C.GRAY}  ...{C.RESET}")

        print()
        print(f"    {C.GRAY}Only {attempts} attempts for n = {n}.")
        print(f"    For a 2048-bit RSA key, n has ~617 digits.")
        print(f"    The largest RSA number factored (RSA-250) had 250 digits")
        print(f"    and took ~2700 CPU-core-years in 2020.{C.RESET}")
    else:
        print(f"    {C.GRAY}n = {n} is small enough to factor instantly,")
        print(f"    but 2048-bit keys (617+ digit n) remain infeasible.{C.RESET}")

    pause()
    return (e, n), (d, n)


# ─── Text Encryption Demo ────────────────────────────────

def text_encryption_demo(pub_key, priv_key):
    """Encrypt and decrypt a text message using the RSA keys."""
    e, n = pub_key
    d, _ = priv_key

    banner("BONUS: TEXT ENCRYPTION\nEncrypt a short message character by character")

    print(f"    {C.GRAY}Each character → its ASCII code → RSA encrypt → ciphertext number")
    print(f"    Max character code must be < n = {n}{C.RESET}")
    print()

    if n < 128:
        print(f"    {C.RED}n = {n} is too small for full ASCII (need n ≥ 128).")
        print(f"    Use medium or larger primes for text encryption.{C.RESET}")
        pause()
        return

    try:
        msg = input(f"  {C.DIM}Enter a short message: {C.RESET}").strip()
    except EOFError:
        msg = "Hello"

    if not msg:
        msg = "Hello"

    # Check all chars fit
    if any(ord(ch) >= n for ch in msg):
        print(f"  {C.RED}Some characters have codes ≥ n. Truncating.{C.RESET}")
        msg = "".join(ch for ch in msg if ord(ch) < n)

    print()
    print(f"    {C.WHITE}Plaintext:{C.RESET}  \"{msg}\"")
    print()

    # Encrypt each character
    encrypted = []
    print(f"    {C.GREEN}Encrypting:{C.RESET}")
    for ch in msg:
        m = ord(ch)
        c = pow(m, e, n)
        encrypted.append(c)
        print(f"      '{ch}' → ASCII {m:>3} → {m}^{e} mod {n} = {C.YELLOW}{c}{C.RESET}")

    print()
    print(f"    {C.YELLOW}Ciphertext:{C.RESET}  {encrypted}")
    print()

    # Decrypt
    decrypted = []
    print(f"    {C.RED}Decrypting:{C.RESET}")
    for c in encrypted:
        m = pow(c, d, n)
        ch = chr(m)
        decrypted.append(ch)
        print(f"      {c} → {c}^{d} mod {n} = {m} → '{C.GREEN}{ch}{C.RESET}'")

    recovered = "".join(decrypted)
    print()
    print(f"    {C.WHITE}Recovered:{C.RESET}  \"{recovered}\"")

    if recovered == msg:
        print(f"\n    {C.BG_GREEN} {C.WHITE}{C.BOLD} ✓ Perfect recovery! {C.RESET}")
    else:
        print(f"\n    {C.BG_RED} {C.WHITE}{C.BOLD} ✗ Mismatch! {C.RESET}")

    pause()


# ─── Putting It Together ──────────────────────────────────

def connection_demo(dh_secret, pub_key):
    """Show how DH + RSA work together in practice (like TLS)."""

    banner("HOW THEY WORK TOGETHER\nThe TLS Connection (Simplified)")

    e, n = pub_key

    print(f"  {C.GRAY}In a real TLS connection, both protocols play a role:{C.RESET}")
    print()
    print(f"    {C.CYAN}1.{C.RESET} Server sends its {C.GREEN}RSA public key{C.RESET} (in a certificate)")
    print(f"    {C.CYAN}2.{C.RESET} Client & server run {C.YELLOW}Diffie-Hellman{C.RESET} to get a shared secret")
    print(f"    {C.CYAN}3.{C.RESET} DH parameters are {C.MAGENTA}signed with RSA{C.RESET} to prevent MITM")
    print(f"    {C.CYAN}4.{C.RESET} The DH shared secret becomes the {C.WHITE}symmetric session key{C.RESET}")
    print(f"    {C.CYAN}5.{C.RESET} All further traffic uses fast {C.WHITE}AES encryption{C.RESET} with that key")
    print()
    W = 55
    print(f"    ┌{'─' * W}┐")
    print(f"    │{' ' * W}│")
    for vis, clr in [
        ("  RSA  = Authentication (proves identity, signs DH)", f"  {C.GREEN}RSA{C.RESET}  = Authentication (proves identity, signs DH)"),
        ("  DH   = Key Exchange  (creates shared secret)", f"  {C.YELLOW}DH{C.RESET}   = Key Exchange  (creates shared secret)"),
        ("  AES  = Bulk Encryption (encrypts actual data)", f"  {C.WHITE}AES{C.RESET}  = Bulk Encryption (encrypts actual data)"),
    ]:
        print(box_line(vis, W, clr))
    print(f"    │{' ' * W}│")
    for vis, clr in [
        ("  RSA alone is too slow for bulk data.", f"  {C.GRAY}RSA alone is too slow for bulk data.{C.RESET}"),
        ("  DH alone can't authenticate (vulnerable to MITM).", f"  {C.GRAY}DH alone can't authenticate (vulnerable to MITM).{C.RESET}"),
        ("  Together they provide the best of both worlds.", f"  {C.GRAY}Together they provide the best of both worlds.{C.RESET}"),
    ]:
        print(box_line(vis, W, clr))
    print(f"    │{' ' * W}│")
    print(f"    └{'─' * W}┘")
    print()

    print(f"  {C.WHITE}From this demo:{C.RESET}")
    print(f"    DH shared secret:  {C.YELLOW}{dh_secret}{C.RESET}  → would derive AES-256 session key")
    print(f"    RSA public key:    {C.GREEN}(e={e}, n={n}){C.RESET}  → authenticates the server")

    pause()


# ─── Main Menu ────────────────────────────────────────────

def main():
    os.system("clear" if os.name == "posix" else "cls")

    BW = 60  # inner width of banner
    def bline(vis, clr=""):
        if not clr: clr = vis
        pad = BW - len(vis)
        return f"  {C.CYAN}║{C.RESET}   {clr}{' ' * max(0, pad - 3)}{C.CYAN}║{C.RESET}"

    print()
    print(f"  {C.CYAN}╔{'═' * BW}╗{C.RESET}")
    print(f"  {C.CYAN}║{' ' * BW}║{C.RESET}")
    print(bline("Nothing to Hide", f"{C.WHITE}{C.BOLD}Nothing to Hide{C.RESET}"))
    print(bline("Building Crypto from Prime Numbers", f"{C.GRAY}Building Crypto from Prime Numbers{C.RESET}"))
    print(bline("Diffie-Hellman Key Exchange + RSA from Scratch", f"{C.GRAY}Diffie-Hellman Key Exchange + RSA from Scratch{C.RESET}"))
    print(f"  {C.CYAN}║{' ' * BW}║{C.RESET}")
    print(bline("EC 441 · Mathis Souef-Myers · Spring 2026", f"{C.GRAY}EC 441 · Mathis Souef-Myers · Spring 2026{C.RESET}"))
    print(f"  {C.CYAN}║{' ' * BW}║{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * BW}╝{C.RESET}")
    print()

    print(f"  {C.WHITE}This demo walks through two foundational protocols{C.RESET}")
    print(f"  {C.WHITE}of modern cryptography, step by step, with real math.{C.RESET}")
    print()
    print(f"  {C.CYAN}[1]{C.RESET} Full demo  (DH → RSA → Text Encryption → How TLS uses both)")
    print(f"  {C.CYAN}[2]{C.RESET} Diffie-Hellman only")
    print(f"  {C.CYAN}[3]{C.RESET} RSA only")
    print(f"  {C.CYAN}[q]{C.RESET} Quit")

    try:
        choice = input(f"\n  {C.DIM}Pick [1/2/3/q]: {C.RESET}").strip().lower()
    except EOFError:
        choice = "1"

    if choice == "q":
        print(f"\n  {C.GRAY}Goodbye!{C.RESET}\n")
        return

    dh_secret = None
    pub_key = None
    priv_key = None

    if choice in ("1", "2"):
        dh_secret = diffie_hellman()

    if choice in ("1", "3"):
        pub_key, priv_key = rsa_demo()

    if choice == "1" and pub_key:
        text_encryption_demo(pub_key, priv_key)

    if choice == "1" and dh_secret and pub_key:
        connection_demo(dh_secret, pub_key)

    # Wrap up
    banner("DEMO COMPLETE")
    print(f"  {C.WHITE}Key takeaways:{C.RESET}")
    print()
    print(f"    {C.CYAN}•{C.RESET} DH uses the {C.YELLOW}Discrete Logarithm Problem{C.RESET} (hard to find exponent)")
    print(f"    {C.CYAN}•{C.RESET} RSA uses the {C.YELLOW}Integer Factorization Problem{C.RESET} (hard to factor n)")
    print(f"    {C.CYAN}•{C.RESET} Both rely on {C.YELLOW}one-way functions{C.RESET}: easy to compute, hard to invert")
    print(f"    {C.CYAN}•{C.RESET} DH provides {C.GREEN}key exchange{C.RESET}, RSA provides {C.GREEN}authentication + encryption{C.RESET}")
    print(f"    {C.CYAN}•{C.RESET} TLS uses {C.GREEN}both together{C.RESET}: RSA signs DH params, DH creates session key")
    print(f"    {C.CYAN}•{C.RESET} Symmetric ciphers (AES) do the {C.GREEN}bulk encryption{C.RESET} — asymmetric is too slow")
    print()
    print(f"  {C.GRAY}Run again with different prime sizes to see how the difficulty scales.{C.RESET}")
    print()

    try:
        again = input(f"  {C.DIM}Run again? (y/n): {C.RESET}").strip().lower()
    except EOFError:
        again = "n"
    if again in ("y", "yes"):
        main()


if __name__ == "__main__":
    main()