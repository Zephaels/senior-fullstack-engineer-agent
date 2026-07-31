#!/usr/bin/env python3
"""Canonical file bytes used by manifests and reproducible release archives."""

from pathlib import Path


def canonical_bytes(path: Path) -> bytes:
    """Return platform-independent bytes for release hashing and packaging.

    Git may check text files out with CRLF on Windows and LF on Linux. Release
    identities must not change solely because the build host uses a different
    line-ending convention. UTF-8 text is therefore normalized to LF, while
    non-UTF-8/binary content is preserved byte-for-byte.
    """

    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
