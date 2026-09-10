import hashlib

# Calculates the SHA-256 checksum of the file.
def calculate_checksum(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()