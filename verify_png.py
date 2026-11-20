import os
import hashlib

def verify_entry_png(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return

    size = os.path.getsize(file_path)
    if size > 1048576:
        print(f"Error: File size {size} bytes exceeds 1,048,576 bytes")
    else:
        print(f"File size: {size} bytes (OK)")

    with open(file_path, "rb") as f:
        magic = f.read(4)
        if magic != b"\x89PNG":
            print(f"Error: Invalid PNG magic bytes: {magic.hex()}")
        else:
            print(f"PNG magic bytes: OK")

        f.seek(0)
        sha256 = hashlib.sha256(f.read()).hexdigest()
        print(f"SHA256: {sha256}")

if __name__ == "__main__":
    verify_entry_png("entry.png")
