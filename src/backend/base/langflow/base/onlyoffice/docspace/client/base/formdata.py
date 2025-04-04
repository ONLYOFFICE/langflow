import random


def encode_multipart_formdata(filename: str, chunk: bytes) -> tuple[str, bytes]:
    boundary = _generate_boundary()
    ls: list[bytes] = []
    ls.append(f"--{boundary}".encode())
    ls.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    ls.append(b"Content-Type: application/octet-stream")
    ls.append(b"")
    ls.append(chunk)
    ls.append(f"--{boundary}--".encode())
    body = b"\r\n".join(ls)
    content_type = f"multipart/form-data; boundary={boundary}"
    return content_type, body


def _generate_boundary() -> str:
    # https://github.com/form-data/form-data/blob/v4.0.2/lib/form_data.js/#L348
    b = "--------------------------"
    for _ in range(24):
        b += str(random.randint(0, 9))  # noqa: S311
    return b
