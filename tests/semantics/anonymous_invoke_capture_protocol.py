#!/usr/bin/env python3
"""Implicit invocation keeps its selected receiver through argument rebinding."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invoke_cases.json'
SOURCE_SHA = '83c728734479cf3026e0950fcde848684b3e91eb15141b404116a84847266a27'
PREFIX = r'''
dec $ainvoke_output_item(pevent) : ptbytes
def $ainvoke_output_item(OUTPUT ptbytes) = ptbytes
def $ainvoke_output_item(pevent) = eps -- otherwise
dec $ainvoke_output(pevent*) : ptbytes
def $ainvoke_output(eps) = eps
def $ainvoke_output(pevent :: pevent_tail*) = $ainvoke_output_item(pevent) ++ $ainvoke_output(pevent_tail*)
dec $ainvoke_site(pstate,porigin) : bool
def $ainvoke_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprFuncCall expression (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata) = 17
def $ainvoke_site(S,porigin) = false -- otherwise
dec $ainvoke_stage(pstate,nat) : bool
def $ainvoke_stage(S,0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 2 poperand* (porigin_site) z) :: ptask_tail*
  -- if $ainvoke_site(S,porigin_site)
def $ainvoke_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 11
def $ainvoke_stage(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = eps
  -- if pdestructorcall.FRAME =/= eps
  -- if pdestructorcall.RELEASE =/= eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 15
def $ainvoke_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 18
def $ainvoke_stage(S,n) = false -- otherwise
dec $ainvoke_seek(pstate,nat,nat) : pstate
def $ainvoke_seek(S,n_stage,n) = S -- if $ainvoke_stage(S,n_stage)
def $ainvoke_seek(S,n_stage,0) = S -- if ~$ainvoke_stage(S,n_stage)
def $ainvoke_seek(S,n_stage,n) = $ainvoke_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ainvoke_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ainvoke_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $ainvoke_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$ainvoke_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_sent', 0),
        'S_sent.TODO = (CALL_ARGS (METHOD_TARGET n_old porigin_invoke) eps 2 poperand* (porigin_site) z_call) :: ptask_tail*',
        '$lookup(S_sent.ENV,$ptascii("value159Review")) = (n_value)',
        'S_sent.STORE[n_value] = DEFINED pvalue_raw', '$string_bytes(pvalue_raw) = ($ptascii("7"))',
        '$lookup(S_sent.ENV,$ptascii("callable159Review")) = (n_callable)',
        '$lookup(S_sent.ENV,$ptascii("replacement159Review")) = (n_replacement)',
        'S_sent.STORE[n_callable] = DEFINED (POBJECT n_new)',
        'S_sent.STORE[n_replacement] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        '(HOBJECT n_old) <- S_sent.ALLOCATIONS', '(HOBJECT n_new) <- S_sent.ALLOCATIONS',
        '~(n_old <- S_sent.DESTRUCTION.CALLED)',
        'S_sent.OBJECTS[n_old] = INSTANCE porigin_class_old',
        'S_sent.OBJECTS[n_new] = INSTANCE porigin_class_new',
        'porigin_class_old =/= porigin_class_new',
        '$object_invoke_method(S_sent,n_old) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_class_old', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc.STATIC', '~pmethoddesc.ABSTRACT',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_invoke',
        '$target_function(S_sent,METHOD_TARGET n_old porigin_invoke) = (pfunction)',
        'pfunction = pmethoddesc.FUNCTION', '~$function_generator(S_sent,pfunction)',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_value,psparam_ignored]',
        'psparam_value.NAME = $ptascii("value")', 'psparam_value.BYREF',
        'psparam_value.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '~psparam_ignored.BYREF', 'psparam_ignored.TYPE = eps',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]',
        '~pfunction.SIGNATURE.BYREF',
        'poperand* = [REFERENCE n_value,KNOWN (POBJECT n_new)]',
        '$method_call_selected(S_sent,METHOD_TARGET n_old porigin_invoke,(porigin_site))',
        '$call_task_valid(S_sent,S_sent.TODO[0])',
        '$call_reference_operand_valid(S_sent,REFERENCE n_value)',
        '$ainvoke_output(S_sent.EVENTS) = eps',
        '$class_state_valid(S_sent)', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_old porigin_invoke) eps 1 poperand* (porigin_site) z_call)',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_old porigin_invoke) eps 2 ([KNOWN pvalue_raw,KNOWN (POBJECT n_new)]) (porigin_site) z_call)',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_old porigin_invoke) eps 2 poperand* (porigin_site) $(z_call + 1))',
        'S_entered_raw = $drive_steps(S_sent,1)',
        r'S_entered_raw.COMPLETION = NORMAL \/ S_entered_raw.COMPLETION = BUDGET',
        'S_entered = S_entered_raw[.COMPLETION = NORMAL]',
        'S_entered.TODO = [TYPE_RECEIVE porigin_invoke 0]',
        'S_entered.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_old porigin_invoke',
        'pcallcontext.FUNCTION = porigin_invoke', 'pcallcontext.RECEIVER = (n_old)',
        'pcallcontext.LEXICAL_CLASS = (porigin_class_old)',
        'pcallcontext.CALLED_CLASS = (porigin_class_old)',
        'pcallcontext.CALLSITE = (porigin_site)',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
        '$lookup(S_entered.ENV,$ptascii("value")) = (n_value)',
        'S_entered.STORE[n_value] = DEFINED pvalue_raw',
        '$lookup(S_entered.ENV,$ptascii("ignored")) = (n_ignored)',
        'S_entered.STORE[n_ignored] = DEFINED (POBJECT n_new)',
        'S_entered.FRAMES = pframe_root :: pframe_tail*',
        'pframe_root.LOCALS = eps',
        'S_entered.GLOBALTABLE = (psymboltable_root)',
        '$lookup(psymboltable_root.ENV,$ptascii("callable159Review")) = (n_callable)',
        '~$typed_caller_strict(S_entered)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        *seek('S_entered', 'S_body', 1),
        'S_body.CURRENT = (pcallcontext)',
        'S_body.STORE[n_value] = DEFINED (PINT 7)',
        'S_body.STORE[n_callable] = DEFINED (POBJECT n_new)',
        '(HOBJECT n_old) <- S_body.ALLOCATIONS',
        '~(n_old <- S_body.DESTRUCTION.CALLED)',
        '$ainvoke_output(S_body.EVENTS) = eps',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        *seek('S_body', 'S_destructor', 2),
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        '$destructor_context_call(pcallcontext_destructor,S_destructor.CURRENT,S_destructor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_old', 'pdestructorcall.OPERATION = eps',
        'pdestructorcall.FRAME = (pdestructionframe)',
        'pdestructorcall.RELEASE = (pdestructionrelease)',
        'pdestructionframe.FUNCTION = porigin_invoke',
        'pdestructionframe.CALLER = eps', 'pdestructionframe.PENDING = eps',
        'pdestructionframe.VALUE = KNOWN pvalue_returned',
        '$string_bytes(pvalue_returned) = ($ptascii("original"))',
        '$destructor_frames_valid(S_destructor,S_destructor.DESTRUCTION.FRAMES)',
        '$destructor_leaf_valid(S_destructor,pdestructorcall)',
        '$destructor_call_pending_valid(S_destructor,pdestructorcall)',
        'S_destructor.STORE[n_value] = DEFINED (PINT 11)',
        'S_destructor.STORE[n_callable] = DEFINED (POBJECT n_new)',
        '$ainvoke_output(S_destructor.EVENTS) = $ptascii("head-int|")',
        '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))',
        *seek('S_destructor', 'S_observe', 3),
        '$lookup(S_observe.ENV,$ptascii("result159Review")) = (n_result)',
        'S_observe.STORE[n_result] = DEFINED pvalue_result',
        '$string_bytes(pvalue_result) = ($ptascii("original"))',
        'S_observe.STORE[n_value] = DEFINED (PINT 11)',
        'S_observe.STORE[n_callable] = DEFINED (POBJECT n_new)',
        '~((HOBJECT n_old) <- S_observe.ALLOCATIONS)', 'n_old <- S_observe.DESTRUCTION.CALLED',
        '(HOBJECT n_new) <- S_observe.ALLOCATIONS',
        '$ainvoke_output(S_observe.EVENTS) = $ptascii("head-int|original-dtor|")',
        '$class_state_valid(S_observe)', '$call_descriptors_valid(S_observe)', '$heap_valid($heap_graph(S_observe))',
        'S_done = $drive_steps(S_observe,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ainvoke_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-invoke-capture-', dir=ROOT / '.tools'))
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
