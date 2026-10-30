#!/usr/bin/env python3
"""Captured own/inherited method diagnostics and the retained real receiver."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_captured_method_cases.json'
SOURCE_SHA = '7c9654cd64ebb349af107f88911a3b76cf6b8d6592491b2f6976f7070c5350a5'
PREFIX = r'''
dec $ac162_output_item(pevent) : ptbytes
def $ac162_output_item(OUTPUT ptbytes) = ptbytes
def $ac162_output_item(pevent) = eps -- otherwise
dec $ac162_output(pevent*) : ptbytes
def $ac162_output(eps) = eps
def $ac162_output(pevent :: pevent_tail*) = $ac162_output_item(pevent) ++ $ac162_output(pevent_tail*)
dec $ac162_root_echo(pstate,int) : bool
def $ac162_root_echo(S,z) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = z
def $ac162_root_echo(S,z) = false -- otherwise
dec $ac162_missing(pstate,ptbytes) : bool
def $ac162_missing(S,ptbytes_name) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 1]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.FUNCTION = porigin
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = ptbytes_name
def $ac162_missing(S,ptbytes_name) = false -- otherwise
dec $ac162_stage(pstate,nat) : bool
def $ac162_stage(S,0) = $ac162_root_echo(S,15)
def $ac162_stage(S,1) = $ac162_missing(S,$ptascii("needOwn"))
def $ac162_stage(S,2) = $ac162_missing(S,$ptascii("needBase"))
def $ac162_stage(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 8
def $ac162_stage(S,4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 31
def $ac162_stage(S,5) = $ac162_root_echo(S,32)
def $ac162_stage(S,n) = false -- otherwise
dec $ac162_seek(pstate,nat,nat) : pstate
def $ac162_seek(S,n_stage,n) = S -- if $ac162_stage(S,n_stage)
def $ac162_seek(S,n_stage,0) = S -- if ~$ac162_stage(S,n_stage)
def $ac162_seek(S,n_stage,n) = $ac162_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ac162_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ac162_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $ac162_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$ac162_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    assert stdout.endswith(b'owner-drop|after')
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_start', 0),
        '~$named_defined(S_start,$ptascii("owner162Review"))',
    ]
    for label, variable, lexical in [
        ('own', 'own162Review', 'porigin_class_owner'),
        ('base', 'base162Review', 'porigin_class_base'),
        ('wrong', 'wrong162Review', 'porigin_class_owner'),
    ]:
        checks += [
            f'$lookup(S_start.ENV,$ptascii("{variable}")) = (n_cell_{label})',
            f'S_start.STORE[n_cell_{label}] = DEFINED (POBJECT n_capture_{label})',
            f'(HOBJECT n_capture_{label}) <- S_start.ALLOCATIONS',
            f'$object_body(S_start.OBJECTS[n_capture_{label}]) = METHODCLOSURE porigin_method_{label} porigin_site_{label} porigin_class_owner eps',
            f'$closure_scope_at(S_start.CLOSURESCOPES,n_capture_{label}) = (pclosurescope_{label})',
            f'pclosurescope_{label}.LEXICAL = {lexical}',
            f'pclosurescope_{label}.CALLED = porigin_class_owner',
            f'pclosurescope_{label}.RECEIVER = (n_owner)',
            f'pclosurescope_{label}.CREATION = eps',
            f'$method_closure_scope_valid(S_start,pclosurescope_{label})',
            f'$node_children(S_start,HOBJECT n_capture_{label}) = [HOBJECT n_owner]',
        ]
    checks += [
        'S_start.CLOSURESCOPES = [pclosurescope_own,pclosurescope_base,pclosurescope_wrong]',
        '(HOBJECT n_owner) <- S_start.ALLOCATIONS',
        '$object_body(S_start.OBJECTS[n_owner]) = INSTANCE porigin_class_owner',
        '~(n_owner <- S_start.DESTRUCTION.CALLED)',
        '$class_at(S_start.CLASSES,porigin_class_owner) = (pclassdesc_owner)',
        '$class_at(S_start.CLASSES,porigin_class_base) = (pclassdesc_base)',
        'porigin_class_owner =/= porigin_class_base',
        'pclassdesc_base.NAME = $ptascii("Base162Review")',
        '$ac162_output(S_start.EVENTS) = eps',
        '$class_state_valid(S_start)', '$call_descriptors_valid(S_start)',
        '$heap_valid($heap_graph(S_start))',
        *seek('S_start', 'S_own', 1),
        'S_own.CURRENT = (pcallcontext_own)',
        'pcallcontext_own.TARGET = CLOSURE_TARGET n_capture_own',
        'pcallcontext_own.INSTANCE = (n_capture_own)',
        'pcallcontext_own.FUNCTION = porigin_method_own',
        'pcallcontext_own.RECEIVER = (n_owner)',
        'pcallcontext_own.LEXICAL_CLASS = (porigin_class_owner)',
        'pcallcontext_own.CALLED_CLASS = (porigin_class_owner)',
        'pcallcontext_own.ARGC = 1', 'pcallcontext_own.HOLES = eps',
        '$class_method_origin(S_own.CLASSES,porigin_method_own) = (pmethoddesc_own)',
        '$target_function(S_own,CLOSURE_TARGET n_capture_own) = (pfunction_own)',
        '$method_closure_functions(S_own,n_capture_own,pmethoddesc_own) = (pfunction_own,pfunction_own)',
        'pfunction_own = pmethoddesc_own.FUNCTION',
        'pfunction_own.NAME = pclassdesc_owner.NAME ++ $ptascii("::needOwn")',
        '$captured_method_diagnostic(S_own) = (pmethoddesc_own)',
        '$missing_argument_function_name(S_own,pfunction_own) = $c_string(pclassdesc_owner.NAME) ++ $ptascii("::needOwn")',
        '$call_function_name(S_own,pfunction_own) = pfunction_own.NAME',
        '$call_function_kind(S_own) = $ptascii("method")',
        '$missing_argument_function_name(S_own,pfunction_own[.NAME = $ptascii("forged")]) = $call_function_name(S_own,pfunction_own[.NAME = $ptascii("forged")])',
        '$captured_method_diagnostic(S_own[.CLOSURESCOPES = [pclosurescope_own[.LEXICAL = porigin_class_base],pclosurescope_base,pclosurescope_wrong]][.CURRENT = (pcallcontext_own[.LEXICAL_CLASS = (porigin_class_base)])]) = eps',
        '$call_task_valid(S_own,TYPE_RECEIVE porigin_method_own 1)',
        '$ac162_output(S_own.EVENTS) = $ptascii("before|")',
        '$call_current_valid(S_own)', '$call_descriptors_valid(S_own)',
        '$heap_valid($heap_graph(S_own))',
        *seek('S_own', 'S_base', 2),
        'S_base.CURRENT = (pcallcontext_base)',
        'pcallcontext_base.TARGET = CLOSURE_TARGET n_capture_base',
        'pcallcontext_base.INSTANCE = (n_capture_base)',
        'pcallcontext_base.FUNCTION = porigin_method_base',
        'pcallcontext_base.RECEIVER = (n_owner)',
        'pcallcontext_base.LEXICAL_CLASS = (porigin_class_base)',
        'pcallcontext_base.CALLED_CLASS = (porigin_class_owner)',
        '$class_method_origin(S_base.CLASSES,porigin_method_base) = (pmethoddesc_base)',
        'pmethoddesc_base.OWNER = porigin_class_base',
        '$target_function(S_base,CLOSURE_TARGET n_capture_base) = (pfunction_base)',
        '$captured_method_diagnostic(S_base) = (pmethoddesc_base)',
        '$missing_argument_function_name(S_base,pfunction_base) = $ptascii("Base162Review::needBase")',
        '$call_function_name(S_base,pfunction_base) = $ptascii("Base162Review::needBase")',
        '$call_task_valid(S_base,TYPE_RECEIVE porigin_method_base 1)',
        '$call_current_valid(S_base)', '$call_descriptors_valid(S_base)',
        '$heap_valid($heap_graph(S_base))',
        *seek('S_base', 'S_return', 3),
        'S_return.CURRENT = (pcallcontext_return)',
        'pcallcontext_return.TARGET = CLOSURE_TARGET n_capture_wrong',
        'pcallcontext_return.INSTANCE = (n_capture_wrong)',
        'pcallcontext_return.FUNCTION = porigin_method_wrong',
        'pcallcontext_return.RECEIVER = (n_owner)',
        '$target_function(S_return,CLOSURE_TARGET n_capture_wrong) = (pfunction_wrong)',
        '$class_method_origin(S_return.CLASSES,porigin_method_wrong) = (pmethoddesc_wrong)',
        '$captured_method_diagnostic(S_return) = (pmethoddesc_wrong)',
        '$return_function_name(S_return,pfunction_wrong) = $c_string(pclassdesc_owner.NAME) ++ $ptascii("::wrongOwn")',
        '$call_function_name(S_return,pfunction_wrong) = pfunction_wrong.NAME',
        '$return_function_name(S_return,pfunction_wrong[.NAME = $ptascii("forged")]) = $call_function_name(S_return,pfunction_wrong[.NAME = $ptascii("forged")])',
        '$call_current_valid(S_return)', '$call_descriptors_valid(S_return)',
        '$heap_valid($heap_graph(S_return))',
        *seek('S_return', 'S_unset', 4),
        '(HOBJECT n_owner) <- S_unset.ALLOCATIONS',
        '~(n_owner <- S_unset.DESTRUCTION.CALLED)',
        '$ac162_output(S_unset.EVENTS) = ' + term(stdout.removesuffix(b'owner-drop|after')),
        *seek('S_unset', 'S_released', 5),
        '~((HOBJECT n_capture_own) <- S_released.ALLOCATIONS)',
        '~((HOBJECT n_capture_base) <- S_released.ALLOCATIONS)',
        '~((HOBJECT n_capture_wrong) <- S_released.ALLOCATIONS)',
        '~((HOBJECT n_owner) <- S_released.ALLOCATIONS)',
        'n_owner <- S_released.DESTRUCTION.CALLED',
        '$ac162_output(S_released.EVENTS) = ' + term(stdout.removesuffix(b'after')),
        '$class_state_valid(S_released)', '$call_descriptors_valid(S_released)',
        '$heap_valid($heap_graph(S_released))',
        'S_done = $drive_steps(S_released,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ac162_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-captured-method-owner-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source, Path(__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': SOURCE_SHA, 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        checks = assertions(checked['fixture'], os.fsencode(source), stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks)-3,
                      derived_conditions=3, derived_guards=3, fixture_sha256=sha(fixture))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
