#!/usr/bin/env python3
"""Source-reached SET callbacks nested in typed static conversion."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).with_name('typed_static_set_cases.json')
PREFIX = r'''
dec $set_static_entered(pstate) : bool
def $set_static_entered(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe_config :: pframe_static :: pframe_tail*
  -- if pframe_config.TODO = (STRINGIFY_RESULT n_inner porigin_config z_call) :: (CONFIG_STRING_RESULT pconfigcall n_inner porigin_config z_child z_call) :: ptask_config_tail*
  -- if pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH
  -- if pframe_static.TODO = (STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_static_tail*
  -- if pcallcontext.TARGET = METHOD_TARGET n_inner porigin_method
def $set_static_entered(S) = false -- otherwise
dec $set_static_phase(pstate,nat) : bool
def $set_static_phase(S,0) = $set_static_entered(S)
def $set_static_phase(S,1) = true
  -- if $set_static_entered(S)
  -- if S.FILEINCLUDEPATH = ($ptascii("inner"))
def $set_static_phase(S,2) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_inner porigin_config z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH
  -- if S.RESULT = KNOWN (PSTRING $ptascii("outer"))
def $set_static_phase(S,3) = true
  -- if S.TODO = (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING $ptascii("s"))
def $set_static_phase(S,4) = true
  -- if $set_static_entered(S)
  -- if S.TODO = (FINALLY_RESUME porigin_try (n_exception)) :: (FINALLY_PHASE porigin_try 1) :: ptask_tail*
def $set_static_phase(S,n) = false -- otherwise
dec $set_static_seek(pstate,nat,nat) : pstate
def $set_static_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $set_static_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $set_static_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if $set_static_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $set_static_seek(S,n_phase,0) = S
  -- if ~S.COMPILESTOP
  -- if ~$set_static_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $set_static_seek(S,n_phase,n) = $set_static_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if $(n > 0)
  -- if ~$set_static_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $set_static_output_marker(pevent) : bool
def $set_static_output_marker(OUTPUT ptbytes) = true
def $set_static_output_marker(pevent) = false -- otherwise
dec $set_static_outputs(pevent*) : ptbytes
def $set_static_outputs(eps) = eps
def $set_static_outputs((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $set_static_outputs(pevent_tail*)
def $set_static_outputs(pevent :: pevent_tail*) = $set_static_outputs(pevent_tail*)
  -- if ~$set_static_output_marker(pevent)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def byte_expr(data):
    return '$base64(' + json.dumps(b64(data)) + ')'


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def no_directory(state, cwd):
    return [f'{state}.FILECWD = ({byte_expr(os.fsencode(cwd))})',
            f'{state}.DIRSEQ = 0', f'{state}.DIRCONVSEQ = 0',
            f'{state}.DIRCONVERSIONS = eps', f'{state}.DIRCONTEXT = eps',
            f'{state}.REFCOERCIONS = eps']


def seek(state, previous, phase):
    return [f'{state}_found = $set_static_seek({previous},{phase},2048)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$set_static_phase({state},{phase})']


def common(checked, path, cwd):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + byte_expr(os.fsencode(path)) + ',' + byte_expr(os.fsencode(cwd)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S', 'S_initial', 0)]
    checks += r'''
S.FILEINCLUDEPATH = ($ptascii("seed"))
$set_static_outputs(S.EVENTS) = $ptascii("T")
S.CURRENT = (pcallcontext_inner)
S.FRAMES = pframe_config :: pframe_static :: pframe_tail*
pframe_config.TODO = (STRINGIFY_RESULT n_inner porigin_config z_call) :: (CONFIG_STRING_RESULT pconfigcall n_inner porigin_config z_child z_call) :: ptask_config_tail*
pframe_static.TODO = (STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_static_tail*
pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH
pconfigcall.NAMED
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_inner))]
pconfigcall.OWNER = eps
pconfigcall.SELECTION = eps
pconfigcall.PACKS = eps
pcallcontext_inner.TARGET = METHOD_TARGET n_inner porigin_inner_method
pcallcontext_inner.INSTANCE = eps
pcallcontext_inner.RECEIVER = (n_inner)
pcallcontext_inner.LEXICAL_CLASS = (porigin_q)
pcallcontext_inner.CALLED_CLASS = (porigin_q)
pframe_config.CONTEXT = (pcallcontext_outer)
pcallcontext_outer.TARGET = METHOD_TARGET n_outer porigin_outer_method
pcallcontext_outer.INSTANCE = eps
pcallcontext_outer.RECEIVER = (n_outer)
pcallcontext_outer.LEXICAL_CLASS = (porigin_p)
pcallcontext_outer.CALLED_CLASS = (porigin_d)
pframe_static.CONTEXT = (pcallcontext_caller)
pcallcontext_caller.TARGET = STATIC_METHOD_TARGET porigin_b porigin_set
pcallcontext_caller.INSTANCE = eps
pcallcontext_caller.RECEIVER = eps
pcallcontext_caller.LEXICAL_CLASS = (porigin_a)
pcallcontext_caller.CALLED_CLASS = (porigin_b)
porigin_b =/= porigin_a
porigin_d =/= porigin_p
pstaticstring.CLASS = porigin_a
pstaticstring.OBJECT = n_outer
pstaticstring.SITE = porigin_static
pstaticstring.LINE = z_static
pstaticstring.NAME = $ptascii("p")
pstaticstring.RHS = KNOWN (POBJECT n_outer)
S.GLOBALTABLE = (psymboltable)
$trace_slot(S,psymboltable.ENV,$ptascii("spareq")) = POBJECT n_spare_inner
$trace_slot(S,psymboltable.ENV,$ptascii("spared")) = POBJECT n_spare_outer
n_spare_inner =/= n_inner
n_spare_outer =/= n_outer
n_outer =/= n_inner
S.OBJECTS[n_inner] = INSTANCE porigin_q
S.OBJECTS[n_spare_inner] = INSTANCE porigin_q
S.OBJECTS[n_outer] = INSTANCE porigin_d
S.OBJECTS[n_spare_outer] = INSTANCE porigin_d
(HOBJECT n_inner) <- S.ALLOCATIONS
(HOBJECT n_spare_inner) <- S.ALLOCATIONS
(HOBJECT n_outer) <- S.ALLOCATIONS
(HOBJECT n_spare_outer) <- S.ALLOCATIONS
$task_nodes(STATIC_STRING_RESULT pstaticstring) = eps
$task_nodes(STATIC_STRING_CAPTURE pstaticstring) = [HOBJECT n_outer]
(HOBJECT n_inner) <- $task_nodes(CONFIG_STRING_RESULT pconfigcall n_inner porigin_config z_child z_call)
$config_string_site_valid(S,pconfigcall,n_inner,porigin_config,z_child,z_call)
$config_string_trace_context(S,pcallcontext_inner)
$static_string_record_valid(S,pstaticstring)
$static_string_task_valid(S[.CURRENT = pframe_static.CONTEXT][.ORIGIN = pframe_static.ORIGIN][.TODO = pframe_static.TODO],pstaticstring)
$class_static_at(S.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_before)
pclassstatic_before.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("old")))
~$reference_coercion_producer(S,n_outer,porigin_static,z_static)
'''.strip().splitlines()
    for name, origin in [('Q', 'q'), ('P', 'p'), ('D', 'd'), ('A', 'a'), ('B', 'b')]:
        checks += [f'$class_at(S.CLASSES,porigin_{origin}) = (pclassdesc_{origin})',
                   f'pclassdesc_{origin}.NAME = $ptascii("{name}")']
    checks += valid('S') + no_directory('S', cwd)
    config = '(STRINGIFY_RESULT n_inner porigin_config z_call) :: (CONFIG_STRING_RESULT __RECORD__ n_inner porigin_config z_child z_call) :: ptask_config_tail*'
    static = '(STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT __RECORD__) :: (STATIC_STRING_CAPTURE __RECORD__) :: ptask_static_tail*'
    mutations = {
        'inner_receiver': 'S[.CURRENT = (pcallcontext_inner[.RECEIVER = (n_spare_inner)])]',
        'inner_instance': 'S[.CURRENT = (pcallcontext_inner[.INSTANCE = (n_inner)])]',
        'inner_target': 'S[.CURRENT = (pcallcontext_inner[.TARGET = METHOD_TARGET n_spare_inner porigin_inner_method])]',
        'outer_receiver': 'S[.FRAMES = pframe_config[.CONTEXT = (pcallcontext_outer[.RECEIVER = (n_spare_outer)])] :: pframe_static :: pframe_tail*]',
        'static_instance': 'S[.FRAMES = pframe_config :: pframe_static[.CONTEXT = (pcallcontext_caller[.INSTANCE = (n_outer)])] :: pframe_tail*]',
        'called_class': 'S[.FRAMES = pframe_config :: pframe_static[.CONTEXT = (pcallcontext_caller[.CALLED_CLASS = (porigin_a)])] :: pframe_tail*]',
    }
    for name, replacement in [('named', 'pconfigcall[.NAMED = false]'),
                              ('sent', 'pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT n_spare_inner))]]'),
                              ('config_line', 'pconfigcall[.LINE = $(z_call + 1)]')]:
        mutations[name] = 'S[.FRAMES = pframe_config[.TODO = ' + config.replace('__RECORD__', replacement) + '] :: pframe_static :: pframe_tail*]'
    for name, replacement in [('property_object', 'pstaticstring[.OBJECT = n_spare_outer]'),
                              ('property_line', 'pstaticstring[.LINE = $(z_static + 1)]'),
                              ('property_site', 'pstaticstring[.SITE = porigin_config]')]:
        mutations[name] = 'S[.FRAMES = pframe_config :: pframe_static[.TODO = ' + static.replace('__RECORD__', replacement) + '] :: pframe_tail*]'
    for name, todo in [
        ('missing_capture', '(STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT pstaticstring) :: ptask_static_tail*'),
        ('duplicate_capture', '(STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_static_tail*'),
        ('wrapped_capture', '(STRINGIFY_RESULT n_outer porigin_static z_static) :: (STATIC_STRING_RESULT pstaticstring) :: (AT porigin_static (STATIC_STRING_CAPTURE pstaticstring)) :: ptask_static_tail*'),
        ('wrapped_scratch', '(AT porigin_static (STRINGIFY_RESULT n_outer porigin_static z_static)) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_static_tail*')]:
        mutations[name] = 'S[.FRAMES = pframe_config :: pframe_static[.TODO = ' + todo + '] :: pframe_tail*]'
    for name, expression in mutations.items():
        state = 'S_bad_' + name
        checks += [state + ' = ' + expression, f'$heap_valid($heap_graph({state}))',
                   f'~$call_descriptors_valid({state})']
    checks += seek('S_inner', 'S', 1)
    checks += ['S_inner.CURRENT = S.CURRENT', 'S_inner.FRAMES = S.FRAMES',
               'S_inner.FILEINCLUDEPATH = ($ptascii("inner"))',
               '$set_static_outputs(S_inner.EVENTS) = $ptascii("TN")',
               '$class_static_at(S_inner.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_before)']
    checks += valid('S_inner') + no_directory('S_inner', cwd)
    return checks


def normal(checks, cwd):
    checks += seek('S_ready', 'S_inner', 2)
    checks += ['S_ready.TODO = (CONFIG_STRING_RESULT pconfigcall n_inner porigin_config z_child z_call) :: ptask_ready_tail*',
               'S_ready.FILEINCLUDEPATH = ($ptascii("inner"))',
               'S_ready.CURRENT = pframe_config.CONTEXT',
               'S_ready.FRAMES = pframe_static :: pframe_tail*',
               'S_ready.RESULT = KNOWN (PSTRING $ptascii("outer"))']
    checks += valid('S_ready') + no_directory('S_ready', cwd)
    checks += ['S_set_found = $drive_steps(S_ready,1)',
               'S_set_found.COMPLETION = BUDGET',
               'S_set = S_set_found[.COMPLETION = NORMAL]',
               'S_set.FILEINCLUDEPATH = ($ptascii("outer"))',
               'S_set.RESULT = KNOWN (PSTRING $ptascii("inner"))',
               'S_set.CURRENT = S_ready.CURRENT', 'S_set.FRAMES = S_ready.FRAMES',
               '$class_static_at(S_set.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_before)',
               '$static_string_task_valid(S_set[.CURRENT = pframe_static.CONTEXT][.ORIGIN = pframe_static.ORIGIN][.TODO = pframe_static.TODO],pstaticstring)']
    checks += valid('S_set') + no_directory('S_set', cwd)
    checks += seek('S_write', 'S_set', 3)
    checks += ['S_write.FILEINCLUDEPATH = ($ptascii("outer"))',
               'S_write.CURRENT = pframe_static.CONTEXT',
               'S_write.FRAMES = pframe_tail*',
               '$class_static_at(S_write.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_before)',
               '$static_string_task_valid(S_write,pstaticstring)',
               'S_bad_result = S_write[.RESULT = KNOWN (PINT 0)]',
               '$heap_valid($heap_graph(S_bad_result))',
               '~$call_descriptors_valid(S_bad_result)',
               'S_done = $drive_steps(S_write,2048)', 'S_done.COMPLETION = NORMAL',
               '$set_static_outputs(S_done.EVENTS) = $ptascii("TNinners|s|outer")',
               'S_done.FILEINCLUDEPATH = ($ptascii("end"))',
               '$class_static_at(S_done.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_done)',
               'pclassstatic_done.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("s")))']
    return terminal(checks, cwd)


def abrupt(checks, cwd):
    checks += seek('S_final', 'S_inner', 4)
    checks += ['S_final.CURRENT = S.CURRENT', 'S_final.FRAMES = S.FRAMES',
               'S_final.FILEINCLUDEPATH = ($ptascii("inner"))',
               'S_final.TODO = (FINALLY_RESUME porigin_try (n_exception)) :: (FINALLY_PHASE porigin_try 1) :: ptask_final_tail*',
               '$set_static_outputs(S_final.EVENTS) = $ptascii("TNF")',
               '$throwable_member(S_final,n_exception)',
               '$object_name(S_final,n_exception) = $ptascii("Exception")',
               '$throwable_field(S_final,n_exception,"line") = PINT 20',
               '$throwable_field(S_final,n_exception,"message") = PSTRING $ptascii("X")',
               '(HOBJECT n_exception) <- $task_nodes(FINALLY_RESUME porigin_try (n_exception))',
               '$finally_state_valid(S_final)', '~$throwable_member(S_final,n_spare_inner)',
               'S_bad_phase = S_final[.TODO = (FINALLY_RESUME porigin_try (n_exception)) :: (FINALLY_PHASE porigin_try 0) :: ptask_final_tail*]',
               '$heap_valid($heap_graph(S_bad_phase))', '~$call_descriptors_valid(S_bad_phase)',
               'S_bad_exception = S_final[.TODO = (FINALLY_RESUME porigin_try (n_spare_inner)) :: (FINALLY_PHASE porigin_try 1) :: ptask_final_tail*]',
               '$heap_valid($heap_graph(S_bad_exception))', '~$call_descriptors_valid(S_bad_exception)',
               '$throwable_field(S_final,n_exception,"trace") = PARRAY n_trace']
    checks += valid('S_final') + no_directory('S_final', cwd)
    checks += ['S_done = $drive_steps(S_final,2048)', 'S_done.COMPLETION = UNCAUGHT n_exception',
               '$set_static_outputs(S_done.EVENTS) = $ptascii("TNF")',
               'S_done.FILEINCLUDEPATH = ($ptascii("inner"))',
               '$class_static_at(S_done.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic_before)',
               '$throwable_field(S_done,n_exception,"trace") = PARRAY n_trace',
               '$throwable_field(S_done,n_exception,"line") = PINT 20',
               '(HOBJECT n_exception) <- S_done.ALLOCATIONS']
    return terminal(checks, cwd, trace_retains_inner=True)


def terminal(checks, cwd, trace_retains_inner=False):
    checks += [f'S_done.{field} = eps' for field in ['TODO', 'FRAMES', 'CURRENT', 'ORIGIN', 'TRACE']]
    checks += [f'$heap_count(HOBJECT {obj},$heap_graph(S_done).ROOTS) = 0' for obj in ['n_inner', 'n_outer']]
    if trace_retains_inner:
        checks += ['(HOBJECT n_inner) <- S_done.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_done),HOBJECT n_inner) =/= 0']
    else:
        checks += ['~((HOBJECT n_inner) <- S_done.ALLOCATIONS)']
    checks += ['~((HOBJECT n_outer) <- S_done.ALLOCATIONS)']
    return checks + valid('S_done') + no_directory('S_done', cwd)


def snapshot(freeze_path):
    identity = {key: subprocess.check_output(['git', *argv], cwd=ROOT, text=True).strip()
                for key, argv in [('head', ['rev-parse', 'HEAD']),
                                  ('status', ['status', '--porcelain', '--untracked-files=all'])]}
    fingerprint = types.syntax_validation.implementation_fingerprint()
    result = {'identity': identity, 'fingerprint': fingerprint,
              'ordered_modules': json.loads((ROOT / 'spec/semantics/modules.json').read_text())}
    if freeze_path:
        freeze = json.loads(freeze_path.read_text())
        assert identity == {'head': freeze['head'], 'status': ''}
        assert result['ordered_modules'] == freeze['ordered_modules']
        result['watched'] = {name: {'sha256': sha(ROOT / name),
                                   'mode': oct((ROOT / name).stat().st_mode & 0o7777)}
                             for name in freeze['watched']}
        assert {k: v['sha256'] for k, v in result['watched'].items()} == freeze['watched']
        assert {k: v['mode'] for k, v in result['watched'].items()} == freeze['file_modes']
        result['freeze'] = {'sha256': sha(freeze_path),
                            'mode': oct(freeze_path.stat().st_mode & 0o7777)}
    return result


def process(command, directory, timeout, cwd):
    directory.mkdir()
    (directory / 'command.json').write_text(json.dumps({'argv': command, 'cwd': str(cwd),
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'other': 'inherited'}, 'timeout': timeout}) + '\n')
    try:
        result = subprocess.run(command, cwd=cwd, env=types.ENV, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        (directory / 'stdout').write_bytes(error.stdout or b'')
        (directory / 'stderr').write_bytes(error.stderr or b'')
        (directory / 'process.json').write_text(json.dumps({'status': 'timeout', 'timeout': timeout}) + '\n')
        raise
    (directory / 'stdout').write_bytes(result.stdout)
    (directory / 'stderr').write_bytes(result.stderr)
    (directory / 'process.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode,
                                                       'timeout': timeout}) + '\n')
    return result


def checked(row, directory, path):
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'] is True
            value = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert value['ok'] is True
        finally:
            adapter.close()
    finally:
        frontend.close()
    checks = common(value, path, directory)
    checks = abrupt(checks, directory) if row['abrupt'] else normal(checks, directory)
    body = 'dec $body() : bool\ndef $body() = true\n'
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, checks


def numeric(fixture, directory):
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                      *[str(ROOT / name) for name in modules], str(fixture)], directory / 'numeric', 300, ROOT)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr


def source(row, directory, path):
    observed = process([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, str(path)],
                       directory / 'native', 30, directory)
    assert observed.returncode == (255 if row['abrupt'] else 0)
    assert observed.stdout == row['expected_stdout'].encode()
    if row['abrupt']:
        prefix = b'Fatal error: Uncaught Exception: X in ' + os.fsencode(path) + b':20\nStack trace:\n'
        assert observed.stderr.startswith(prefix)
        assert observed.stderr.endswith(b'  thrown in ' + os.fsencode(path) + b' on line 20\n')
    else:
        assert not observed.stderr
    facts = {'version': 2, 'main': b64(os.fsencode(path)), 'cwd': b64(os.fsencode(directory)),
             'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    result = process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
                      str(facts_path), '--steps', '100000', '--timeout', '60'],
                     directory / 'model', 90, directory)
    assert result.returncode == 0 and not result.stderr
    outcome = json.loads(result.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == ('php_error' if row['abrupt'] else 'normal')
    assert outcome['exit_status'] == observed.returncode and outcome['reason'] is None
    assert base64.b64decode(outcome['stdout'], validate=True) == observed.stdout
    assert base64.b64decode(outcome['stderr'], validate=True) == observed.stderr
    if row['abrupt']:
        assert outcome['diagnostic']['class'] == 'Exception' and outcome['diagnostic']['line'] == 20
        assert base64.b64decode(outcome['diagnostic']['message'], validate=True) == b'X'
    return {'status': outcome['status'], 'exit_status': outcome['exit_status']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'source', 'finite'])
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    assert args.mode == 'prepare' or args.freeze, 'Runtime modes require the independently reviewed freeze'
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='typed-static-set-' + args.mode + '-', dir=ROOT / '.tools'))
    report = {'scope': 'Two original SET172 / user-string168 / typed-static197 source witnesses',
              'profile': types.PROFILE, 'mode': args.mode, 'before': before, 'records': [],
              'passed': False, 'state_assertions_evaluated': 0, 'unused_body_assertions': 0}
    print(out, flush=True)
    try:
        for row in json.loads(CASES.read_text())['cases']:
            record = {'case': row['case'], 'completed': False}
            report['records'].append(record)
            directory = out / row['case']
            directory.mkdir()
            path = directory / 'main.php'
            path.write_text(row['source'])
            assert sha(path) == row['source_sha256']
            record['source_sha256'] = sha(path)
            if args.mode == 'source':
                record['outcome'] = source(row, directory, path)
            else:
                body, checks = checked(row, directory, path)
                (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
                fixture = directory / 'protocol.watsup'
                fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = '
                                   + ('true' if args.mode == 'prepare' else '$body()') + '\n')
                numeric(fixture, directory)
                record['body_assertions'] = len(checks)
                report['unused_body_assertions' if args.mode == 'prepare'
                       else 'state_assertions_evaluated'] += len(checks)
            assert snapshot(args.freeze) == before
            record['completed'] = True
            print(row['case'], 'prepared' if args.mode == 'prepare' else 'pass', flush=True)
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        try:
            report['after'] = snapshot(args.freeze)
            report['passed'] = report['passed'] and report['after'] == before
        except BaseException as error:
            report['after_error'] = {'type': type(error).__name__, 'message': str(error)}
            report['passed'] = False
        report['raw_files'] = {str(path.relative_to(ROOT)): {'sha256': sha(path),
            'bytes': path.stat().st_size, 'mode': oct(path.stat().st_mode & 0o7777)}
            for path in sorted(out.rglob('*')) if path.is_file()}
        receipt = out / 'report.json'
        receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        print(receipt, sha(receipt), 'pass', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
