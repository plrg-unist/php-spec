#!/usr/bin/env python3
"""Source-derived undefined operand callbacks, trace frames and empty-path priority."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-undefined')
GROUPS = ('direct', 'empty', 'throw-include', 'throw-once', 'throw-dynamic', 'dynamic', 'nohandler')
b64 = lambda value: base64.b64encode(value).decode()
term = lambda value: '$base64(' + json.dumps(b64(value)) + ')'
HELPERS = r'''
dec $source_cv_marker(ptask) : int?
def $source_cv_marker(SOURCE_READ_RESULT psourceoperand) = (psourceoperand.LINE)
def $source_cv_marker(SOURCE_NAME_RESULT psourceoperand z) = (psourceoperand.LINE)
def $source_cv_marker(ptask) = eps -- otherwise
dec $source_cv_stage(pstate, int, nat) : bool
def $source_cv_stage(S, z, 0) = true
  -- if S.TODO = (EVAL_REQUEST porigin z) :: ptask_tail*
def $source_cv_stage(S, z, 0) = true
  -- if S.TODO = (FILE_REQUEST porigin z n_kind) :: ptask_tail*
def $source_cv_stage(S, z, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if $source_cv_marker(perrorcall.RESUME) = (z)
def $source_cv_stage(S, z, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $source_cv_marker(perrorcall.RESUME) = (z)
  -- if pcallcontext.CALLSITE = (perrorcall.SITE)
def $source_cv_stage(S, z, 3) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $source_cv_marker(perrorcall.RESUME) = (z)
def $source_cv_stage(S, z, 4) = true
  -- if S.TODO = (SOURCE_READ_RESULT psourceoperand) :: ptask_tail*
  -- if psourceoperand.LINE = z
def $source_cv_stage(S, z, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $source_cv_marker(perrorcall.RESUME) = (z)
def $source_cv_stage(S, z, 10) = true
  -- if S.TODO = (NAME_READ z) :: ptask_tail*
def $source_cv_stage(S, z, n) = false -- otherwise
dec $source_cv_seek(pstate, int, nat, nat) : pstate
def $source_cv_seek(S, z, n_stage, n) = S -- if $source_cv_stage(S, z, n_stage)
def $source_cv_seek(S, z, n_stage, n) = S
  -- if ~$source_cv_stage(S, z, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $source_cv_seek(S, z, n_stage, 0) = S
  -- if ~$source_cv_stage(S, z, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $source_cv_seek(S, z, n_stage, n) = $source_cv_seek($drive_steps(S[.COMPLETION = NORMAL], 1), z, n_stage, $nabs($(n - 1)))
  -- if ~$source_cv_stage(S, z, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def render(fixtures, sources):
    setup = ''.join('dec $source_cv_' + name + '() : program\ndef $source_cv_' + name + '() = ' + value + '\n' for name, value in fixtures.items()) + HELPERS
    start = lambda name: '$php_startup_run($source_cv_' + name + '(), 0, ' + json.dumps(b64(bytes(sources[name]))) + ', {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})'
    groups = {}
    groups['direct'] = [
        'S_initial = ' + start('mutation'),
        'S_before = $source_cv_seek(S_initial, 23, 0, 1000)', '$source_cv_stage(S_before, 23, 0)',
        'S_before.RESULT = VARIABLE n_name* z_input', '$error_missing_operand(S_before, S_before.RESULT)',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_READ_RESULT psourceoperand',
        'psourceoperand.INPUT = S_before.RESULT', 'psourceoperand.KIND = 0', 'psourceoperand.OWNER = 0',
        'psourceoperand.TAIL = ptask_tail*', '$call_descriptors_valid(S_pending)',
        '$task_nodes(perrorcall.RESUME) = eps', 'S_pending.RESULT = KNOWN PNULL',
        'S_pending.BASE = BASE_VALUE (KNOWN PNULL)', 'S_pending.FILESEQ = 0', 'S_pending.EVALCONTEXTS = eps',
        '~$error_call_valid(S_pending, perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_pending, perrorcall[.LINE = 24])',
        '~$error_call_valid(S_pending, perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand[.SITE = $source_operand_child(psourceoperand)]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand[.KIND = 1]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand[.OWNER = 1]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand[.INPUT = VARIABLE $ptascii("wrong") z_input]]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand[.INPUT = KNOWN PNULL]]) :: ptask_tail*])',
        '~$source_read_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: [DISCARD] ++ ptask_tail* ++ [SOURCE_READ_RESULT psourceoperand] ++ ptask_tail*], psourceoperand)',
        'S_entered = $source_cv_seek(S_pending, 23, 2, 1000)', '$source_cv_stage(S_entered, 23, 2)',
        '$call_descriptors_valid(S_entered)', 'S_entered.FRAMES = pframe :: pframe_tail*',
        '$eval_trace_preparser(S_entered, S_entered.CURRENT, pframe) = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("eval")', 'ptraceframe.LINE = 23', 'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS',
        'S_returned = $source_cv_seek(S_entered, 23, 3, 1000)', '$source_cv_stage(S_returned, 23, 3)',
        '$call_descriptors_valid(S_returned)',
        'S_result = $drive_steps(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_READ_RESULT psourceoperand) :: ptask_tail*', '$call_descriptors_valid(S_result)',
        'S_zero = $drive_steps(S_result[.COMPLETION = NORMAL], 0)', 'S_zero.TODO = S_result.TODO',
        'S_frozen = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)',
        'S_frozen.RESULT = KNOWN PNULL', 'S_frozen.TODO = (EVAL_REQUEST psourceoperand.SITE 23) :: ptask_tail*',
        'S_done = $drive_steps(S_frozen[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EVALCONTEXTS = eps', 'S_done.FILESEQ = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    groups['empty'] = [
        'S_initial = ' + start('empty'),
        'S_before = $source_cv_seek(S_initial, 9, 0, 1000)', '$source_cv_stage(S_before, 9, 0)',
        'S_before.FILECWD = eps', 'S_before.FILESEQ = 0',
        'S_result = $source_cv_seek(S_before, 9, 4, 1000)', '$source_cv_stage(S_result, 9, 4)',
        'S_result.TODO = (SOURCE_READ_RESULT psourceoperand) :: ptask_tail*', '$call_descriptors_valid(S_result)',
        'S_frozen = $drive_steps(S_result[.COMPLETION = NORMAL], 1)', 'S_frozen.RESULT = KNOWN PNULL',
        'S_error = $drive_steps(S_frozen[.COMPLETION = NORMAL], 1)',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        '$throwable_field(S_error, n_error, "message") = PSTRING $ptascii("Path must not be empty")',
        '$throwable_field(S_error, n_error, "previous") = PNULL',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "ValueError"',
        'S_error.FILECWD = eps', 'S_error.FILESEQ = 0', 'S_error.FILECONTEXTS = eps',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_file = $php_file_startup_run($source_cv_empty(), 0, ' + term(bytes(sources['empty'])) + ', ' + term(bytes(R)) + ', {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})',
        'S_wait = $drive_steps(S_file[.COMPLETION = NORMAL], 2000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.FILECONTEXTS = pfilecontext :: eps', 'pfilecontext.KIND = 2', 'pfilecontext.REQUESTED = eps',
        'pfilecontext.INCLUDEPATH = $ptascii("callback-path")', 'pfilecontext.NONCE = 0',
        '$call_descriptors_valid(S_wait)',
        'S_failure = $file_open_resume(S_wait, FILE_OPEN_FAILURE 0 ' + term(bytes(sources['empty'])) + ' eps ' + term(bytes(sources['empty'].parent)) + ' ' + term(bytes(sources['empty'].parent)) + ' $ptascii("No such file or directory"))',
        '$call_descriptors_valid(S_failure)',
    ]
    groups['throw'] = [
        'S_initial = ' + start('private'),
        'S_search = $source_cv_seek(S_initial, 39, 5, 2000)', '$source_cv_stage(S_search, 39, 5)',
        'S_search.TODO = (THROW_SEARCH n_old) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_READ_RESULT psourceoperand', 'psourceoperand.KIND = 1',
        'psourceoperand.OWNER = |S_search.FRAMES|', 'psourceoperand.TAIL = ptask_tail*',
        '$call_descriptors_valid(S_search)',
        'S_emitter = S_search[.TODO = (THROW_SEARCH n_old) :: ptask_tail*]',
        '$source_read_empty_throw(S_emitter, psourceoperand)',
        'S_retired = S_emitter[.ALLOCATIONS = $destruction_node_delete(S_emitter.ALLOCATIONS, HOBJECT n_old)]',
        '$throwable_member(S_retired, n_old)',
        '~$source_read_empty_throw(S_retired, psourceoperand)',
        '$error_read_discard(S_retired, SOURCE_READ_RESULT psourceoperand) = S_retired',
        'S_drop = $drive_steps(S_search[.COMPLETION = NORMAL], 1)',
        'S_drop.TODO = (THROW_SEARCH n_new) :: ptask_tail*', 'n_new =/= n_old',
        '$throwable_field(S_drop, n_new, "previous") = POBJECT n_old',
        '$throwable_field(S_drop, n_new, "message") = PSTRING $ptascii("Path must not be empty")',
        '$throwable_field(S_drop, n_old, "message") = PSTRING $ptascii("handler")',
        'S_drop.FILECWD = eps', 'S_drop.FILESEQ = 0', 'S_drop.FILECONTEXTS = eps',
        '$call_descriptors_valid(S_drop)', '$heap_valid($heap_graph(S_drop))',
        'S_bad_tail = S_search[.TODO = (THROW_SEARCH n_old) :: [DISCARD] ++ ptask_tail*]',
        '~$source_read_empty_throw(S_bad_tail, psourceoperand)',
        '~$source_read_empty_throw(S_search[.TODO = (THROW_SEARCH n_old) :: ptask_tail*], psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)])',
        'S_once = $source_cv_seek(S_drop, 48, 5, 2000)', '$source_cv_stage(S_once, 48, 5)',
        'S_once.TODO = (THROW_SEARCH n_once) :: (ERROR_HANDLER_RESULT perrorcall_once) :: ptask_once_tail*',
        'perrorcall_once.RESUME = SOURCE_READ_RESULT psourceoperand_once', 'psourceoperand_once.KIND = 4',
        'S_once_drop = $drive_steps(S_once[.COMPLETION = NORMAL], 1)',
        'S_once_drop.TODO = (THROW_SEARCH n_once) :: ptask_once_tail*',
        '$throwable_field(S_once_drop, n_once, "previous") = PNULL',
        'S_once_drop.FILECWD = eps', 'S_once_drop.FILESEQ = 0', '$call_descriptors_valid(S_once_drop)',
        'S_dynamic = $source_cv_seek(S_once_drop, 58, 5, 2000)', '$source_cv_stage(S_dynamic, 58, 5)',
        'S_dynamic.TODO = (THROW_SEARCH n_dynamic) :: (ERROR_HANDLER_RESULT perrorcall_dynamic) :: ptask_dynamic_tail*',
        'perrorcall_dynamic.RESUME = SOURCE_NAME_RESULT psourceoperand_dynamic z_dynamic',
        'S_dynamic_drop = $drive_steps(S_dynamic[.COMPLETION = NORMAL], 1)',
        'S_dynamic_drop.TODO = (THROW_SEARCH n_dynamic) :: ptask_dynamic_tail*',
        '$throwable_field(S_dynamic_drop, n_dynamic, "previous") = PNULL', 'S_dynamic_drop.FILESEQ = 0',
        '$call_descriptors_valid(S_dynamic_drop)',
        'S_done = $drive_steps(S_dynamic_drop[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EVALCONTEXTS = eps', 'S_done.FILECONTEXTS = eps',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    groups['dynamic'] = [
        'S_initial = ' + start('private'),
        'S_before = $source_cv_seek(S_initial, 32, 10, 2000)', '$source_cv_stage(S_before, 32, 10)',
        '$source_name_pending(S_before[.COMPLETION = NORMAL])',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_NAME_RESULT psourceoperand z',
        'psourceoperand.INPUT = KNOWN (PSTRING $ptascii("dynamicEval"))', 'psourceoperand.KIND = 0',
        'psourceoperand.TAIL = ptask_tail*', '$call_descriptors_valid(S_pending)', '$task_nodes(perrorcall.RESUME) = eps',
        '~$error_call_valid(S_pending, perrorcall[.LEVEL = 8])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand $(z + 1)]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand[.SITE = $source_operand_child(psourceoperand)] z]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand[.KIND = 1] z]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand[.INPUT = KNOWN PNULL] z]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand[.INPUT = KNOWN (PSTRING ([256]))] z]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)] z]) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = [ERROR_HANDLER_INVOKE perrorcall]])',
        'S_entered = $source_cv_seek(S_pending, 32, 2, 1000)', '$source_cv_stage(S_entered, 32, 2)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$eval_trace_preparser(S_entered, S_entered.CURRENT, pframe) = eps',
        '$call_descriptors_valid(S_entered)',
        'S_returned = $source_cv_seek(S_entered, 32, 3, 1000)', '$source_cv_stage(S_returned, 32, 3)',
        'S_result = $drive_steps(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_NAME_RESULT psourceoperand z) :: ptask_tail*',
        'S_frozen = $drive_steps(S_result[.COMPLETION = NORMAL], 1)',
        'S_frozen.RESULT = KNOWN PNULL', 'S_frozen.TODO = ptask_tail*',
        '$call_descriptors_valid(S_frozen)', 'S_frozen.EVALCONTEXTS = eps', 'S_frozen.FILESEQ = 0',
    ]
    groups['nohandler'] = [
        'S_initial = ' + start('nohandler'),
        'S_before = $source_cv_seek(S_initial, 2, 0, 1000)', '$source_cv_stage(S_before, 2, 0)',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (SOURCE_READ_RESULT psourceoperand) :: ptask_tail*',
        'S_pending.RESULT = KNOWN PNULL', 'S_pending.BASE = BASE_VALUE (KNOWN PNULL)',
        '$call_descriptors_valid(S_pending)', '$task_nodes(SOURCE_READ_RESULT psourceoperand) = eps',
        'S_zero = $drive_steps(S_pending[.COMPLETION = NORMAL], 0)', 'S_zero.TODO = S_pending.TODO',
        'S_done = $drive_steps(S_zero[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EVALCONTEXTS = eps', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    # Keep the original combined throw probe and its timeout; split its exact
    # predicates at reached continuation boundaries under the same 90s cap.
    throw = groups['throw']
    groups['throw-include'] = throw[:29]
    groups['throw-once'] = throw[:4] + [throw[15]] + throw[29:40]
    groups['throw-dynamic'] = throw[:4] + [throw[15]] + throw[29:32] + [throw[34]] + throw[40:]
    return setup, groups



def prepare(out, private_source='private-state'):
    sources = {'mutation': SOURCES / 'eval-mutation.php', 'empty': SOURCES / 'file-empty.php',
               'private': SOURCES / (private_source + '.php'), 'nohandler': SOURCES / 'eval-nohandler.php'}
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    flags = [item for key, value in profile.items() for item in ('-d', key + '=' + value)]
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
        'counts': counts, 'main_premises': sum(counts[name] for name in GROUPS),
        'distinct_premises': 198, 'repeated_throw_setup': 14}) + '\n')
    return counts

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS + ('throw',), action='append')
    parser.add_argument('--private-source', choices=('private-state', 'private-source'), default='private-state')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    selected = args.group or GROUPS
    assert len(selected) == len(set(selected))
    out = Path(tempfile.mkdtemp(prefix='source-undefined-protocol-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', Path(__file__), runner,
               R / 'tests/semantics/error_handler_run.py', R / 'tests/semantics/recorded_worker.py',
               R / 'frontend/worker.php', R / '_build/default/adapter/main.exe',
               R / 'tests/semantics/profile.json', *sorted(SOURCES.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    counts = prepare(out, args.private_source)
    rows = []
    if not args.prepare_only:
        for name in selected:
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
        'selected': selected, 'selected_main_premises': sum(counts[name] for name in selected),
        'private_source': args.private_source,
        'mode': 'SL', 'main_premises': sum(counts[name] for name in GROUPS),
        'distinct_premises': 198, 'repeated_throw_setup': 14, 'prepare_only': args.prepare_only,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}, indent=2) + '\n')
    return args.prepare_only or (len(rows) == len(selected) and all(row['pass'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
