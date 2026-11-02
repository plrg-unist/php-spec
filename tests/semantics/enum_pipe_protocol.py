#!/usr/bin/env python3
"""Source-reached generated enum pipe selection and saved-call guards."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='enum-pipe-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

CASES = {row['id']: row for row in json.loads((ROOT / 'tests/semantics/enum_pipe_cases.json').read_text())}
MODULES = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_pipe_cases.json',
           ROOT / 'tests/semantics/enum_pipe_protocol.py', ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]
PREFIX = r'''
dec $ep_front(pstate, ptbytes) : bool
def $ep_front(S, ptbytes_method) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes_class text_method
  -- if ptbytes_method = $ptascii(text_method)
  -- if $pipe_site(S, pconfigcall.SITE)
def $ep_front(S, ptbytes_method) = false -- otherwise
dec $ep_seek(pstate, ptbytes, nat) : pstate
def $ep_seek(S, ptbytes_method, 0) = S
def $ep_seek(S, ptbytes_method, n) = S
  -- if $(n > 0)
  -- if $ep_front(S, ptbytes_method)
def $ep_seek(S, ptbytes_method, n) = $ep_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptbytes_method, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$ep_front(S, ptbytes_method)
dec $ep_output_item(pevent) : ptbytes
def $ep_output_item(OUTPUT n*) = n*
def $ep_output_item(pevent) = eps -- otherwise
dec $ep_output(pevent*) : ptbytes
def $ep_output(eps) = eps
def $ep_output(pevent :: pevent_tail*) = $ep_output_item(pevent) ++ $ep_output(pevent_tail*)
'''


def checked_source(case_id):
    row = CASES[case_id]
    source = OUT / (case_id + '.php')
    source.write_bytes(row['source'].encode())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS, '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], OUT / (case_id + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         OUT / (case_id + '-adapter'))
        parsed = frontend.request({'op': 'parse', 'source': request.b64(source.read_bytes())})
        assert parsed['ok'] and parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        if frontend:
            frontend.close()
        if adapter:
            adapter.close()
    path = base64.b64encode(str(source).encode()).decode()
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(path) + ')'


def run_case(case_id, method, expected_class, expected_output):
    checks = [
        'S_initial = ' + checked_source(case_id),
        'S_initial.COMPLETION = BUDGET',
        'S_wait = $ep_seek(S_initial, $ptascii("' + method + '"), 2000)',
        '$ep_front(S_wait, $ptascii("' + method + '"))',
        'S = S_wait[.COMPLETION = NORMAL]',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_class ptbytes_class "' + method + '"',
        'ptbytes_class = $ptascii("' + expected_class + '")',
        'pconfigcall.OWNER = eps',
        'pconfigcall.SELECTION = (n_nonce)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_left))]',
        '(HOBJECT n_left) <- $task_nodes(CONFIG_INVOKE pconfigcall)',
        '$(n_nonce < |S.SELECTEDCALLS|)',
        'S.SELECTEDCALLS[n_nonce] = pselectedcall',
        'pselectedcall.NONCE = n_nonce',
        'pselectedcall.SITE = pconfigcall.SITE',
        'pselectedcall.KIND = pconfigcall.KIND',
        'pselectedcall.LINE = pconfigcall.LINE',
        '$selected_entry_source_valid(S, pselectedcall)',
        '$selected_entry_active_valid(S, pselectedcall)',
        '$selected_task_count(S.TODO, n_nonce) = 1',
        '$config_invoke_valid(S, pconfigcall)',
        '$call_descriptors_valid(S)',
        '$heap_valid($heap_graph(S))',
        '~$config_invoke_valid(S[.SELECTEDCALLS = eps], pconfigcall)',
        '~$config_invoke_valid(S, pconfigcall[.SELECTION = ($(n_nonce + 1))])',
        '~$config_invoke_valid(S, pconfigcall[.SITE = (PORIGIN 999 eps)])',
        '~$config_invoke_valid(S, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
        '~$selected_entry_source_valid(S, pselectedcall[.SITE = PORIGIN 999 eps])',
        'S_zero = $drive_steps(S, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$ep_output(S_done.EVENTS) = $ptascii("' + expected_output + '")',
    ]
    fixture = OUT / (case_id + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=120)
    (OUT / (case_id + '.command.json')).write_text(json.dumps(command) + '\n')
    (OUT / (case_id + '.stdout')).write_bytes(result.stdout)
    (OUT / (case_id + '.stderr')).write_bytes(result.stderr)
    record = {'case': case_id, 'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace')}
    print(json.dumps(record), flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, OUT
    return record


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    records = [run_case('enum-pipe-forced-left-error', 'cases', 'PipeNoArgs', 'arity|LEFT-DROP|'),
               run_case('enum-pipe-rebinding-left', 'from', 'PipeSelected', 'CAST|DROP|selected|rebound|')]
    assert before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in WATCHED}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (OUT / 'report.json').write_text(json.dumps({'revision': revision, 'modules': len(MODULES),
                                                  'mode': 'SL', 'direct_inputs': before,
                                                  'records': records}, indent=2) + '\n')
    print('PASS enum pipe protocol', OUT, flush=True)
