#!/usr/bin/env python3
"""Paused switch source, ownership, comparison, and boolean-branch guards."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import request_environment as request
from recorded_worker import Worker

SOURCES = {
    'normal': '''<?php
function target() { return 7; }
function keep($x) { return $x; }
$g = target(...);
switch (keep($g)) {
 case null: echo 'X'; break;
 default: $g = null; echo 'A'; echo target();
}
''',
    'abrupt': '''<?php
function target() { return 7; }
function keep($x) { return $x; }
$g = target(...);
switch (keep($g)) {
 case null: echo 'X'; break;
 default: $g = null; echo 'A'; missing_switch();
}
''',
    'bool': "<?php\nfunction value(){return NAN;}\nswitch (1 === 1) {case value(): echo 'A'; break;}\n",
}
PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true -- if S.TODO = (SWITCH_START statement porigin) :: ptask*
def $review_stage(S, 1) = true -- if S.TODO = (SWITCH_SCAN statement porigin poperand n) :: ptask*
def $review_stage(S, 2) = true -- if S.TODO = (SWITCH_COMPARE statement porigin poperand n z) :: ptask*
def $review_stage(S, 3) = true -- if S.TODO = (SWITCH_NEXT statement porigin poperand) :: ptask*
def $review_stage(S, n) = false -- otherwise
dec $review_seek(pstate, nat, nat) : pstate
def $review_seek(S, n_stage, n_left) = S -- if $review_stage(S, n_stage)
def $review_seek(S, n_stage, n_left) = $review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, n_rest)
  -- if ~$review_stage(S, n_stage)
  -- if $(n_left > 0)
  -- if n_rest = $(n_left - 1)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
dec $forge_compare_match(pcodeexpr, pcpath) : bool
def $forge_compare_match(CODESWITCH_COMPARE pcpath z, pcpath) = true
def $forge_compare_match(pcodeexpr, pcpath) = false -- otherwise
dec $forge_compare(pcodeexpr*, pcpath) : pcodeexpr*
def $forge_compare(eps, pcpath) = eps
def $forge_compare((CODESWITCH_COMPARE pcpath z) :: pcodeexpr*, pcpath) = (CODESWITCH_COMPARE pcpath $(z + 1)) :: pcodeexpr*
def $forge_compare(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $forge_compare(pcodeexpr_tail*, pcpath)
  -- if ~$forge_compare_match(pcodeexpr, pcpath)
dec $forge_bool_match(pcodeexpr, pcpath) : bool
def $forge_bool_match(CODESWITCH_BOOL pcpath b, pcpath) = true
def $forge_bool_match(pcodeexpr, pcpath) = false -- otherwise
dec $forge_bool(pcodeexpr*, pcpath) : pcodeexpr*
def $forge_bool(eps, pcpath) = eps
def $forge_bool((CODESWITCH_BOOL pcpath b) :: pcodeexpr*, pcpath) = (CODESWITCH_BOOL pcpath (~b)) :: pcodeexpr*
def $forge_bool(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $forge_bool(pcodeexpr_tail*, pcpath)
  -- if ~$forge_bool_match(pcodeexpr, pcpath)
dec $forge_code(pcode*, porigin, nat, bool) : pcode*
def $forge_code(eps, porigin, n_case, b_bool) = eps
def $forge_code(pcode :: pcode_tail*, PORIGIN n pcpath_root, n_case, false) = pcode[.EXPRESSIONS = $forge_compare(pcode.EXPRESSIONS, pcpath_root ++ [PCFIELD 1, PCINDEX n_case])] :: pcode_tail*
  -- if pcode.UNIT = n
def $forge_code(pcode :: pcode_tail*, PORIGIN n pcpath_root, n_case, true) = pcode[.EXPRESSIONS = $forge_bool(pcode.EXPRESSIONS, pcpath_root)] :: pcode_tail*
  -- if pcode.UNIT = n
def $forge_code(pcode :: pcode_tail*, PORIGIN n pcpath_root, n_case, b_bool) = pcode :: $forge_code(pcode_tail*, PORIGIN n pcpath_root, n_case, b_bool)
  -- if pcode.UNIT =/= n
'''
COMMON = [
    'S_initial = __INITIAL__',
    'S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], __STAGE__, 512)',
    'S = S_pause[.COMPLETION = NORMAL]',
    '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$drive(S, 1) = $drive_steps(S, 1)',
    'S_done = $drive(S, 1000)',
]
NORMAL = [
    ['S.TODO = (SWITCH_START statement porigin) :: ptask_tail*',
     '~$call_tasks_valid(S, (SWITCH_START statement (PORIGIN 0 eps)) :: ptask_tail*)',
     '~$call_tasks_valid(S[.ORIGIN = eps], S.TODO)'],
    ['S.TODO = (SWITCH_SCAN statement porigin (KNOWN (POBJECT n_object)) n) :: ptask_tail*',
     '$task_nodes(SWITCH_SCAN statement porigin (KNOWN (POBJECT n_object)) n) = [HOBJECT n_object]',
     '~$call_tasks_valid(S, (SWITCH_SCAN statement porigin (KNOWN (POBJECT n_object)) $(|$switch_cases(statement)| + 1)) :: ptask_tail*)',
     '~$call_tasks_valid(S, (SWITCH_SCAN statement (PORIGIN 0 eps) (KNOWN (POBJECT n_object)) n) :: ptask_tail*)'],
    ['S.TODO = (SWITCH_COMPARE statement porigin (KNOWN (POBJECT n_object)) n z) :: ptask_tail*',
     '~$call_tasks_valid(S, (SWITCH_COMPARE statement porigin (KNOWN (POBJECT n_object)) n $(z + 1)) :: ptask_tail*)',
     '~$call_tasks_valid(S, (SWITCH_COMPARE statement porigin (KNOWN (POBJECT n_object)) $(|$switch_cases(statement)|) z) :: ptask_tail*)',
     'S_forged = S[.CODE = $forge_code(S.CODE, porigin, n, false)][.TODO = (SWITCH_COMPARE statement porigin (KNOWN (POBJECT n_object)) n $(z + 1)) :: ptask_tail*]',
     '~$call_descriptors_valid(S_forged)'],
    ['S.TODO = (SWITCH_NEXT statement porigin (KNOWN (POBJECT n_object))) :: ptask_tail*',
     '$task_nodes(SWITCH_NEXT statement porigin (KNOWN (POBJECT n_object))) = [HOBJECT n_object]',
     '$heap_owners($heap_graph(S), HOBJECT n_object) = 1',
     '~$call_tasks_valid(S, (SWITCH_NEXT statement (PORIGIN 0 eps) (KNOWN (POBJECT n_object))) :: ptask_tail*)',
     '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0'],
]
ABRUPT = NORMAL[2] + [
    '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
    'S_done.TODO = eps',
]
BOOL = [
    'S.TODO = (SWITCH_COMPARE statement porigin (KNOWN (PBOOL true)) n z) :: ptask_tail*',
    '$switch_bool_mode(S, porigin) = (true)',
    '~$call_tasks_valid(S, (SWITCH_COMPARE statement porigin (KNOWN (PBOOL false)) n z) :: ptask_tail*)',
    '~$call_tasks_valid(S, (SWITCH_COMPARE statement porigin (KNOWN PNULL) n z) :: ptask_tail*)',
    'S_forged = S[.CODE = $forge_code(S.CODE, porigin, n, true)][.TODO = (SWITCH_COMPARE statement porigin (KNOWN (PBOOL false)) n z) :: ptask_tail*]',
    '~$call_descriptors_valid(S_forged)',
]


def checked_source(name, output):
    source = output / (name + '.php')
    source.write_text(SOURCES[name])
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], output / (name + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         output / (name + '-adapter'))
        parsed = frontend.request({'op': 'parse', 'source': request.b64(source.read_bytes())})
        assert parsed['ok'] and parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    return ('$php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(request.b64(str(source).encode())) + ')'), hashlib.sha256(source.read_bytes()).hexdigest()


def main():
    output = Path(tempfile.mkdtemp(prefix='switch-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    rows = []
    for name, stages in [('normal', list(enumerate(NORMAL))), ('abrupt', [(2, ABRUPT)]), ('bool', [(2, BOOL)])]:
        initial, source_hash = checked_source(name, output)
        for stage, extra in stages:
            checks = [line.replace('__INITIAL__', initial).replace('__STAGE__', str(stage)) for line in COMMON]
            checks += ['S_done.COMPLETION = NORMAL' if name != 'abrupt' else 'S_done.COMPLETION = THROWN text n_message* z_error',
                       '$outputs(S_done.EVENTS) = ' + ('[65, 55]' if name == 'normal' else '[65]')]
            checks += extra
            fixture = output / (name + '-' + str(stage) + '.watsup')
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- if ' + line + '\n' for line in checks))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(fixture)], capture_output=True, timeout=300)
            (output / (name + '-' + str(stage) + '.stdout')).write_bytes(result.stdout)
            (output / (name + '-' + str(stage) + '.stderr')).write_bytes(result.stderr)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            row = {'source': name, 'stage': stage, 'assertions': len(checks), 'pass': passed,
                   'source_sha256': source_hash}
            rows.append(row)
            print(row, flush=True)
            assert passed, result.stderr
    assert before == request.t.syntax_validation.implementation_fingerprint()
    assert [sum(row['assertions'] for row in rows if row['source'] == name) for name in SOURCES] == [53, 17, 15]
    (output / 'report.json').write_text(json.dumps({'result': 'pass', 'fingerprint': before, 'stages': rows}, indent=2) + '\n')
    print('PASS switch protocol: 6 stages, 85 assertions', output)


if __name__ == '__main__':
    main()
