#!/usr/bin/env python3
"""Genuine list targets preserve nested arrays until compiler visitation."""
import base64, hashlib, json, os, subprocess, tempfile
from pathlib import Path
from validate import ROOT, Worker, require, normalize, structurally_equal, implementation_fingerprint

ARCHIVE = ROOT/'coverage/semantics/destructuring-list-target-originals.json'

def fingerprint():
    return {'implementation': implementation_fingerprint(),
            'originals_sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}

def diagnostics(result):
    prefixes = (b'Fatal error:', b'Parse error:', b'Warning:', b'Deprecated:')
    return [line.split(b' in ', 1)[0] for line in result.stderr.splitlines() if line.startswith(prefixes)]

def main():
    before = fingerprint()
    rows = json.loads(ARCHIVE.read_text())
    if isinstance(rows, dict): rows = rows['cases']
    profile = json.loads((ROOT/'tests/semantics/profile.json').read_text())
    flags = [flag for key, value in profile.items() for flag in ['-d', key+'='+value]]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)])
    observations = []
    try:
        with tempfile.TemporaryDirectory(prefix='php-list-targets-') as directory:
            original_path = Path(directory)/'original.php'
            printed_path = Path(directory)/'printed.php'
            for encoding in ['plain', 'UTF-16BE']:
                extra = [] if encoding == 'plain' else ['-d', 'zend.multibyte=1', '-d', 'internal_encoding=UTF-8']
                frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *flags, *extra, str(ROOT/'frontend/worker.php')])
                try:
                    for row in rows:
                        source = base64.b64decode(row['source_base64'])
                        code = source if encoding == 'plain' else b'\xfe\xff'+source.decode().encode('utf-16be')
                        parsed = require(frontend.call(op='parse', source=base64.b64encode(code).decode()), 'parse')
                        assert parsed['accepted'], (row['id'], parsed)
                        checked = require(adapter.call(op='elaborate', ast=parsed['ast'], fixture=True), 'check')
                        assert checked['ast'] == parsed['ast']
                        printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
                        assert printed['ast'] == checked['ast']
                        reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
                        assert reparsed['accepted'] and structurally_equal(normalize(parsed['ast']), normalize(reparsed['ast']))
                        original_path.write_bytes(code)
                        printed_path.write_bytes(base64.b64decode(printed['source']))
                        command = [str(ROOT/'.tools/php/bin/php'), '-n', *flags, *extra, '-l']
                        original = subprocess.run(command+[str(original_path)], capture_output=True, env=env, cwd=ROOT, timeout=10)
                        fresh = subprocess.run(command+[str(printed_path)], capture_output=True, env=env, cwd=ROOT, timeout=10)
                        assert (original.returncode, diagnostics(original)) == (fresh.returncode, diagnostics(fresh)), (row['id'], original, fresh)
                        observations.append({'id': row['id'], 'encoding': encoding,
                            'source_base64': base64.b64encode(code).decode(),
                            'checked_ast_sha256': hashlib.sha256(json.dumps(checked['ast'], sort_keys=True).encode()).hexdigest(),
                            'printed_source': printed['source'], 'native_status': original.returncode,
                            'native_stderr': base64.b64encode(original.stderr).decode(),
                            'printed_native_stderr': base64.b64encode(fresh.stderr).decode()})
                finally: frontend.close()
    finally: adapter.close()
    assert before == fingerprint(), 'list-target inputs changed'
    report = {'fingerprint': before, 'scope': 'checked syntax and fresh printing preserve original native diagnostic families; reached destructuring semantics remain pending',
              'profiles': len(observations), 'cases': observations}
    (ROOT/'coverage/semantics/list-target-metadata.json').write_text(json.dumps(report, indent=2)+'\n')
    print(len(observations), 'list-target checked/printer/native phase profiles passed')

if __name__ == '__main__': main()
