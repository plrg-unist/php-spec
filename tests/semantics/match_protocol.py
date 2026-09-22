#!/usr/bin/env python3
"""Match source continuations, ownership, malformed tasks and budget resumption."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [('subject',
  b'<?php $x=2;echo match($x){1=>"X",2=>"Y"};',
  'S.TODO = (MATCH_START porigin) :: ptask*',
  ['S.TODO = (MATCH_START porigin) :: ptask*',
   '$call_task_valid(S, MATCH_START porigin)',
   '~$call_task_valid(S, MATCH_START (PORIGIN 99 eps))',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [89]']),
 ('condition-owner',
  b'<?php echo match([1]){[0]=>"X",[1]=>"Y"};',
  'S.TODO = (MATCH_COMPARE porigin poperand n_arm n_cond) :: ptask*',
  ['S.TODO = (MATCH_COMPARE porigin poperand n_arm n_cond) :: ptask*',
   'poperand = KNOWN (PARRAY n_array)',
   '$($heap_owners($heap_graph(S),HARRAY n_array) > 0)',
   '$call_task_valid(S, MATCH_COMPARE porigin poperand n_arm n_cond)',
   '~$call_task_valid(S, MATCH_COMPARE porigin poperand 99 n_cond)',
   '~$call_task_valid(S, MATCH_COMPARE porigin poperand n_arm 99)',
   '~$call_task_valid(S[.ORIGIN = eps], MATCH_COMPARE porigin poperand n_arm n_cond)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [89]']),
 ('selected-body-owner',
  b'<?php class C{} function subject(){return new C;}function body(){echo "B";return "Y";}echo m'
  b'atch(subject()){default=>body()};',
  'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("body")',
  ['S.CURRENT = (pcallcontext)',
   'S.OBJECTPROPS = [pobjectprops]',
   '$($heap_owners($heap_graph(S),HOBJECT pobjectprops.OBJECT) > 0)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [66,89]',
   '$heap_owners($heap_graph(S_done),HOBJECT pobjectprops.OBJECT) = 0',
   'S_done.OBJECTPROPS = eps']),
 ('condition-call-owner',
  b'<?php class C{}function subject(){return new C;}function cond(){echo "C";return 0;}echo matc'
  b'h(subject()){cond()=>"X",default=>"Y"};',
  'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("cond")',
  ['S.CURRENT = (pcallcontext)',
   'S.OBJECTPROPS = [pobjectprops]',
   '$($heap_owners($heap_graph(S),HOBJECT pobjectprops.OBJECT) > 0)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [67,89]',
   'S_done.OBJECTPROPS = eps']),
 ('result-copy',
  b'<?php $x=[1];$y=match(1){1=>$x};$y[0]=2;echo $x[0],$y[0];',
  'S.TODO = (MATCH_RESULT porigin poperand n_arm) :: ptask*',
  ['S.TODO = (MATCH_RESULT porigin poperand n_arm) :: ptask*',
   '$call_task_valid(S, MATCH_RESULT porigin poperand n_arm)',
   '~$call_task_valid(S, MATCH_RESULT porigin poperand 99)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [49,50]']),
 ('nested-scan',
  b'<?php echo match(2){1=>"X",2=>match(3){1=>"X",3=>"Y"}};',
  'S.TODO = (MATCH_SCAN porigin poperand n_arm n_cond) :: ptask*',
  ['S.TODO = (MATCH_SCAN porigin poperand n_arm n_cond) :: ptask*',
   '$call_task_valid(S, MATCH_SCAN porigin poperand n_arm n_cond)',
   '~$call_task_valid(S, MATCH_SCAN porigin poperand 99 n_cond)',
   '~$call_task_valid(S, MATCH_SCAN porigin poperand n_arm 99)',
   '~$call_task_valid(S, MATCH_SCAN porigin (KNOWN (PINT 999)) n_arm n_cond)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [89]']),
 ('abrupt-owner',
  b'<?php class C{}function subject(){return new C;}echo match(subject()){default=>MISSING};',
  'S.TODO = (MATCH_SCAN porigin poperand n_arm n_cond) :: ptask*',
  ['$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = PHPERROR $ptascii("MISSING") 1',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.OBJECTPROPS = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('cv-capture',
  b'<?php $x=2;echo match($x){1=>"X",2=>"Y"};',
  'S.TODO = (MATCH_SCAN porigin poperand n_arm n_cond) :: ptask*',
  ['S.TODO = (MATCH_SCAN porigin poperand n_arm n_cond) :: ptask*',
   '~$call_task_valid(S, MATCH_SCAN porigin (VARIABLE $ptascii("bad") 1) n_arm n_cond)',
   '~$call_task_valid(S, MATCH_SCAN porigin (VARIABLE $ptascii("x") 99) n_arm n_cond)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [89]'])]

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
    out = Path(tempfile.mkdtemp(prefix='match-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
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
        results.append({'name': name, 'assertions': len(conditions),
                        'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert before == request.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'assertions': sum(r['assertions'] for r in results),
              'cases': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    main()
