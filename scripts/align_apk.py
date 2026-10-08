#!/usr/bin/env python3
"""Align uncompressed APK entries before signing (16 KiB for native libraries)."""
from __future__ import annotations

import argparse
import struct
import zipfile
from pathlib import Path

ALIGNMENT_EXTRA_ID = 0xD935


def without_alignment_extra(extra: bytes) -> bytes:
    result = bytearray()
    offset = 0
    while offset < len(extra):
        if offset + 4 > len(extra):
            raise ValueError("Malformed ZIP extra field")
        kind, size = struct.unpack_from("<HH", extra, offset)
        end = offset + 4 + size
        if end > len(extra):
            raise ValueError("Malformed ZIP extra field length")
        if kind != ALIGNMENT_EXTRA_ID:
            result.extend(extra[offset:end])
        offset = end
    return bytes(result)


def data_offset(apk: Path, entry: zipfile.ZipInfo) -> int:
    with apk.open("rb") as file:
        file.seek(entry.header_offset)
        header = file.read(30)
    if len(header) != 30 or header[:4] != b"PK\x03\x04":
        raise ValueError("Invalid ZIP local header")
    filename_size, extra_size = struct.unpack_from("<HH", header, 26)
    return entry.header_offset + 30 + filename_size + extra_size


def check_alignment(apk: Path) -> dict[str, int]:
    offsets = {}
    with zipfile.ZipFile(apk) as archive:
        for info in archive.infolist():
            if info.compress_type != zipfile.ZIP_STORED or info.is_dir():
                continue
            alignment = 16384 if info.filename.endswith(".so") else 4
            offset = data_offset(apk, info)
            if offset % alignment:
                raise ValueError(f"{info.filename} is not {alignment}-byte aligned")
            if info.filename.endswith(".so") or info.filename == "resources.arsc":
                offsets[info.filename] = offset
    return offsets


def align_apk(source: Path, destination: Path) -> dict[str, int]:
    if source.resolve() == destination.resolve():
        raise ValueError("Never align an APK in place")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination, "w") as result:
        result.comment = original.comment
        for entry in original.infolist():
            # Apktool normally drops these; do not carry any stale JAR signatures.
            if entry.filename.startswith("META-INF/") and (
                entry.filename.upper().endswith((".RSA", ".DSA", ".EC", ".SF"))
                or entry.filename.upper() == "META-INF/MANIFEST.MF"
            ):
                continue
            extra = without_alignment_extra(entry.extra)
            entry.extra = extra
            if entry.compress_type == zipfile.ZIP_STORED and not entry.is_dir():
                alignment = 16384 if entry.filename.endswith(".so") else 4
                # zipfile writes ASCII names as ASCII and all other names as UTF-8.
                # ASCII has the same byte length under UTF-8.
                name_size = len(entry.filename.encode("utf-8"))
                position = result.fp.tell()
                current_offset = position + 30 + name_size + len(extra)
                if current_offset % alignment:
                    # Android's alignment extra field contains uint16 alignment
                    # followed by padding. There is no change to entry contents.
                    padding = -(current_offset + 6) % alignment
                    entry.extra += struct.pack("<HHH", ALIGNMENT_EXTRA_ID, 2 + padding, alignment)
                    entry.extra += b"\0" * padding
            result.writestr(entry, original.read(entry.filename))
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination) as result:
        for entry in result.infolist():
            if original.read(entry.filename) != result.read(entry.filename):
                raise ValueError(f"Entry contents changed while aligning: {entry.filename}")
    return check_alignment(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    for name, offset in align_apk(args.source, args.destination).items():
        print(f"Aligned: {name} (data offset {offset})")


if __name__ == "__main__":
    main()
