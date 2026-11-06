#!/usr/bin/env python3
"""Static Producer authority across actual include and eval entries."""
from pathlib import Path

import enum_included_constant_method_cache as base

base.SOURCES = Path(__file__).resolve().with_suffix('')
base.HASHES = {
    "main.php": "a192290e67edeb7f5ec7d92576c757ff4f242791e401d46263eae25b6ca8b827",
    "cold.php": "6d08b0cf57fb6d27e48696fbc160562e59b2c901abc96310d941e78a17136380",
    "warm-eval.txt": "b4511b8390a323362f4c7e6ea8e7a46d05391e060e327df083a5cb09e96e2910"
}
base.EXPECTED = (
    b'cold-scope:StaticProducerMethodCache146\\Producer:StaticProducerMethodCache146\\ChildProducer:no-this|'
    b'cold-ready|'
    b'raw|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'warm-scope:StaticProducerMethodCache146\\Producer:StaticProducerMethodCache146\\ChildProducer:no-this|'
    b'warm-ready|'
    b'static-returned|'
    b'cold|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'private-copy|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'cold-again|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'warm|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'fresh|'
    b'USER:OLD|'
    b'query:0:OLD|'
    b'shared-copy|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'retire|'
    b'held|'
    b'query:1:StaticProducerMethodCache146\\Target::cases|'
    b'source-gone|'
    b'fresh-gone|'
    b'shared-gone|'
    b'done|'
)


if __name__ == '__main__':
    raise SystemExit(0 if base.main(extra_inputs=(Path(__file__),), included_files=('cold.php',)) else 1)
