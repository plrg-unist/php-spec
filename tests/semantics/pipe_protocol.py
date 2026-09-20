#!/usr/bin/env python3
"""Paused pipe ownership and compiled-line integrity controls."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(tempfile.mkdtemp(prefix='pipe-protocol-'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

sources = json.loads((ROOT / 'tests/semantics/pipe_cases.json').read_text())
sources['pipe-only'] = '<?php echo 2 |> 3;\n'
modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
fingerprint = request.t.syntax_validation.implementation_fingerprint()

PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_FORCE porigin z_read z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (POBJECT n)) z_send z_call) :: ptask*
def $review_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin)
  -- if $pipe_site(S, porigin)
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
dec $review_match(pcodeexpr, pcpath, nat) : bool
def $review_match(CODEEXPR pcpath z b, pcpath, 0) = true
def $review_match(CODEPIPE_SEND pcpath z, pcpath, n) = true -- if $(n > 0)
def $review_match(pcodeexpr, pcpath, n) = false -- otherwise
dec $review_edit(pcodeexpr*, pcpath, nat) : pcodeexpr*
def $review_edit(eps, pcpath, n) = eps
def $review_edit((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath, 0) = (CODEEXPR pcpath $(z + 1) b) :: pcodeexpr*
def $review_edit((CODEPIPE_SEND pcpath z) :: pcodeexpr*, pcpath, 1) = (CODEPIPE_SEND pcpath $(z + 1)) :: pcodeexpr*
def $review_edit((CODEPIPE_SEND pcpath z) :: pcodeexpr*, pcpath, 2) = pcodeexpr*
def $review_edit((CODEPIPE_SEND pcpath z) :: pcodeexpr*, pcpath, 3) = (CODEPIPE_SEND pcpath z) :: (CODEPIPE_SEND pcpath z) :: pcodeexpr*
def $review_edit(pcodeexpr :: pcodeexpr_tail*, pcpath, n) = pcodeexpr :: $review_edit(pcodeexpr_tail*, pcpath, n)
  -- if ~$review_match(pcodeexpr, pcpath, n)
dec $review_edit_codes(pcode*, porigin, nat) : pcode*
def $review_edit_codes(eps, porigin, n_mode) = eps
def $review_edit_codes(pcode :: pcode_tail*, PORIGIN n pcpath, n_mode) = pcode[.EXPRESSIONS = $review_edit(pcode.EXPRESSIONS, pcpath, n_mode)] :: pcode_tail*
  -- if pcode.UNIT = n
def $review_edit_codes(pcode :: pcode_tail*, PORIGIN n pcpath, n_mode) = pcode :: $review_edit_codes(pcode_tail*, PORIGIN n pcpath, n_mode)
  -- if pcode.UNIT =/= n
'''

FORCE = [
    'S.TODO = (PIPE_FORCE porigin z_read z_send z_call) :: ptask_tail*',
    '$pipe_task_valid(S, porigin, z_read, z_send, z_call)',
    '~$call_tasks_valid(S, (PIPE_FORCE porigin z_read $(z_send + 1) z_call) :: ptask_tail*)',
    '~$call_tasks_valid(S, (PIPE_FORCE porigin z_read z_send $(z_call + 1)) :: ptask_tail*)',
    '~$pipe_task_valid(S[.ORIGIN = (PORIGIN 0 eps)], PORIGIN 0 eps, z_read, z_send, z_call)',
]
AUTH = [
    'S_root = S[.CODE = $review_edit_codes(S.CODE, porigin, 0)][.TODO = (PIPE_FORCE porigin z_read z_send $(z_call + 1)) :: ptask_tail*]',
    '~$call_descriptors_valid(S_root)',
    'S_send = S[.CODE = $review_edit_codes(S.CODE, porigin, 1)][.TODO = (PIPE_FORCE porigin z_read $(z_send + 1) z_call) :: ptask_tail*]',
    '~$call_descriptors_valid(S_send)',
    '~$call_descriptors_valid(S[.CODE = $review_edit_codes(S.CODE, porigin, 2)])',
    '~$call_descriptors_valid(S[.CODE = $review_edit_codes(S.CODE, porigin, 3)])',
]
APPLY = [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (POBJECT n)) z_send z_call) :: ptask_tail*',
    '$closure_callable(S, n)',
    '$task_nodes(PIPE_APPLY porigin (KNOWN (POBJECT n)) z_send z_call) = [HOBJECT n]',
    'n_owners = $heap_owners($heap_graph(S), HOBJECT n)', '$(n_owners > 0)',
    '~$pipe_apply_task_valid(S, porigin, (KNOWN PNULL), $(z_send + 1), z_call)',
    '~$pipe_apply_task_valid(S, porigin, (KNOWN PNULL), z_send, $(z_call + 1))',
]
CURRENT = [
    'S.CURRENT = (pcallcontext)', 'pcallcontext.CALLSITE = (porigin)',
    '$pipe_site(S, porigin)', '$call_current_valid(S)',
    '~$call_current_valid(S[.CURRENT = (pcallcontext[.ARGC = 2])])',
    '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLSITE = (PORIGIN 0 eps)])])',
]


def checked_source(name):
    source = OUTPUT / (name + '.php')
    source.write_bytes(sources[name].encode())
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], OUTPUT / (name + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         OUTPUT / (name + '-adapter'))
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
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(request.b64(str(source).encode())) + ')'


def run_case(name, initial, stage, completion, output, extra):
    checks = [
        'S_initial = ' + initial,
        'S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], ' + str(stage) + ', 256)',
        'S = S_pause[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$drive(S, 1) = $drive_steps(S, 1)',
        'S_done = $drive(S, 1000)',
        'S_done.COMPLETION ' + completion,
        '$outputs(S_done.EVENTS) = ' + output,
        *extra,
    ]
    fixture = OUTPUT / (name + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *modules, str(fixture)], capture_output=True, timeout=300)
    (OUTPUT / (name + '.stdout')).write_bytes(result.stdout)
    (OUTPUT / (name + '.stderr')).write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, name
    print(name, len(checks), 'pass', flush=True)
    return len(checks)


normal = checked_source('pending-wrapper-rebind')
abrupt = checked_source('fatal-right-owned-left')
pipe_only = checked_source('pipe-only')
count = 0
count += run_case('normal-force', normal, 0, '= NORMAL', '[55]', FORCE + AUTH)
count += run_case('normal-apply', normal, 1, '= NORMAL', '[55]', APPLY)
count += run_case('normal-current', normal, 2, '= NORMAL', '[55]', CURRENT)
count += run_case('abrupt-force', abrupt, 0, '=/= NORMAL', '[82]', FORCE + [
    'S.OBJECTS[0] = NAMEDCLOSURE porigin_function',
    '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT 0) = 0',
    'S_done.TODO = eps',
])
count += run_case('pipe-only-force', pipe_only, 0, '=/= NORMAL', 'eps', FORCE + AUTH)
assert fingerprint == request.t.syntax_validation.implementation_fingerprint()
assert count == 89, count
print('PASS pipe protocol: 5 stages, 89 assertions', flush=True)
shutil.rmtree(OUTPUT)
