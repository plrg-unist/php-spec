#!/usr/bin/env python3
"""Synthetic ALIAS evidence coexists with a retired arrow's deferred default."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

import reference_coercion_protocol as backing
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php const K="7";class O{}class C{public O $p;}class A{public static O $p;}'
          b'$a=new O;$c=new C;$c->p=&$a;A::$p=&$a;'
          b'$f=static fn &($x=K):string=>$x;$f();$f=null;$good=new O;')


def checks(initial):
    return backing.initialized(initial) + [
        'S.DEFAULTCACHE = [pdefaultcache]',
        'S.CLOSURETEMPLATES = [pfunction]',
        'pfunction.SIGNATURE.BYREF /\\ ~pfunction.CODE.STRICT',
        '$reference_coercion_function(pfunction)',
        'pfunction.DEFAULTS = [pdefault]',
        'pdefault.KIND = PDDEFERRED',
        'pdefaultcache.ORIGIN = pdefault.ORIGIN /\\ pdefaultcache.CLASS = PVSTRING true',
        'pdefaultcache.VALUE = PSTRING ([55]) /\\ $compiled_read(S,pdefault.ORIGIN) = eps',
        'S.OBJECTS[2] = REALCLOSURE pfunction.ORIGIN pitem* pstaticcell*',
        '~((HOBJECT 2) <- S.ALLOCATIONS)',
        '$lookup(S.ENV,$ptascii("f")) = (n_f)',
        'S.STORE[n_f] = DEFINED PNULL',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (z_line)',
        '$reference_coercion_source(S,pfunction.ORIGIN,z_line)',
        '$default_caches_valid(S,S.DEFAULTCACHE) /\\ $call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        '$lookup(S.ENV,$ptascii("a")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_original)',
        'prefcoercion = {CELL n_cell,SITE pfunction.ORIGIN,LINE z_line,VALUE ([55])}',
        'S_missing = $prune_allocations(S[.STORE = $set_cell(S.STORE,n_cell,DEFINED (PSTRING ([55])))])',
        '~$property_state_valid(S_missing) /\\ ~$proprefs_valid(S_missing) /\\ ~$class_statics_valid(S_missing)',
        'S_witness = S_missing[.REFCOERCIONS = [prefcoercion]]',
        '$reference_coercions_valid(S_witness) /\\ $reference_coercion_value(S_witness,n_cell,PSTRING ([55]))',
        '$default_caches_valid(S_witness,S_witness.DEFAULTCACHE) /\\ $call_descriptors_valid(S_witness) /\\ $class_state_valid(S_witness) /\\ $heap_valid($heap_graph(S_witness))',
        'S_witness.PROPREFS = S.PROPREFS /\\ S_witness.CLASSSTATICS = S.CLASSSTATICS /\\ S_witness.DEFAULTCACHE = S.DEFAULTCACHE',
        '$machine_roots(S_witness) = $machine_roots(S_missing)',
        '~((HOBJECT n_original) <- S_witness.ALLOCATIONS) /\\ ~((HOBJECT 2) <- S_witness.ALLOCATIONS)',
        '~$default_caches_valid(S_witness[.CLOSURETEMPLATES = eps],S_witness.DEFAULTCACHE)',
        '~$call_descriptors_valid(S_witness[.CLOSURETEMPLATES = eps])',
        '~$default_caches_valid(S_witness,S_witness.DEFAULTCACHE ++ S_witness.DEFAULTCACHE)',
        'S_reject = $write_cell_checked(S_witness,n_cell,PSTRING ([55]),1)',
        'S_reject.COMPLETION = THROWN "TypeError" ptbytes_error z_error',
        'S_reject.STORE[n_cell] = S_witness.STORE[n_cell] /\\ S_reject.REFCOERCIONS = S_witness.REFCOERCIONS',
        '$default_caches_valid(S_reject,S_reject.DEFAULTCACHE) /\\ $call_descriptors_valid(S_reject) /\\ $class_state_valid(S_reject)',
        '$lookup(S.ENV,$ptascii("good")) = (n_good_cell)',
        'S.STORE[n_good_cell] = DEFINED (POBJECT n_good)',
        'S_accept = $write_cell_checked(S_witness,n_cell,POBJECT n_good,1)',
        'S_accept.COMPLETION = NORMAL /\\ S_accept.STORE[n_cell] = DEFINED (POBJECT n_good) /\\ S_accept.REFCOERCIONS = eps',
        'S_accept.PROPREFS = S_witness.PROPREFS /\\ S_accept.DEFAULTCACHE = S.DEFAULTCACHE /\\ S_accept.CLOSURETEMPLATES = S.CLOSURETEMPLATES',
        '$default_caches_valid(S_accept,S_accept.DEFAULTCACHE) /\\ $call_descriptors_valid(S_accept) /\\ $class_state_valid(S_accept) /\\ $heap_valid($heap_graph(S_accept))',
    ]


def main():
    out = Path(tempfile.mkdtemp(prefix='reference-coercion-default-cache-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), Path(backing.__file__),
                         ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'spec/semantics/modules.json',
                         ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so',
                         ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php', ROOT / '.tools/php/bin/php']
    before = {str(path.relative_to(ROOT)): backing.digest(path) for path in watched}
    path = out / 'source.php'
    path.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    initial = '$php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
    premises = checks(initial)
    fixture = out / 'default-cache-coexistence.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + premise + '\n' for premise in premises))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *map(str, modules), str(fixture)]
    started = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, timeout=180)
        stdout, stderr, code, timed_out = result.stdout, result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', None, True
    (out / 'stdout').write_bytes(stdout)
    (out / 'stderr').write_bytes(stderr)
    assert before == {str(path.relative_to(ROOT)): backing.digest(path) for path in watched}, 'inputs changed during run'
    passed = code == 0 and stdout == b'true\n' and not stderr
    report = {'result': 'timeout' if timed_out else 'pass' if passed else 'fail',
              'scope': 'Synthetic current-state/permanent-site coexistence, default-false producer; no source-native callback or historical CELL association proof.',
              'inputs': before, 'source_sha256': hashlib.sha256(SOURCE).hexdigest(),
              'fixture_sha256': backing.digest(fixture), 'assertions': len(premises), 'command': command,
              'seconds': time.monotonic() - started, 'limit_seconds': 180,
              'timeout': timed_out, 'returncode': code}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], len(premises), flush=True)
    assert passed


if __name__ == '__main__':
    main()
