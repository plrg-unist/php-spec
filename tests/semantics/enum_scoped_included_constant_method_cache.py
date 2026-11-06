#!/usr/bin/env python3
"""Inherited class-scoped include captures without a retained Producer receiver."""
from pathlib import Path

import enum_included_constant_method_cache as base

base.SOURCES = Path(__file__).resolve().with_suffix('')
base.HASHES = {
    "main.php": "3001035e518352e8f601bb343fcfc2dac697dd77b442dbf203d4b58196c0933f",
    "cold.php": "2d8c02cdb7504a4064dfbcdaef4541e15676e4d372d4ac8e24c9be57c59fa0bc",
    "warm.php": "15b973ae98e2201e4e6d9cc8460c2b34b62b3f1850c022ebeb2d3587b671f684"
}
base.EXPECTED = (
    b'cold-scope:ScopedIncludedMethodCache144\\Producer:ScopedIncludedMethodCache144\\ChildProducer|'
    b'cold-ready|'
    b'raw|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'warm-scope:ScopedIncludedMethodCache144\\Producer:ScopedIncludedMethodCache144\\ChildProducer|'
    b'warm-ready|'
    b'producer-gone|'
    b'cold|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'private-copy|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'cold-again|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'warm|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'fresh|'
    b'USER:OLD|'
    b'query:0:OLD|'
    b'shared-copy|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'retire|'
    b'held|'
    b'query:1:ScopedIncludedMethodCache144\\Target::cases|'
    b'source-gone|'
    b'fresh-gone|'
    b'shared-gone|'
    b'done|'
)


if __name__ == '__main__':
    raise SystemExit(0 if base.main(extra_inputs=(Path(__file__),)) else 1)
