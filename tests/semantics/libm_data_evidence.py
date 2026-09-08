#!/usr/bin/env python3
"""Compare imported power constants with pinned ELF bytes; no math execution."""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]


def main():
    provenance = ROOT / 'dependencies/libm-provenance.json'
    expected = json.loads(provenance.read_text())['runtime']
    library = Path(expected['path'])
    data = ROOT / 'spec/semantics/08-libm-data.watsup'
    watched = [provenance, library, data, Path(__file__)]
    def fingerprints():
        return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):
                hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    assert before[str(library)] == expected['sha256'], 'different runtime library'
    binary, dsl = library.read_bytes(), data.read_text()
    checked = 0
    # ELF offsets follow the retained disassembly's data references and the
    # imported math_config.h struct layout, independently of the generator.
    fields = {'ln2hi': 0xb6b80, 'ln2lo': 0xb6b88, 'invln2N': 0xb4980,
              'shift': 0xb4988, 'negln2hiN': 0xb4990, 'negln2loN': 0xb4998}
    for name, offset in fields.items():
        value = int(re.search(r'def \$pow_' + name + r'\(\) = (\d+)', dsl)[1])
        assert struct.unpack_from('<Q', binary, offset)[0] == value, name
        checked += 1
    tables = [('log_coeff', 0xb6b90, 8, [0], 7),
              ('exp_coeff', 0xb49a0, 8, [0], 4),
              ('log_table', 0xb6bc8, 32, [0, 16, 24], 128),
              ('exp_table', 0xb4a30, 16, [0, 8], 128)]
    for name, offset, stride, positions, count in tables:
        rows = list(re.finditer(r'def \$pow_' + name + r'\((\d+)\) = (.+)', dsl))
        assert [int(row[1]) for row in rows] == list(range(count)), name
        for row in rows:
            values = [int(value) for value in re.findall(r'\d+', row[2])]
            assert len(values) == len(positions), name
            for value, position in zip(values, positions):
                actual = struct.unpack_from('<Q', binary, offset + int(row[1]) * stride + position)[0]
                assert actual == value, (name, row[1], position)
                checked += 1
    assert checked == 657
    assert before == fingerprints(), 'power evidence inputs changed'
    report = {'scope': 'independent source-table to pinned runtime ELF equality; no PHP evaluation',
              'binary64_words': checked, 'result': 'pass', 'fingerprints': before}
    (ROOT / 'coverage/semantics/libm-data.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'{checked} generated binary64 words match the pinned runtime ELF')


if __name__ == '__main__':
    main()
