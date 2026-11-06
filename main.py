# -*- coding: utf-8 -*-
"""
main.py - Giao diện chạy thử hệ mã RC4 (TinyRC4 và RC4 chuẩn)
Người làm: Mai Chi

Cách chạy:  python main.py

Chức năng:
  1. TinyRC4: nhập chữ A-H và khóa (các số 0-7) -> mã hóa / giải mã
  2. RC4 chuẩn: nhập văn bản (UTF-8) và khóa -> mã hóa / giải mã (hex)
  3. Mã hóa tệp (mặc định demo_tap_tin.txt)
  4. Giải mã tệp và so với tệp gốc
  5. Demo nhanh: chạy các ca mẫu của nhóm, tự tính rồi so với đáp án

Bảng chữ cái cho TinyRC4: A=000 B=001 C=010 D=011 E=100 F=101 G=110 H=111
Ví dụ của nhóm: P = FACE, khóa = 3 1 4  ->  C = BACE
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------
# Nối với code của các bạn khác. Nếu chưa có file thì dùng bản dự
# phòng bên dưới để main.py vẫn chạy được.
# Khi gộp code, chỉ cần 2 tên hàm này tồn tại:
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
            out += format(int(bits[pos:pos + 3], 2) ^ k, "03b")
        return out
    print("[Lưu ý] Chưa tìm thấy tiny_rc4.py -> đang dùng bản dự phòng.")

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
    print("[Lưu ý] Chưa tìm thấy rc4_core.py -> đang dùng bản dự phòng.")


LETTERS = "ABCDEFGH"
TEP_MAC_DINH = "demo_tap_tin.txt"

# Ca mẫu của nhóm (đáp án lấy từ tinyrc4_test_cases.csv và rc4_text_cases.csv).
# Demo nhanh sẽ TỰ TÍNH rồi so với đáp án, không in đáp án có sẵn.
TINY_DEMO = [
    ("FACE", [3, 1, 4], "BACE"),
    ("CAB", [5, 2, 0, 7], "GFA"),
    ("BEEF", [6, 4, 1], "HBBB"),
    ("CAFE", [1, 6, 2, 5], "EBCA"),
]
RC4_DEMO = [
    ("thay Thai dep trai", "ATBMTT-2026", "ac5aee741f4d5ffbafecc15c82d7d530ab70"),
    ("cho tui em 10 diem", "RC4-10DIEM", "87ff0171e60b58b1ffb1aa3633b07450adca"),
    ("ATBMTT", "Nhom4-KSA", "49ca668b8fe4"),
    ("Chúc thầy Thái một ngày vui!", "Vietnam-UTF8",
     "4df3df377f5f81981ae93994a8d08dce5961ac0dd2183a4b6a32a0c0375492c6f14c2f"),
]


# ------------------------- Hàm phụ -------------------------
def text_to_bits(text):
    return "".join(format(LETTERS.index(c), "03b") for c in text)


def bits_to_text(bits):
    return "".join(LETTERS[int(bits[i:i + 3], 2)] for i in range(0, len(bits), 3))


def nhom_bit(bits):
    return " ".join(bits[i:i + 3] for i in range(0, len(bits), 3))


def doc_khoa_tiny():
    while True:
        s = input("Nhập khóa (các số 0-7 cách nhau bởi dấu cách, ví dụ: 3 1 4): ").split()
        try:
            key = [int(x) for x in s]
            if 1 <= len(key) <= 8 and all(0 <= k <= 7 for k in key):
                return key
        except ValueError:
            pass
        print("  -> Khóa sai. Phải có từ 1 đến 8 số, mỗi số từ 0 đến 7.")


def doc_chu_tiny(nhan):
    while True:
        s = input(nhan).strip().upper()
        if s and all(c in LETTERS for c in s):
            return s
        print("  -> Chỉ được nhập chữ A-H, không để trống.")


def doc_khoa_rc4():
    while True:
        khoa = input("Nhập khóa (chữ bất kỳ, 1-256 byte): ").encode("utf-8")
        if 1 <= len(khoa) <= 256:
            return khoa
        print("  -> Khóa phải dài từ 1 đến 256 byte.")


def doc_duong_dan(nhan, mac_dinh):
    s = input(f"{nhan} [Enter = {mac_dinh}]: ").strip().strip('"')
    return s or mac_dinh


# ------------------------- Chức năng -------------------------
def chay_tiny():
    print("\n--- TinyRC4 (chữ A-H, mỗi chữ 3 bit) ---")
    print("1. Mã hóa   2. Giải mã")
    chon = input("Chọn: ").strip()
    if chon not in ("1", "2"):
        print("Lựa chọn không hợp lệ.")
        return
    key = doc_khoa_tiny()
    if chon == "1":
        p = doc_chu_tiny("Nhập bản rõ P (ví dụ FACE): ")
        bits = text_to_bits(p)
        c_bits = tiny_rc4_crypt(bits, key)
        print("P (bit) :", nhom_bit(bits))
        print("C (bit) :", nhom_bit(c_bits))
        print("=> Bản mã C =", bits_to_text(c_bits))
    else:
        c = doc_chu_tiny("Nhập bản mã C (ví dụ BACE): ")
        bits = text_to_bits(c)
        p_bits = tiny_rc4_crypt(bits, key)
        print("=> Bản rõ P =", bits_to_text(p_bits))


def chay_rc4():
    print("\n--- RC4 chuẩn (văn bản UTF-8, khóa 1-256 byte) ---")
    print("1. Mã hóa   2. Giải mã (nhập bản mã dạng hex)")
    chon = input("Chọn: ").strip()
    if chon not in ("1", "2"):
        print("Lựa chọn không hợp lệ.")
        return
    khoa = doc_khoa_rc4()
    if chon == "1":
        p = input("Nhập bản rõ P: ").encode("utf-8")
        c = rc4_crypt(p, khoa)
        print("=> Bản mã C (hex) =", c.hex())
    else:
        try:
            c = bytes.fromhex(input("Nhập bản mã C (hex): ").strip())
        except ValueError:
            print("  -> Chuỗi hex không hợp lệ.")
            return
        p = rc4_crypt(c, khoa)
        print("=> Bản rõ P =", p.decode("utf-8", errors="replace"))


def ma_hoa_tep():
    print("\n--- Mã hóa tệp bằng RC4 ---")
    duong_dan = doc_duong_dan("Tệp cần mã hóa", TEP_MAC_DINH)
    if not os.path.isfile(duong_dan):
        print(f"  -> Không tìm thấy tệp '{duong_dan}'. Hãy để tệp cùng thư mục với main.py.")
        return
    khoa = doc_khoa_rc4()
    try:
        with open(duong_dan, "rb") as f:
            du_lieu = f.read()
        ban_ma = rc4_crypt(du_lieu, khoa)
        dau_ra = duong_dan + ".enc"
        with open(dau_ra, "wb") as f:
            f.write(ban_ma)
    except OSError as e:
        print("  -> Lỗi đọc/ghi tệp:", e)
        return
    print(f"Đã mã hóa {len(du_lieu)} byte -> ghi ra '{dau_ra}'")
    print("16 byte đầu của bản mã (hex):", ban_ma[:16].hex())


def giai_ma_tep():
    print("\n--- Giải mã tệp bằng RC4 ---")
    duong_dan = doc_duong_dan("Tệp cần giải mã", TEP_MAC_DINH + ".enc")
    if not os.path.isfile(duong_dan):
        print(f"  -> Không tìm thấy tệp '{duong_dan}'. Hãy mã hóa tệp trước (chọn 3).")
        return
    khoa = doc_khoa_rc4()
    goc = duong_dan[:-4] if duong_dan.lower().endswith(".enc") else duong_dan
    ten, duoi = os.path.splitext(goc)
    dau_ra = ten + "_giai_ma" + (duoi or ".txt")
    try:
        with open(duong_dan, "rb") as f:
            ban_ma = f.read()
        ban_ro = rc4_crypt(ban_ma, khoa)
        with open(dau_ra, "wb") as f:
            f.write(ban_ro)
    except OSError as e:
        print("  -> Lỗi đọc/ghi tệp:", e)
        return
    print(f"Đã giải mã {len(ban_ma)} byte -> ghi ra '{dau_ra}'")
    print("Xem trước 3 dòng đầu:")
    for dong in ban_ro.decode("utf-8", errors="replace").splitlines()[:3]:
        print("   ", dong)
    if os.path.isfile(goc):
        with open(goc, "rb") as f:
            giong = f.read() == ban_ro
        print("=> KHỚP với tệp gốc." if giong else "=> KHÔNG khớp tệp gốc (sai khóa?).")


def demo_nhanh():
    print("\n--- Demo nhanh: tự tính rồi so với đáp án của nhóm ---")
    dat = 0
    tong = 0
    print("TinyRC4:")
    for p, key, mong_doi in TINY_DEMO:
        c = bits_to_text(tiny_rc4_crypt(text_to_bits(p), key))
        lai = bits_to_text(tiny_rc4_crypt(text_to_bits(c), key))
        ok = (c == mong_doi and lai == p)
        tong += 1
        dat += ok
        print(f"  P={p:<5} khóa={' '.join(map(str, key)):<8} C={c:<5} giải mã={lai:<5} "
              f"{'PASS' if ok else 'FAIL (đáp án ' + mong_doi + ')'}")
    print("RC4 chuẩn:")
    for p, khoa, mong_doi in RC4_DEMO:
        c = rc4_crypt(p.encode("utf-8"), khoa.encode("utf-8"))
        lai = rc4_crypt(c, khoa.encode("utf-8")).decode("utf-8", errors="replace")
        ok = (c.hex() == mong_doi and lai == p)
        tong += 1
        dat += ok
        print(f"  P='{p}' khóa={khoa}")
        print(f"     C(hex)={c.hex()}")
        print(f"     giải mã='{lai}' -> {'PASS' if ok else 'FAIL'}")
    print(f"Kết quả: {dat}/{tong} ca đạt.")


def main():
    while True:
        print("\n========== CHƯƠNG TRÌNH RC4 ==========")
        print("1. TinyRC4 (nhập chữ A-H, khóa là các số)")
        print("2. RC4 chuẩn (nhập văn bản)")
        print("3. Mã hóa tệp")
        print("4. Giải mã tệp")
        print("5. Demo nhanh (ca mẫu của nhóm)")
        print("0. Thoát")
        chon = input("Chọn: ").strip()
        if chon == "1":
            chay_tiny()
        elif chon == "2":
            chay_rc4()
        elif chon == "3":
            ma_hoa_tep()
        elif chon == "4":
            giai_ma_tep()
        elif chon == "5":
            demo_nhanh()
        elif chon == "0":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã thoát.")
