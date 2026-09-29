#!/usr/bin/env python3
"""Check source Throwable instance slots and live trace ownership."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
from throwable_protocol import PREFIX

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b'<?php class Child extends ErrorException { private $trace="shadow"; public $x=3; } $e=new Child; echo get_class($e);'
STAGE = 'S.RESULT = KNOWN (POBJECT n)'
CHECKS = [
    'S.OBJECTS[n] = INSTANCE porigin',
    '$class_throwable_kind(S,porigin,|S.CLASSES|) = ("ErrorException")',
    '$throwable_member(S,n)',
    '$objectprops_record_at(S.OBJECTPROPS,n) = (pobjectprops)',
    'pobjectprops.SLOTS = [ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous,ppropertyslot_severity,ppropertyslot_shadow,ppropertyslot_x]',
    'ppropertyslot_trace.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("trace"))',
    'ppropertyslot_trace.STATE = PROP_VALUE (DIRECT (PARRAY n_trace))',
    '$trace_graph_valid(S,n_trace)',
    'ppropertyslot_severity.DECL = (INTERNAL_PROPERTY "ErrorException" $ptascii("severity"))',
    'ppropertyslot_shadow.DECL = (porigin_shadow)',
    'ppropertyslot_shadow.NAME = [0] ++ $ptascii("Child") ++ [0] ++ $ptascii("trace")',
    'ppropertyslot_x.NAME = $ptascii("x")',
    '$property_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n,[ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace[.DECL = (INTERNAL_PROPERTY "Error" $ptascii("trace"))],ppropertyslot_previous,ppropertyslot_severity,ppropertyslot_shadow,ppropertyslot_x])])',
    '~$class_links_valid(S[.LINKEDPARENTS = eps])',
    'S_done = $drive(S,1000)',
    'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("Child")',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = modules + [ROOT / 'spec/semantics/modules.json', Path(__file__),
                        ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
                        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
                        ROOT / 'tests/semantics/profile.json', ROOT / '_build/default/adapter/main.exe',
                        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    out = Path(tempfile.mkdtemp(prefix='throwable-subclass-storage-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(SOURCE)
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
    initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')'
    conditions = ['S_initial = ' + initial,
                  'S = $seek(S_initial[.COMPLETION = NORMAL],1000)[.COMPLETION = NORMAL]',
                  STAGE] + CHECKS
    fixture = out / 'protocol.watsup'
    fixture.write_text(PREFIX.replace('STAGE', STAGE) + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + condition + '\n' for condition in conditions))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=300)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in inputs}, 'inputs changed'
    report = {'result': 'pass' if passed else 'fail', 'inputs': before,
              'source_sha256': digest(source), 'fixture_sha256': digest(fixture),
              'assertions': len(conditions)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], result.stderr[:1000])
    assert passed


if __name__ == '__main__':
    main()
