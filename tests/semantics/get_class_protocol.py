#!/usr/bin/env python3
"""Check paused get_class selections, heap ownership and unpack prefixes."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('object-invoke', b'<?php $o=new stdClass;echo get_class($o);',
     'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*', [
         'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*',
         'pgetclasscall.SENT = [NAMED_SENT (KNOWN (POBJECT n))]',
         '$getclass_invoke_valid(S,pgetclasscall)',
         '$getclass_live_object(S,n)',
         '$call_descriptors_valid(S)',
         '~$getclass_live_object(S[.ALLOCATIONS = eps],n)',
         '~$getclass_call_valid(S[.ALLOCATIONS = eps],pgetclasscall)',
         '~$getclass_call_valid(S[.OBJECTS = eps],pgetclasscall)',
         '~$getclass_call_valid(S,pgetclasscall[.LINE = 999])',
         'S_bad = $drive(S[.TODO = (GETCLASS_INVOKE pgetclasscall[.LINE = 999]) :: ptask*],1000)',
         'S_bad.COMPLETION = UNSUPPORTED text',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         '$outputs(S_done.EVENTS) = $ptascii("stdClass")',
     ]),
    ('unpack-prefix', b'<?php $o=new stdClass;echo get_class(...["object"=>$o]);',
     'S.TODO = (GETCLASS_UNPACK_NEXT pgetclasscall poperand 0) :: ptask*', [
         'S.TODO = (GETCLASS_UNPACK_NEXT pgetclasscall poperand 0) :: ptask*',
         '$getclass_unpack_valid(S,pgetclasscall,poperand,0)',
         '$call_descriptors_valid(S)',
         '~$getclass_unpack_valid(S,pgetclasscall,poperand,2)',
         '~$getclass_unpack_valid(S[.SOURCES = eps],pgetclasscall,poperand,0)',
         '~$getclass_unpack_valid(S[.CODE = eps],pgetclasscall,poperand,0)',
         'S_bad = $drive(S[.TODO = (GETCLASS_UNPACK_NEXT pgetclasscall poperand 2) :: ptask*],1000)',
         'S_bad.COMPLETION = UNSUPPORTED text',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         '$outputs(S_done.EVENTS) = $ptascii("stdClass")',
     ]),
    ('selected-closure', b'<?php $f=get_class(...);echo $f(new stdClass);',
     'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*', [
         'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*',
         'pgetclasscall.OWNER = (n_owner)',
         '(HOBJECT n_owner) <- $task_nodes(GETCLASS_INVOKE pgetclasscall)',
         '$getclass_selected_valid(S,pgetclasscall)',
         '~$getclass_selected_valid(S,pgetclasscall[.OWNER = (999)])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         '$outputs(S_done.EVENTS) = $ptascii("stdClass")',
     ]),
    ('temporary-object', b'<?php echo get_class(new stdClass);',
     'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*', [
         'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: ptask*',
         'pgetclasscall.SENT = [NAMED_SENT (KNOWN (POBJECT n))]',
         '$getclass_live_object(S,n)',
         '$heap_valid($heap_graph(S))',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         '~((HOBJECT n) <- S_next.ALLOCATIONS)',
         '$heap_valid($heap_graph(S_next))',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         '$outputs(S_done.EVENTS) = $ptascii("stdClass")',
     ]),
]

PREFIX = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def main():
    out = Path(tempfile.mkdtemp(prefix='get-class-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    results = []
    for name, source, stage, checks in CASES:
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]'] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in conditions))
        process = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                  *modules, str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stderr[-2400:])
        results.append({'id': name, 'assertions': len(conditions),
                        'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert before == request.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'cases': results,
              'assertions': sum(row['assertions'] for row in results), 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    main()
