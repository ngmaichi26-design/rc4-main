# -*- coding: utf-8 -*-
"""
main.py - Giao dien chay thu he ma RC4 (TinyRC4 va RC4 chuan)
Nguoi lam: Mai Chi

Bang chu cai dung cho TinyRC4: A=000 B=001 C=010 D=011 E=100 F=101 G=110 H=111
Vi du trong slide: P = BAG, khoa = 2 1 3  ->  C = EBA
"""

# ---------------------------------------------------------------
# Noi cac file cua cac ban khac. Neu chua co file thi dung ban
# du phong ben duoi de main.py van chay duoc.
# Khi gop code, Duong chi can dam bao 2 ten ham nay ton tai:
#   tiny_rc4.py : tiny_rc4_crypt(bits: str, key: list[int]) -> str
#   rc4_core.py : rc4_crypt(data: bytes, key: bytes) -> bytes
# ---------------------------------------------------------------
try:
    from tiny_rc4 import tiny_rc4_crypt
except ImportError:
    def tiny_rc4_crypt(bits, key):
        n = len(key)
        S = list(range(8))
        T = [key[i % n] for i in range(8)]
        j = 0
        for i in range(8):
            j = (j + S[i] + T[i]) % 8
            S[i], S[j] = S[j], S[i]
        i = j = 0
        out = ""
        for pos in range(0, len(bits), 3):
            i = (i + 1) % 8
            j = (j + S[i]) % 8
            S[i], S[j] = S[j], S[i]
            k = S[(S[i] + S[j]) % 8]
            block = int(bits[pos:pos + 3], 2) ^ k
            out += format(block, "03b")
        return out
    print("[Luu y] Chua tim thay tiny_rc4.py -> dang dung ban du phong.")

try:
    from rc4_core import rc4_crypt
except ImportError:
    def rc4_crypt(data, key):
        S = list(range(256))
        T = [key[i % len(key)] for i in range(256)]
        j = 0
        for i in range(256):
            j = (j + S[i] + T[i]) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        out = bytearray()
        for b in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(b ^ S[(S[i] + S[j]) % 256])
        return bytes(out)
    print("[Luu y] Chua tim thay rc4_core.py -> dang dung ban du phong.")


LETTERS = "ABCDEFGH"


def text_to_bits(text):
    return "".join(format(LETTERS.index(c), "03b") for c in text)


def bits_to_text(bits):
    return "".join(LETTERS[int(bits[i:i + 3], 2)] for i in range(0, len(bits), 3))


def doc_khoa_tiny():
    while True:
        s = input("Nhap khoa (cac so 0-7 cach nhau boi dau cach, vi du: 2 1 3): ").split()
        try:
            key = [int(x) for x in s]
            if 1 <= len(key) <= 8 and all(0 <= k <= 7 for k in key):
                return key
        except ValueError:
            pass
        print("  -> Khoa sai. Phai co tu 1 den 8 so, moi so tu 0 den 7.")


def doc_van_ban_tiny(nhan):
    while True:
        s = input(nhan).strip().upper()
        if s and all(c in LETTERS for c in s):
            return s
        print("  -> Chi duoc nhap chu A-H, khong de trong.")


def chay_tiny():
    print("\n--- TinyRC4 (chu A-H, moi chu 3 bit) ---")
    print("1. Ma hoa   2. Giai ma")
    chon = input("Chon: ").strip()
    if chon not in ("1", "2"):
        print("Lua chon khong hop le.")
        return
    key = doc_khoa_tiny()
    if chon == "1":
        p = doc_van_ban_tiny("Nhap ban ro P (vi du BAG): ")
        bits = text_to_bits(p)
        c_bits = tiny_rc4_crypt(bits, key)
        print("P (bit) :", " ".join(bits[i:i + 3] for i in range(0, len(bits), 3)))
        print("C (bit) :", " ".join(c_bits[i:i + 3] for i in range(0, len(c_bits), 3)))
        print("=> Ban ma C =", bits_to_text(c_bits))
    else:
        c = doc_van_ban_tiny("Nhap ban ma C (vi du EBA): ")
        bits = text_to_bits(c)
        p_bits = tiny_rc4_crypt(bits, key)
        print("=> Ban ro P =", bits_to_text(p_bits))


def chay_rc4():
    print("\n--- RC4 chuan (van ban bat ky, khoa 1-256 byte) ---")
    print("1. Ma hoa   2. Giai ma (nhap ban ma dang hex)")
    chon = input("Chon: ").strip()
    if chon not in ("1", "2"):
        print("Lua chon khong hop le.")
        return
    khoa = input("Nhap khoa (chu bat ky): ").encode("utf-8")
    if not khoa or len(khoa) > 256:
        print("  -> Khoa phai dai tu 1 den 256 byte.")
        return
    if chon == "1":
        p = input("Nhap ban ro P: ").encode("utf-8")
        c = rc4_crypt(p, khoa)
        print("=> Ban ma C (hex) =", c.hex().upper())
    else:
        try:
            c = bytes.fromhex(input("Nhap ban ma C (hex): ").strip())
        except ValueError:
            print("  -> Chuoi hex khong hop le.")
            return
        p = rc4_crypt(c, khoa)
        print("=> Ban ro P =", p.decode("utf-8", errors="replace"))


def main():
    while True:
        print("\n========== CHUONG TRINH RC4 ==========")
        print("1. TinyRC4 (ban thu nho trong slide)")
        print("2. RC4 chuan")
        print("0. Thoat")
        chon = input("Chon: ").strip()
        if chon == "1":
            chay_tiny()
        elif chon == "2":
            chay_rc4()
        elif chon == "0":
            print("Tam biet!")
            break
        else:
            print("Lua chon khong hop le.")


if __name__ == "__main__":
    main()
