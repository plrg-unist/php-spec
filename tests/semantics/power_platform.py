"""Test-only libm identity/dispatch inspection; never computes a semantic value."""
import ctypes
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def inspect_platform():
    assert not os.environ.get("LD_PRELOAD"), "power tests forbid preload interposition"
    assert not os.environ.get("LD_AUDIT"), "power tests forbid audit interposition"
    provenance = json.loads((ROOT / 'dependencies/libm-provenance.json').read_text())
    expected = provenance['runtime']
    library = Path(expected['path']).resolve()
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    assert digest == expected['sha256'], 'power oracle libm differs from its reviewed pin'
    libm = ctypes.CDLL(str(library))
    libc = ctypes.CDLL(None)
    libc.dlvsym.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    libc.dlvsym.restype = ctypes.c_void_p
    address = libc.dlvsym(libm._handle, b'__pow_finite', b'GLIBC_2.15')
    assert address, 'pinned pow IFUNC symbol unavailable'
    selected = None
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields = line.split()
        start, end = (int(value, 16) for value in fields[0].split('-'))
        if start <= address < end:
            assert len(fields) == 6 and Path(fields[5]).resolve() == library
            selected = hex(address - start + int(fields[2], 16))
            break
    assert selected == expected['selected_elf_offset'], 'power oracle selected a different CPU implementation'
    libm.fegetround.restype = ctypes.c_int
    assert libm.fegetround() == 0, 'power tests require nearest-even floating rounding'
    return {'libm_path': str(library), 'libm_sha256': digest, 'selected_elf_offset': selected,
            'arithmetic': expected['arithmetic'], 'source_version': provenance['version']}
