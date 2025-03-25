from typing import Tuple
import random


def encode_multipart_formdata(filename: str, chunk: bytes) -> Tuple[str, bytes]:
    boundary = _generate_boundary()
    body: list[str] = []
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    body.append(b"Content-Type: application/octet-stream")
    body.append(b"")
    body.append(chunk)
    body.append(f"--{boundary}--".encode())
    body = b"\r\n".join(body)
    content_type = f"multipart/form-data; boundary={boundary}"
    return content_type, body


def _generate_boundary() -> str:
    # https://github.com/form-data/form-data/blob/v4.0.2/lib/form_data.js/#L348
    b = "--------------------------"
    for _ in range(24):
        b += str(random.randint(0, 9))
    return b
