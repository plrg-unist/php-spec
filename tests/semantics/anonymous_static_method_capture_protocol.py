#!/usr/bin/env python3
"""Source-reached receiverless static capture, retirement and caller reference."""
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
SOURCE_SHA = 'b43667aa7a8a5965d5dec1179325d2852d5fbda8b9ab8b0445e288628cb748c0'
PREFIX = r'''
dec $asc161_output_item(pevent) : ptbytes
def $asc161_output_item(OUTPUT ptbytes) = ptbytes
def $asc161_output_item(pevent) = eps -- otherwise
dec $asc161_output(pevent*) : ptbytes
def $asc161_output(eps) = eps
def $asc161_output(pevent :: pevent_tail*) = $asc161_output_item(pevent) ++ $asc161_output(pevent_tail*)
dec $asc161_echo(pstate,int) : bool
def $asc161_echo(S,z) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = z
def $asc161_echo(S,z) = false -- otherwise
dec $asc161_stage(pstate,nat) : bool
def $asc161_stage(S,0) = true
  -- if S.TODO = (METHOD_CONVERT pcalltarget porigin z) :: ptask_tail*
  -- if $origin_node(S.SOURCES,porigin) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata) = 10
def $asc161_stage(S,1) = (S.CURRENT = eps /\ $asc161_echo(S,14))
def $asc161_stage(S,2) = (S.CURRENT = eps /\ $asc161_echo(S,16))
def $asc161_stage(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $asc161_echo(S,4)
def $asc161_stage(S,4) = (S.CURRENT = eps /\ $asc161_echo(S,17))
def $asc161_stage(S,n) = false -- otherwise
dec $asc161_seek(pstate,nat,nat) : pstate
def $asc161_seek(S,n_stage,n) = S -- if $asc161_stage(S,n_stage)
def $asc161_seek(S,n_stage,0) = S -- if ~$asc161_stage(S,n_stage)
def $asc161_seek(S,n_stage,n) = $asc161_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$asc161_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $asc161_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $asc161_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$asc161_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_capture', 0),
        'S_capture.CURRENT = eps',
        'S_capture.TODO = (METHOD_CONVERT pcalltarget porigin_capture z_capture) :: ptask_capture_tail*',
        'pcalltarget = SCOPED_TARGET porigin_class_old porigin_method porigin_class_old eps poperand_selector',
        '$lookup(S_capture.ENV,$ptascii("selected161Review")) = (n_selected_cell)',
        'S_capture.STORE[n_selected_cell] = DEFINED (POBJECT n_old)',
        '(HOBJECT n_old) <- S_capture.ALLOCATIONS',
        '$object_body(S_capture.OBJECTS[n_old]) = INSTANCE porigin_class_old',
        '$class_at(S_capture.CLASSES,porigin_class_old) = (pclassdesc_old)',
        'poperand_selector = KNOWN (PSTRING pclassdesc_old.NAME)',
        '$class_method_origin(S_capture.CLASSES,porigin_method) = (pmethoddesc_work)',
        'pmethoddesc_work.OWNER = porigin_class_old', 'pmethoddesc_work.STATIC',
        'pmethoddesc_work.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc_work.FUNCTION.SIGNATURE.BYREF',
        '$method_named(pclassdesc_old.METHODS,$ptascii("__destruct")) = (pmethoddesc_destruct)',
        '$target_receiver(S_capture,pcalltarget) = eps',
        '$target_called_class(S_capture,pcalltarget) = (porigin_class_old)',
        '$method_convert_valid(S_capture,pcalltarget,porigin_capture,z_capture)',
        '~$method_convert_valid(S_capture,pcalltarget,porigin_capture,$(z_capture + 1))',
        '~$method_convert_valid(S_capture,SCOPED_TARGET porigin_class_old pmethoddesc_destruct.FUNCTION.ORIGIN porigin_class_old eps poperand_selector,porigin_capture,z_capture)',
        '$asc161_output(S_capture.EVENTS) = eps',
        '$class_state_valid(S_capture)', '$call_descriptors_valid(S_capture)',
        '$heap_valid($heap_graph(S_capture))',
        *seek('S_capture', 'S_rebound', 1),
        '$lookup(S_rebound.ENV,$ptascii("captured161Review")) = (n_capture_cell)',
        'S_rebound.STORE[n_capture_cell] = DEFINED (POBJECT n_capture)',
        '(HOBJECT n_capture) <- S_rebound.ALLOCATIONS',
        '$object_body(S_rebound.OBJECTS[n_capture]) = METHODCLOSURE porigin_method porigin_capture porigin_class_old eps',
        '$closure_scope_at(S_rebound.CLOSURESCOPES,n_capture) = (pclosurescope_capture)',
        'pclosurescope_capture.OBJECT = n_capture',
        'pclosurescope_capture.LEXICAL = porigin_class_old',
        'pclosurescope_capture.CALLED = porigin_class_old',
        'pclosurescope_capture.RECEIVER = eps', 'pclosurescope_capture.CREATION = eps',
        '$method_closure_scope_valid(S_rebound,pclosurescope_capture)',
        '$node_children(S_rebound,HOBJECT n_capture) = eps',
        '~((HOBJECT n_old) <- S_rebound.ALLOCATIONS)',
        'n_old <- S_rebound.DESTRUCTION.CALLED',
        'S_rebound.STORE[n_selected_cell] = DEFINED (POBJECT n_new)',
        '(HOBJECT n_new) <- S_rebound.ALLOCATIONS', 'n_old =/= n_new',
        '$object_body(S_rebound.OBJECTS[n_new]) = INSTANCE porigin_class_new',
        'porigin_class_old =/= porigin_class_new',
        '~$method_capture_receiver_valid(S_rebound,pmethoddesc_work,pclosurescope_capture[.RECEIVER = (n_new)])',
        '$asc161_output(S_rebound.EVENTS) = $ptascii("old-drop|")',
        '$class_state_valid(S_rebound)', '$call_descriptors_valid(S_rebound)',
        '$heap_valid($heap_graph(S_rebound))',
        *seek('S_rebound', 'S_ready', 2),
        '$lookup(S_ready.ENV,$ptascii("head161Review")) = (n_head_cell)',
        'S_ready.STORE[n_head_cell] = DEFINED pvalue_head_raw',
        '$string_bytes(pvalue_head_raw) = ($ptascii("3"))',
        '$closure_callable(S_ready,n_capture)',
        '$asc161_output(S_ready.EVENTS) = $ptascii("old-drop|after-rebind|")',
        *seek('S_ready', 'S_body', 3),
        'S_body.CURRENT = (pcallcontext_body)',
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_capture',
        'pcallcontext_body.FUNCTION = porigin_method',
        'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_class_old)',
        'pcallcontext_body.CALLED_CLASS = (porigin_class_old)',
        '$lookup(S_body.ENV,$ptascii("head")) = (n_head_cell)',
        'n_head_cell <- S_body.REFCELLS',
        'S_body.STORE[n_head_cell] = DEFINED (PINT 3)',
        '$lookup(S_body.ENV,$ptascii("tail")) = (n_tail_cell)',
        'n_tail_cell =/= n_head_cell',
        'S_body.STORE[n_tail_cell] = DEFINED (PINT 8)',
        '$call_current_valid(S_body)',
        '$asc161_output(S_body.EVENTS) = $ptascii("old-drop|after-rebind|")',
        '$class_state_valid(S_body)', '$call_descriptors_valid(S_body)',
        '$heap_valid($heap_graph(S_body))',
        *seek('S_body', 'S_after', 4),
        'S_after.STORE[n_head_cell] = DEFINED (PINT 11)',
        '(HOBJECT n_capture) <- S_after.ALLOCATIONS',
        '(HOBJECT n_new) <- S_after.ALLOCATIONS',
        '~((HOBJECT n_old) <- S_after.ALLOCATIONS)',
        '$asc161_output(S_after.EVENTS) = $ptascii("old-drop|after-rebind|head-int|11|11|")',
        '$class_state_valid(S_after)', '$call_descriptors_valid(S_after)',
        '$heap_valid($heap_graph(S_after))',
        'S_done = $drive_steps(S_after,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$asc161_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-static-method-capture-', dir=ROOT / '.tools'))
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
