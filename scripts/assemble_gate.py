#!/usr/bin/env python3
"""Compile supplemental smali via Apktool's pinned SmaliBuilder API.

The bundled smali Main has no CLI main method, and jdk4py is a runtime rather
than a compiler. Generate a tiny Java-5 classfile bridge to the existing API;
no compiler downloads or npm lifecycle scripts are needed.
"""
import argparse
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_bridge() -> bytes:
    pool = []

    def entry(value):
        pool.append(value)
        return len(pool)

    def utf(value):
        contents = value.encode("utf-8")
        return entry(b"\x01" + struct.pack(">H", len(contents)) + contents)

    def cls(value):
        return entry(b"\x07" + struct.pack(">H", utf(value)))

    def method(owner, name, descriptor):
        name_type = entry(b"\x0c" + struct.pack(">HH", utf(name), utf(descriptor)))
        return entry(b"\x0a" + struct.pack(">HH", owner, name_type))

    bridge = cls("ShadowSmaliCompile")
    object_class = cls("java/lang/Object")
    ext_file = cls("brut/directory/ExtFile")
    ext_ctor = method(ext_file, "<init>", "(Ljava/lang/String;)V")
    file_class = cls("java/io/File")
    file_ctor = method(file_class, "<init>", "(Ljava/lang/String;)V")
    builder = cls("brut/androlib/src/SmaliBuilder")
    build = method(builder, "build", "(Lbrut/directory/ExtFile;Ljava/io/File;I)V")
    main = utf("main")
    descriptor = utf("([Ljava/lang/String;)V")
    code_name = utf("Code")
    # new ExtFile(args[0]); new File(args[1]); SmaliBuilder.build(dir,out,24)
    code = (b"\xbb" + struct.pack(">H", ext_file) + b"\x59\x2a\x03\x32\xb7" + struct.pack(">H", ext_ctor)
            + b"\xbb" + struct.pack(">H", file_class) + b"\x59\x2a\x04\x32\xb7" + struct.pack(">H", file_ctor)
            + b"\x10\x18\xb8" + struct.pack(">H", build) + b"\xb1")
    code_attribute = struct.pack(">HHI", 5, 1, len(code)) + code + struct.pack(">HH", 0, 0)
    return (b"\xca\xfe\xba\xbe" + struct.pack(">HHH", 0, 49, len(pool) + 1) + b"".join(pool)
            + struct.pack(">HHHHHH", 0x21, bridge, object_class, 0, 0, 1)
            + struct.pack(">HHHHHI", 0x09, main, descriptor, 1, code_name, len(code_attribute))
            + code_attribute + struct.pack(">H", 0))


def assemble(java: str, source: Path, output: Path) -> None:
    bridge = ROOT / ".tools/android/ShadowSmaliCompile.class"
    bridge.write_bytes(make_bridge())
    output.parent.mkdir(parents=True, exist_ok=True)
    classpath = str(bridge.parent) + ":" + str(ROOT / ".tools/android/apktool.jar")
    subprocess.run([java, "-cp", classpath, "ShadowSmaliCompile", str(source), str(output)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", required=True)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    assemble(args.java, args.source, args.output)


if __name__ == "__main__":
    main()
