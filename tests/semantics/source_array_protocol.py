#!/usr/bin/env python3
"""Source-derived Array operand owners, warning callbacks and parser cleanup.

Rejected parser helper states are normalized with production prune_allocations;
that registration boundary is not an additional reached VM step.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
import textwrap

from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
C = R
SOURCES = Path(__file__).with_name('source-arrays')
Q = SOURCES / 'core'
GROUPS = ('borrowed', 'captured', 'eval', 'throw')
b64 = lambda b: base64.b64encode(b).decode()
term = lambda b: '$base64(' + json.dumps(b64(b)) + ')'

HELPERS = r'''
dec $array_ingress_stage(pstate, int, nat) : bool
def $array_ingress_stage(S, z, 0) = true
  -- if S.TODO = (FILE_REQUEST porigin z n_kind) :: ptask_tail*
def $array_ingress_stage(S, z, 0) = true
  -- if S.TODO = (EVAL_REQUEST porigin z) :: ptask_tail*
def $array_ingress_stage(S, z, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand
  -- if psourceoperand.LINE = z
def $array_ingress_stage(S, z, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand
  -- if psourceoperand.LINE = z
  -- if pcallcontext.CALLSITE = (perrorcall.SITE)
def $array_ingress_stage(S, z, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand
  -- if psourceoperand.LINE = z
def $array_ingress_stage(S, z, n) = false -- otherwise
dec $array_ingress_seek(pstate, int, nat, nat) : pstate
def $array_ingress_seek(S, z, n_stage, n) = S -- if $array_ingress_stage(S, z, n_stage)
def $array_ingress_seek(S, z, n_stage, n) = S
  -- if ~$array_ingress_stage(S, z, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $array_ingress_seek(S, z, n_stage, 0) = S
  -- if ~$array_ingress_stage(S, z, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $array_ingress_seek(S, z, n_stage, n) = $array_ingress_seek($drive_steps(S[.COMPLETION = NORMAL], 1), z, n_stage, $nabs($(n - 1)))
  -- if ~$array_ingress_stage(S, z, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $array_root_count(pnode*, pnode) : nat
def $array_root_count(eps, pnode) = 0
def $array_root_count(pnode_head :: pnode_tail*, pnode) = $($array_root_count(pnode_tail*, pnode) + 1)
  -- if pnode_head = pnode
def $array_root_count(pnode_head :: pnode_tail*, pnode) = $array_root_count(pnode_tail*, pnode)
  -- if pnode_head =/= pnode
'''


def render(fixtures, sources):
    setup = ''.join('dec $array_' + name + '_program() : program\ndef $array_' + name + '_program() = ' + value + '\n' for name, value in fixtures.items())
    setup += textwrap.dedent(HELPERS)
    core = term(bytes(sources['core']))
    late = term(bytes(sources['late']))
    latebytes = term(sources['late'].read_bytes())
    early = term(bytes(sources['early']))
    earlybytes = term(sources['early'].read_bytes())
    cwd = term(bytes(C))
    setup += '\ndec $array_first_compiled() : pstate\ndef $array_first_compiled() = $file_parse_resume(S_parse, SOURCE_ACCEPT n_unit ' + latebytes + ' $array_late_program())\n'
    setup += '  -- if S_wait = $php_file_run($array_core_program(), 2000, ' + core + ', ' + cwd + ')\n'
    setup += '  -- if S_parse = $file_open_resume(S_wait, FILE_OPENED 0 ' + core + ' $ptascii("Array") ' + late + ' ' + late + ' ' + latebytes + ')\n'
    setup += '  -- if S_parse.FILECONTEXTS = pfilecontext :: eps\n  -- if pfilecontext.UNIT = (n_unit)\n'
    groups = {}
    groups['borrowed'] = [
        'S_initial = $php_file_run($array_core_program(), 0, ' + core + ', ' + cwd + ')',
        '$call_descriptors_valid(S_initial)',
        'S_before = $array_ingress_seek(S_initial, 17, 0, 1000)',
        '$array_ingress_stage(S_before, 17, 0)',
        'S_before.RESULT = VARIABLE n_name* z_variable',
        'S_read = $resolve_at(S_before[.COMPLETION = NORMAL], S_before.RESULT, 17)',
        'S_read.RESULT = KNOWN (PARRAY n_array)',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand',
        'psourceoperand.INPUT = S_before.RESULT',
        'psourceoperand.LINE = 17', 'psourceoperand.KIND = 1', 'psourceoperand.OWNER = 0',
        'psourceoperand.TAIL = ptask_tail*',
        '$call_descriptors_valid(S_pending)', '$error_call_valid(S_pending, perrorcall)',
        '$task_nodes(perrorcall.RESUME) = eps',
        'S_pending.RESULT = KNOWN PNULL', 'S_pending.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_pending.FILESEQ = 0', 'S_pending.FILECONTEXTS = eps',
        '~$error_call_valid(S_pending, perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_pending, perrorcall[.LINE = 18])',
        '~$error_call_valid(S_pending, perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.SITE = $source_operand_child(psourceoperand)]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.KIND = 2]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.OWNER = 1]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.LINE = 18]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.INPUT = VARIABLE $ptascii("wrong") z_variable]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.INPUT = KNOWN (PARRAY n_array)]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = [ERROR_HANDLER_INVOKE perrorcall]])',
        '~$source_array_valid(S_pending[.TODO = [ERROR_HANDLER_INVOKE perrorcall, SOURCE_ARRAY_RESULT psourceoperand] ++ ptask_tail*], psourceoperand)',
        'S_nohandler = $drive_steps(S_before[.COMPLETION = NORMAL][.ERRORHANDLER = S_before.ERRORHANDLER[.CALLBACK = eps]], 1)',
        'S_nohandler.TODO = (SOURCE_ARRAY_RESULT psourceoperand) :: ptask_tail*',
        'S_nohandler.RESULT = KNOWN PNULL', 'S_nohandler.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(SOURCE_ARRAY_RESULT psourceoperand) = eps', '$call_descriptors_valid(S_nohandler)',
        'S_masked = $drive_steps(S_before[.COMPLETION = NORMAL][.ERRORHANDLER = S_before.ERRORHANDLER[.LEVELS = 0]], 1)',
        'S_masked.TODO = (SOURCE_ARRAY_RESULT psourceoperand) :: ptask_tail*',
        'S_masked.RESULT = KNOWN PNULL', 'S_masked.BASE = BASE_VALUE (KNOWN PNULL)', '$call_descriptors_valid(S_masked)',
        'S_entered = $array_ingress_seek(S_pending, 17, 2, 1000)',
        '$array_ingress_stage(S_entered, 17, 2)', '$call_descriptors_valid(S_entered)',
        'S_entered.CURRENT = (pcallcontext)', 'S_entered.FRAMES = pframe :: pframe_tail*',
        '$eval_trace_preparser(S_entered, S_entered.CURRENT, pframe) = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("include")', 'ptraceframe.LINE = 17',
        'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS',
        '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.TODO = [ERROR_HANDLER_RESULT perrorcall]] :: pframe_tail*])',
        'S_returned = $array_ingress_seek(S_entered, 17, 3, 1000)',
        '$array_ingress_stage(S_returned, 17, 3)', '$call_descriptors_valid(S_returned)',
        '~((HARRAY n_array) <- S_returned.ALLOCATIONS)',
        'S_result = $drive_steps(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_ARRAY_RESULT psourceoperand) :: ptask_tail*',
        '$call_descriptors_valid(S_result)',
        'S_wait = $drive_steps(S_result[.COMPLETION = NORMAL], 1)',
        'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.FILECONTEXTS = pfilecontext :: eps',
        'pfilecontext.NONCE = 0', 'pfilecontext.REQUESTED = $ptascii("Array")',
        'pfilecontext.INCLUDEPATH = ' + term(bytes(Q / 'late')),
        'pfilecontext.CWD = ' + cwd,
        'pfilecontext.TAIL = (SOURCE_OPERAND_RELEASE psourceoperand) :: psourceoperand.TAIL',
        '$call_descriptors_valid(S_wait)', '$heap_valid($heap_graph(S_wait))',
        '~((HARRAY n_array) <- $heap_graph(S_wait).ROOTS)',
    ]
    groups['captured'] = [
        'S_first = $array_first_compiled()', 'S_first.COMPLETION = NORMAL', '$call_descriptors_valid(S_first)',
        'S_before = $array_ingress_seek(S_first, 19, 0, 1000)', '$array_ingress_stage(S_before, 19, 0)',
        'S_before.RESULT = KNOWN (PARRAY n_array)', '(HARRAY n_array) <- S_before.ALLOCATIONS',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand',
        'psourceoperand.INPUT = KNOWN (PARRAY n_array)', 'psourceoperand.LINE = 19',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_array]',
        'S_pending.RESULT = KNOWN PNULL', 'S_pending.BASE = BASE_VALUE (KNOWN PNULL)',
        '$array_root_count($heap_graph(S_pending).ROOTS, HARRAY n_array) = 1',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '~$call_descriptors_valid(S_pending[.ALLOCATIONS = $call_remove_owner(S_pending.ALLOCATIONS, HARRAY n_array)])',
        'S_returned = $array_ingress_seek(S_pending, 19, 3, 1000)',
        '$array_ingress_stage(S_returned, 19, 3)', '$call_descriptors_valid(S_returned)',
        '(HARRAY n_array) <- S_returned.ALLOCATIONS',
        'S_result = $drive_steps(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_ARRAY_RESULT psourceoperand) :: ptask_tail*',
        'S_wait = $drive_steps(S_result[.COMPLETION = NORMAL], 1)',
        'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.FILECONTEXTS = pfilecontext :: eps',
        'pfilecontext.NONCE = 1', 'pfilecontext.REQUESTED = $ptascii("Array")',
        'pfilecontext.INCLUDEPATH = ' + term(bytes(Q / 'early')),
        '(HARRAY n_array) <- S_wait.ALLOCATIONS',
        '$array_root_count($heap_graph(S_wait).ROOTS, HARRAY n_array) = 1', '$call_descriptors_valid(S_wait)',
        'S_parse = $file_open_resume(S_wait, FILE_OPENED 1 ' + core + ' $ptascii("Array") ' + early + ' ' + early + ' ' + earlybytes + ')',
        'S_parse.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_parse)',
        '(HARRAY n_array) <- S_parse.ALLOCATIONS',
        '$array_root_count($heap_graph(S_parse).ROOTS, HARRAY n_array) = 1',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps', 'pfilecontext_parse.UNIT = (n_parsed_unit)',
        'S_compiled = $file_parse_resume(S_parse, SOURCE_ACCEPT n_parsed_unit ' + earlybytes + ' $array_early_program())',
        'S_compiled.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*',
        '$call_descriptors_valid(S_compiled)', '$heap_valid($heap_graph(S_compiled))',
        'S_compiled.FILECONTEXTS = pfilecontext_run :: eps',
        'pfilecontext_run.PHASE = FILE_UNIT_RUN', 'pfilecontext_run.TAIL = psourceoperand.TAIL',
        '$array_root_count($heap_graph(S_compiled).ROOTS, HARRAY n_array) = 1',
        '~$call_descriptors_valid(S_compiled[.TODO = (SOURCE_OPERAND_ENTER psourceoperand $(n_unit + 1)) :: ptask_body*])',
        '~$call_descriptors_valid(S_compiled[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]])',
        'S_zero = $drive_steps(S_compiled, 0)', 'S_zero.TODO = S_compiled.TODO', '(HARRAY n_array) <- S_zero.ALLOCATIONS',
        'S_body = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)', 'S_body.TODO = ptask_body*',
        '~((HARRAY n_array) <- S_body.ALLOCATIONS)', '~((HARRAY n_array) <- $heap_graph(S_body).ROOTS)',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
    ]
    message = '$ptascii(' + json.dumps('syntax error, unexpected end of file, expecting "("') + ')'
    groups['eval'] = [
        'S_first = $php_run($array_eval_program(), 2000, ' + json.dumps(b64(bytes(sources['eval']))) + ')',
        'S_first.COMPLETION = SOURCE_PENDING', 'S_first.EVALCONTEXTS = pevalcontext_first :: eps',
        'pevalcontext_first.BYTES = $ptascii("Array")', '$call_descriptors_valid(S_first)',
        'S_reject = $prune_allocations($eval_resume(S_first, SOURCE_PARSE_REJECT pevalcontext_first.UNIT $ptascii("Array") ' + message + ' 1))',
        'S_reject.TODO = (SOURCE_OPERAND_THROW psourceoperand_first n_error_first) :: ptask_first_tail*',
        'ptask_first_tail* = psourceoperand_first.TAIL',
        '$call_descriptors_valid(S_reject)',
        'S_before = $array_ingress_seek(S_reject, 14, 0, 1000)', '$array_ingress_stage(S_before, 14, 0)',
        'S_before.RESULT = KNOWN (PARRAY n_array)',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand',
        'psourceoperand.KIND = 0', 'psourceoperand.INPUT = KNOWN (PARRAY n_array)',
        'S_wait = $drive_steps(S_pending[.COMPLETION = NORMAL], 2000)',
        'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.EVALCONTEXTS = pevalcontext :: eps',
        'pevalcontext.BYTES = $ptascii("Array")',
        'pevalcontext.TAIL = (SOURCE_OPERAND_RELEASE psourceoperand) :: psourceoperand.TAIL',
        '(HARRAY n_array) <- S_wait.ALLOCATIONS',
        '$array_root_count($heap_graph(S_wait).ROOTS, HARRAY n_array) = 1',
        '$call_descriptors_valid(S_wait)', '$heap_valid($heap_graph(S_wait))',
        'S_throw = $prune_allocations($eval_resume(S_wait, SOURCE_PARSE_REJECT pevalcontext.UNIT $ptascii("Array") ' + message + ' 1))',
        'S_throw.TODO = (SOURCE_OPERAND_THROW psourceoperand n_error) :: psourceoperand.TAIL',
        '(HARRAY n_array) <- S_throw.ALLOCATIONS', '(HOBJECT n_error) <- S_throw.ALLOCATIONS',
        '$call_descriptors_valid(S_throw)',
        '~$call_descriptors_valid(S_throw[.TODO = (SOURCE_OPERAND_THROW psourceoperand n_error_first) :: psourceoperand.TAIL])',
        'S_zero = $drive_steps(S_throw, 0)', 'S_zero.TODO = S_throw.TODO',
        'S_search = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)',
        'S_search.TODO = (THROW_SEARCH n_error) :: psourceoperand.TAIL',
        '~((HARRAY n_array) <- S_search.ALLOCATIONS)', '$call_descriptors_valid(S_search)',
        'S_done = $drive_steps(S_search[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        'S_done.EVALCONTEXTS = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    groups['throw'] = [
        'S_initial = $php_startup_run($array_throw_program(), 0, ' + json.dumps(b64(bytes(sources['throw']))) + ', {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})',
        'S_entered = $array_ingress_seek(S_initial, 16, 2, 1000)',
        '$array_ingress_stage(S_entered, 16, 2)', '$call_descriptors_valid(S_entered)',
        'S_entered.CURRENT = (pcallcontext)', 'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand', 'psourceoperand.KIND = 3',
        'S_scope = $constant_frame_scope(S_entered, pframe, pframe_tail*)',
        '$source_array_valid(S_scope, psourceoperand)',
        '$eval_trace_preparser(S_entered, S_entered.CURRENT, pframe) = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("require")', 'ptraceframe.LINE = 16',
        'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS',
        'S_entered.FILECWD = eps', 'S_entered.FILESEQ = 0', 'S_entered.FILECONTEXTS = eps',
        'S_done = $drive_steps(S_entered[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        'S_done.FILECWD = eps', 'S_done.FILESEQ = 0', 'S_done.FILECONTEXTS = eps',
        'S_done.FILEBINDINGS = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return setup, groups



def prepare(out):
    sources = {'core': Q / 'core-observer.php', 'early': Q / 'early/Array',
               'late': Q / 'late/Array', 'eval': SOURCES / 'eval.php', 'throw': SOURCES / 'throw.php'}
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
                  for name, path in sources.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'syntax-adapter')
    try:
        fixtures = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture']
                    for name, row in parsed.items()}
    finally:
        adapter.close()
    setup, groups = render(fixtures, sources)
    counts = {}
    for name, checks in groups.items():
        (out / (name + '.watsup')).write_text(setup + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n')
        counts[name] = len(checks)
    (out / 'prepared.json').write_text(json.dumps({'sources': {name: str(path) for name, path in sources.items()},
        'counts': counts, 'logical_checks': 206, 'main_premises': 207}) + '\n')
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = Path(tempfile.mkdtemp(prefix='source-array-protocol-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', Path(__file__), runner,
               R / 'tests/semantics/error_handler_run.py', R / 'tests/semantics/recorded_worker.py',
               R / 'frontend/worker.php', R / '_build/default/adapter/main.exe',
               R / 'tests/semantics/profile.json', *sorted(SOURCES.rglob('*.php')),
               Q / 'early/Array', Q / 'late/Array']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    counts = prepare(out)
    rows = []
    if not args.prepare_only:
        for name in ([args.group] if args.group else GROUPS):
            process = recorded([str(runner), '--sl', *map(str, modules), str(out / (name + '.watsup'))], out / name, 90)
            passed = (process['exit'] == 0 and not process['timeout']
                      and (out / (name + '.stdout')).read_bytes() == b'true\n'
                      and not (out / (name + '.stderr')).read_bytes())
            rows.append({'group': name, 'conditions': counts[name], 'pass': passed, 'process': process})
            print(name, passed, flush=True)
            if not passed:
                break
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'mode': 'SL', 'logical_checks': 206, 'main_premises': 207, 'prepare_only': args.prepare_only,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}, indent=2) + '\n')
    return args.prepare_only or (len(rows) == (1 if args.group else len(GROUPS)) and all(row['pass'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
