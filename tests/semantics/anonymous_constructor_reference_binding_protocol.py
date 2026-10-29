#!/usr/bin/env python3
"""Real anonymous constructor reference capture, rebinding and typed reception."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_reference_cases.json'
SOURCE_SHA = '65f2ad6dabc0935f288005161bc0cd5ed7ee52eb651ff3b67a225a9d07674ae6'

PREFIX = r'''
dec $ref_binding_output_item(pevent) : ptbytes
def $ref_binding_output_item(OUTPUT ptbytes) = ptbytes
def $ref_binding_output_item(pevent) = eps -- otherwise
dec $ref_binding_output(pevent*) : ptbytes
def $ref_binding_output(eps) = eps
def $ref_binding_output(pevent :: pevent_tail*) = $ref_binding_output_item(pevent) ++ $ref_binding_output(pevent_tail*)
dec $ref_binding_site(pstate,porigin,int) : bool
def $ref_binding_site(S,porigin,z_line) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata) = z_line
def $ref_binding_site(S,porigin,z_line) = false -- otherwise
dec $ref_binding_stage(pstate,nat) : bool
def $ref_binding_stage(S,0) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 2 poperand* (porigin_site) z) :: ptask_tail*
  -- if $ref_binding_site(S,porigin_site,5)
def $ref_binding_stage(S,1) = true
  -- if S.TODO = (NAMED_ARGS (METHOD_TARGET n porigin) eps 2 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $ref_binding_site(S,porigin_site,17)
def $ref_binding_stage(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 23
def $ref_binding_stage(S,3) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $ref_binding_site(S,porigin_site,17)
def $ref_binding_stage(S,n) = false -- otherwise
dec $ref_binding_seek(pstate,nat,nat) : pstate
def $ref_binding_seek(S,n_mode,n) = S -- if $ref_binding_stage(S,n_mode)
def $ref_binding_seek(S,n_mode,0) = S -- if ~$ref_binding_stage(S,n_mode)
def $ref_binding_seek(S,n_mode,n) = $ref_binding_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ref_binding_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ref_binding_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_pos_raw = $ref_binding_seek(S_initial[.COMPLETION = NORMAL],0,4096)',
        r'S_pos_raw.COMPLETION = NORMAL \/ S_pos_raw.COMPLETION = BUDGET',
        'S_pos = S_pos_raw[.COMPLETION = NORMAL]',
        '$ref_binding_stage(S_pos,0)',
        'S_pos.CURRENT = eps',
        'S_pos.TODO = (CALL_ARGS (METHOD_TARGET n_pos_object porigin_pos_ctor) eps 2 poperand* (porigin_pos_site) z_pos) :: ptask_pos*',
        '$target_function(S_pos,METHOD_TARGET n_pos_object porigin_pos_ctor) = (pfunction_pos)',
        'pfunction_pos.SIGNATURE.PARAMETERS = [psparam_ref_pos,psparam_value_pos]',
        'psparam_ref_pos.NAME = $ptascii("value")', 'psparam_value_pos.NAME = $ptascii("ignored")',
        'psparam_ref_pos.BYREF', '~psparam_value_pos.BYREF',
        'psparam_ref_pos.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_value_pos.TYPE = eps',
        '$call_parameter_reference(S_pos,METHOD_TARGET n_pos_object porigin_pos_ctor,0)',
        '~$call_parameter_reference(S_pos,METHOD_TARGET n_pos_object porigin_pos_ctor,1)',
        '$lookup(S_pos.ENV,$ptascii("pos_alias")) = (n_pos_old)',
        'S_pos.STORE[n_pos_old] = DEFINED pvalue_pos_raw',
        '$string_bytes(pvalue_pos_raw) = ($ptascii("7"))',
        '$lookup(S_pos.ENV,$ptascii("pos")) = (n_pos_live)',
        '$lookup(S_pos.ENV,$ptascii("pos_other")) = (n_pos_live)',
        'n_pos_old =/= n_pos_live',
        'S_pos.STORE[n_pos_live] = DEFINED (PINT 30)',
        'poperand* = [REFERENCE n_pos_old,KNOWN (PINT 30)]',
        '$call_reference_operand_valid(S_pos,REFERENCE n_pos_old)',
        '$call_descriptors_valid(S_pos)',
        '~$call_task_valid(S_pos,CALL_ARGS (METHOD_TARGET n_pos_object porigin_pos_ctor) eps 1 poperand* (porigin_pos_site) z_pos)',
        '~$call_task_valid(S_pos,CALL_ARGS (METHOD_TARGET n_pos_object porigin_pos_ctor) eps 2 [KNOWN (PINT 7),KNOWN (PINT 30)] (porigin_pos_site) z_pos)',
        'S_pos_enter_raw = $drive_steps(S_pos,1)',
        r'S_pos_enter_raw.COMPLETION = NORMAL \/ S_pos_enter_raw.COMPLETION = BUDGET',
        'S_pos_enter = S_pos_enter_raw[.COMPLETION = NORMAL]',
        'S_pos_enter.TODO = [TYPE_RECEIVE porigin_pos_ctor 0]',
        'S_pos_enter.CURRENT = (pcallcontext_pos)',
        'pcallcontext_pos.TARGET = METHOD_TARGET n_pos_object porigin_pos_ctor',
        'pcallcontext_pos.ARGC = 2', 'pcallcontext_pos.HOLES = eps',
        '$lookup(S_pos_enter.ENV,$ptascii("value")) = (n_pos_old)',
        'S_pos_enter.STORE[n_pos_old] = DEFINED pvalue_pos_raw',
        '$lookup(S_pos_enter.ENV,$ptascii("ignored")) = (n_pos_ignored)',
        'S_pos_enter.STORE[n_pos_ignored] = DEFINED (PINT 30)',
        'n_pos_ignored =/= n_pos_old',
        'n_pos_ignored =/= n_pos_live',
        '~$typed_parameter_source(S_pos_enter,psparam_ref_pos)',
        '~$typed_caller_strict(S_pos_enter)',
        '$call_task_valid(S_pos_enter,TYPE_RECEIVE porigin_pos_ctor 0)',
        'S_coerced_raw = $drive_steps(S_pos_enter,1)',
        r'S_coerced_raw.COMPLETION = NORMAL \/ S_coerced_raw.COMPLETION = BUDGET',
        'S_coerced = S_coerced_raw[.COMPLETION = NORMAL]',
        'S_coerced.TODO = [TYPE_RECEIVE porigin_pos_ctor 1]',
        'S_coerced.STORE[n_pos_old] = DEFINED (PINT 7)',
        'S_coerced.STORE[n_pos_live] = DEFINED (PINT 30)',
        '$lookup(S_coerced.ENV,$ptascii("value")) = (n_pos_old)',
        '$call_reference_operand_valid(S_coerced,REFERENCE n_pos_old)',
        'S_named_raw = $ref_binding_seek(S_coerced,1,4096)',
        r'S_named_raw.COMPLETION = NORMAL \/ S_named_raw.COMPLETION = BUDGET',
        'S_named = S_named_raw[.COMPLETION = NORMAL]',
        '$ref_binding_stage(S_named,1)',
        'S_named.CURRENT = eps',
        'S_named.TODO = (NAMED_ARGS (METHOD_TARGET n_named_object porigin_named_ctor) eps 2 pnamedargs (porigin_named_site) z_named) :: ptask_named*',
        '$ref_binding_output(S_named.EVENTS) = $ptascii("pos|7|coerced|30|9|30|old-cell|")',
        'S_named.STORE[n_pos_old] = DEFINED (PINT 9)',
        'S_named.STORE[n_pos_live] = DEFINED (PINT 30)',
        '$lookup(S_named.ENV,$ptascii("pos_alias")) = (n_pos_old)',
        '$target_function(S_named,METHOD_TARGET n_named_object porigin_named_ctor) = (pfunction_named)',
        'pfunction_named.SIGNATURE.PARAMETERS = [psparam_ref_named,psparam_value_named]',
        'psparam_ref_named.BYREF', '~psparam_value_named.BYREF',
        '$call_parameter_reference(S_named,METHOD_TARGET n_named_object porigin_named_ctor,0)',
        '~$call_parameter_reference(S_named,METHOD_TARGET n_named_object porigin_named_ctor,1)',
        '$lookup(S_named.ENV,$ptascii("named_alias")) = (n_named_old)',
        'S_named.STORE[n_named_old] = DEFINED pvalue_named_raw',
        '$string_bytes(pvalue_named_raw) = ($ptascii("8"))',
        '$lookup(S_named.ENV,$ptascii("named")) = (n_named_live)',
        '$lookup(S_named.ENV,$ptascii("named_other")) = (n_named_live)',
        'n_named_old =/= n_named_live',
        'S_named.STORE[n_named_live] = DEFINED (PINT 40)',
        'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_named_live),NAMED_SENT (KNOWN (PINT 40))]',
        'pnamedargs.NAMED = eps',
        '$call_reference_operand_valid(S_named,REFERENCE n_named_live)',
        '$call_descriptors_valid(S_named)',
        '~$call_task_valid(S_named,NAMED_ARGS (METHOD_TARGET n_named_object porigin_named_ctor) eps 1 pnamedargs (porigin_named_site) z_named)',
        '~$call_task_valid(S_named,NAMED_ARGS (METHOD_TARGET n_named_object porigin_named_ctor) eps 2 pnamedargs[.SLOTS = [NAMED_SENT (KNOWN (PINT 40)),NAMED_SENT (KNOWN (PINT 40))]] (porigin_named_site) z_named)',
        'S_named_enter_raw = $drive_steps(S_named,1)',
        r'S_named_enter_raw.COMPLETION = NORMAL \/ S_named_enter_raw.COMPLETION = BUDGET',
        'S_named_enter = S_named_enter_raw[.COMPLETION = NORMAL]',
        'S_named_enter.TODO = [NAMED_PREFLIGHT porigin_named_ctor 0]',
        'S_named_enter.CURRENT = (pcallcontext_named)',
        'pcallcontext_named.TARGET = METHOD_TARGET n_named_object porigin_named_ctor',
        'pcallcontext_named.ARGC = 2', 'pcallcontext_named.HOLES = eps',
        '$lookup(S_named_enter.ENV,$ptascii("value")) = (n_named_live)',
        '$lookup(S_named_enter.ENV,$ptascii("ignored")) = (n_ignored)',
        'S_named_enter.STORE[n_ignored] = DEFINED (PINT 40)',
        'n_ignored =/= n_named_live',
        'S_named_type_raw = $ref_binding_seek(S_named_enter,3,4096)',
        r'S_named_type_raw.COMPLETION = NORMAL \/ S_named_type_raw.COMPLETION = BUDGET',
        'S_named_type = S_named_type_raw[.COMPLETION = NORMAL]',
        'S_named_type.TODO = [TYPE_RECEIVE porigin_named_ctor 0]',
        'S_named_type.STORE[n_named_live] = DEFINED (PINT 40)',
        'S_named_type.STORE[n_named_old] = DEFINED pvalue_named_raw',
        '$call_task_valid(S_named_type,TYPE_RECEIVE porigin_named_ctor 0)',
        'S_late_raw = $ref_binding_seek(S_named_type,2,4096)',
        r'S_late_raw.COMPLETION = NORMAL \/ S_late_raw.COMPLETION = BUDGET',
        'S_late = S_late_raw[.COMPLETION = NORMAL]',
        '$ref_binding_stage(S_late,2)',
        '$lookup(S_late.ENV,$ptascii("pos_alias")) = (n_pos_old)',
        '$lookup(S_late.ENV,$ptascii("pos")) = (n_pos_live)',
        'S_late.STORE[n_pos_old] = DEFINED (PINT 9)',
        'S_late.STORE[n_pos_live] = DEFINED (PINT 30)',
        '$lookup(S_late.ENV,$ptascii("named_alias")) = (n_named_old)',
        '$lookup(S_late.ENV,$ptascii("named")) = (n_named_live)',
        'S_late.STORE[n_named_old] = DEFINED pvalue_named_raw',
        'S_late.STORE[n_named_live] = DEFINED (PINT 11)',
        '$call_descriptors_valid(S_late)', '$heap_valid($heap_graph(S_late))',
        'S_done = $drive_steps(S_late,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ref_binding_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-reference-binding-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(b'{FILE}', os.fsencode(source))
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
        report.update(passed=True, conditions=len(checks), derived_guards=4, fixture_sha256=sha(fixture))
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
