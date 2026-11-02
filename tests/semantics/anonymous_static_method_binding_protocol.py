#!/usr/bin/env python3
"""Source-reached receiverless anonymous static call through argument rebinding."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_method_cases.json'
SOURCE_SHA = 'cf7d7634a0013eb0346c7fc00c7e930ead052fd236eaeefa727b39950ee3d7ff'

PREFIX = r'''
dec $anon_static_output_item(pevent) : ptbytes
def $anon_static_output_item(OUTPUT ptbytes) = ptbytes
def $anon_static_output_item(pevent) = eps -- otherwise
dec $anon_static_output(pevent*) : ptbytes
def $anon_static_output(eps) = eps
def $anon_static_output(pevent :: pevent_tail*) = $anon_static_output_item(pevent) ++ $anon_static_output(pevent_tail*)
dec $anon_static_site(pstate,porigin) : bool
def $anon_static_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprMethodCall expression (NIdentifier (BYTES text) metadata_name) (SEQUENCE phpType7*) metadata)
  -- if $base64(text) = $ptascii("update161Author")
  -- if $source_line(metadata) = 20
def $anon_static_site(S,porigin) = false -- otherwise
dec $anon_static_stage(pstate,nat) : bool
def $anon_static_stage(S,0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_ARGS (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 1 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $anon_static_site(S,porigin_site)
def $anon_static_stage(S,1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 1 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 1)
  -- if $anon_static_site(S,porigin_site)
def $anon_static_stage(S,2) = true
  -- if S.TODO = [TYPE_RECEIVE porigin_method 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = STATIC_METHOD_TARGET porigin_class porigin_method
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $anon_static_site(S,porigin_site)
def $anon_static_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 22
def $anon_static_stage(S,n) = false -- otherwise
dec $anon_static_seek(pstate,nat,nat) : pstate
def $anon_static_seek(S,n_mode,n) = S -- if $anon_static_stage(S,n_mode)
def $anon_static_seek(S,n_mode,0) = S -- if ~$anon_static_stage(S,n_mode)
def $anon_static_seek(S,n_mode,n) = $anon_static_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_static_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $anon_static_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $anon_static_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$anon_static_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_before', 0),
        'S_before.TODO = (NAMED_ARGS (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7_before* 1 pnamedargs_before (porigin_site) z_call) :: ptask_before*',
        'S_before.CURRENT = eps',
        '$class_at(S_before.CLASSES,porigin_class) = (pclassdesc)',
        '$class_method_origin(S_before.CLASSES,porigin_method) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_class',
        'pmethoddesc.NAME = $ptascii("update161Author")',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', 'pmethoddesc.STATIC', '~pmethoddesc.ABSTRACT',
        '$target_function(S_before,STATIC_METHOD_TARGET porigin_class porigin_method) = (pfunction)',
        'pfunction = pmethoddesc.FUNCTION',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_value,psparam_delta]',
        'psparam_value.NAME = $ptascii("value")', 'psparam_delta.NAME = $ptascii("delta")',
        'psparam_value.BYREF', '~psparam_delta.BYREF',
        'psparam_value.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_delta.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '~pfunction.SIGNATURE.BYREF',
        '$call_parameter_reference(S_before,STATIC_METHOD_TARGET porigin_class porigin_method,0)',
        '~$call_parameter_reference(S_before,STATIC_METHOD_TARGET porigin_class porigin_method,1)',
        '$lookup(S_before.ENV,$ptascii("object161Author")) = (n_object_cell)',
        'S_before.STORE[n_object_cell] = DEFINED (POBJECT n_old)',
        'S_before.OBJECTS[n_old] = INSTANCE porigin_class',
        '(HOBJECT n_old) <- S_before.ALLOCATIONS',
        '$lookup(S_before.ENV,$ptascii("value161Author")) = (n_value)',
        'S_before.STORE[n_value] = DEFINED (PINT 9)',
        'pnamedargs_before.SLOTS = [NAMED_SENT (REFERENCE n_value)]',
        'pnamedargs_before.NAMED = eps',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class porigin_method) = eps',
        '$target_receiver(S_before,STATIC_METHOD_TARGET porigin_class porigin_method) = eps',
        '$method_call_selected(S_before,STATIC_METHOD_TARGET porigin_class porigin_method,(porigin_site))',
        '$call_task_valid(S_before,S_before.TODO[0])',
        '$anon_static_output(S_before.EVENTS) = $ptascii("5|5|9|9|later|")',
        '$class_state_valid(S_before)', '$call_descriptors_valid(S_before)', '$heap_valid($heap_graph(S_before))',
        *seek('S_before', 'S_after', 1),
        'S_after.TODO = (NAMED_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7_after* 1 pnamedargs_after (porigin_site) z_call) :: ptask_after*',
        'S_after.RESULT = KNOWN (PINT 1)', 'S_after.CURRENT = eps',
        'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_value)]',
        'pnamedargs_after.NAMED = eps',
        'S_after.STORE[n_object_cell] = DEFINED PNULL',
        'S_after.STORE[n_value] = DEFINED (PINT 9)',
        'S_after.OBJECTS[n_old] = INSTANCE porigin_class',
        '~((HOBJECT n_old) <- S_after.ALLOCATIONS)',
        '$anon_static_output(S_after.EVENTS) = $ptascii("5|5|9|9|later|arg|drop|rebound|")',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class porigin_method) = eps',
        '$target_function(S_after,STATIC_METHOD_TARGET porigin_class porigin_method) = (pfunction)',
        '$method_call_selected(S_after,STATIC_METHOD_TARGET porigin_class porigin_method,(porigin_site))',
        '$call_task_valid(S_after,S_after.TODO[0])',
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        *seek('S_after', 'S_type', 2),
        'S_type.TODO = [TYPE_RECEIVE porigin_method 0]',
        'S_type.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = STATIC_METHOD_TARGET porigin_class porigin_method',
        'pcallcontext.INSTANCE = eps', 'pcallcontext.RECEIVER = eps',
        'pcallcontext.LEXICAL_CLASS = (porigin_class)',
        'pcallcontext.CALLED_CLASS = (porigin_class)',
        'pcallcontext.CALLSITE = (porigin_site)',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
        '$lookup(S_type.ENV,$ptascii("value")) = (n_value)',
        'S_type.STORE[n_value] = DEFINED (PINT 9)',
        '$lookup(S_type.ENV,$ptascii("delta")) = (n_delta)',
        'S_type.STORE[n_delta] = DEFINED (PINT 1)',
        '$call_task_valid(S_type,TYPE_RECEIVE porigin_method 0)',
        '$missing_argument_function_name(S_type,pfunction) = $ptascii("class@anonymous::update161Author")',
        '$return_function_name(S_type,pfunction) = $ptascii("class@anonymous::update161Author")',
        '$call_function_kind(S_type) = $ptascii("method")',
        '$missing_argument_function_name(S_type,pfunction[.NAME = $ptascii("forged")]) = $call_function_name(S_type,pfunction[.NAME = $ptascii("forged")])',
        '$return_function_name(S_type,pfunction[.NAME = $ptascii("forged")]) = $call_function_name(S_type,pfunction[.NAME = $ptascii("forged")])',
        '$call_current_valid(S_type)', '$call_descriptors_valid(S_type)', '$heap_valid($heap_graph(S_type))',
        *seek('S_type', 'S_root', 3),
        'S_root.CURRENT = eps',
        'S_root.STORE[n_object_cell] = DEFINED PNULL',
        'S_root.STORE[n_value] = DEFINED (PINT 10)',
        '$anon_static_output(S_root.EVENTS) = $ptascii("5|5|9|9|later|arg|drop|rebound|10|10|gone|")',
        '$class_state_valid(S_root)', '$call_descriptors_valid(S_root)', '$heap_valid($heap_graph(S_root))',
        'S_done = $drive_steps(S_root,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.CURRENT = eps',
        '$anon_static_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-static-binding-', dir=ROOT / '.tools'))
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
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks)-2,
                      derived_conditions=2, derived_guards=2, fixture_sha256=sha(fixture))
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
