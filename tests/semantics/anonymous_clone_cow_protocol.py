#!/usr/bin/env python3
"""Source-reached copy-before-callback array storage and retained reference alias."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_clone_cases.json'
SOURCE_SHA = '46a6660c823d8cff4c8d9515f093da6a85667318c6cca84d20ce69d187eaf3a0'
PREFIX = r'''
dec $aca160_output_item(pevent) : ptbytes
def $aca160_output_item(OUTPUT ptbytes) = ptbytes
def $aca160_output_item(pevent) = eps -- otherwise
dec $aca160_output(pevent*) : ptbytes
def $aca160_output(eps) = eps
def $aca160_output(pevent :: pevent_tail*) = $aca160_output_item(pevent) ++ $aca160_output(pevent_tail*)
dec $aca160_site(pstate,porigin,int) : bool
def $aca160_site(S,porigin,z) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprClone expression metadata)
  -- if $source_line(metadata) = z
def $aca160_site(S,porigin,z) = false -- otherwise
dec $aca160_stage(pstate,nat) : bool
def $aca160_stage(S,0) = true
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
  -- if $aca160_site(S,pcloneoperation.SITE,14)
def $aca160_stage(S,1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 15
def $aca160_stage(S,n) = false -- otherwise
dec $aca160_seek(pstate,nat,nat) : pstate
def $aca160_seek(S,n_stage,n) = S -- if $aca160_stage(S,n_stage)
def $aca160_seek(S,n_stage,0) = S -- if ~$aca160_stage(S,n_stage)
def $aca160_seek(S,n_stage,n) = $aca160_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$aca160_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $aca160_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $aca160_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$aca160_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_enter', 0),
        'S_enter.CURRENT = eps',
        'S_enter.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_enter_tail*',
        'n_source = pcloneoperation.SOURCE', 'n_copy = pcloneoperation.TARGET',
        'n_source =/= n_copy', 'pcloneoperation.CALL = eps', 'pcloneoperation.SCOPE = eps',
        '(HOBJECT n_source) <- S_enter.ALLOCATIONS', '(HOBJECT n_copy) <- S_enter.ALLOCATIONS',
        '$lookup(S_enter.ENV,$ptascii("source160Author")) = (n_source_cell)',
        'S_enter.STORE[n_source_cell] = DEFINED (POBJECT n_source)',
        '$lookup(S_enter.ENV,$ptascii("shared160Author")) = (n_shared_cell)',
        'n_shared_cell <- S_enter.REFCELLS',
        'S_enter.STORE[n_shared_cell] = DEFINED (PINT 4)',
        'S_enter.OBJECTS[n_source] = INSTANCE porigin_class',
        'S_enter.OBJECTS[n_copy] = INSTANCE porigin_class',
        '$clone_method(S_enter,n_copy) = (pmethoddesc_clone)',
        'pmethoddesc_clone.OWNER = porigin_class',
        'pmethoddesc_clone.VISIBILITY = PROPERTY_PUBLIC', '~pmethoddesc_clone.STATIC',
        'pmethoddesc_clone.FUNCTION.SIGNATURE.PARAMETERS = eps',
        '~pmethoddesc_clone.FUNCTION.SIGNATURE.BYREF',
        'pmethoddesc_clone.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
        '$clone_callback_live(S_enter,pcloneoperation)',
        '$call_task_valid(S_enter,S_enter.TODO[0])',
        '$objectprops_record_at(S_enter.OBJECTPROPS,n_source) = (pobjectprops_source)',
        '$objectprops_record_at(S_enter.OBJECTPROPS,n_copy) = (pobjectprops_copy)',
        '$property_slot_at(pobjectprops_source.SLOTS,$ptascii("items")) = (ppropertyslot_source_items)',
        '$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("items")) = (ppropertyslot_copy_items)',
        'ppropertyslot_source_items.DECL = (ppropertyid_items)',
        'ppropertyslot_copy_items.DECL = (ppropertyid_items)',
        'ppropertyslot_source_items.STATE = PROP_VALUE (DIRECT (PARRAY n_array_original))',
        'ppropertyslot_copy_items.STATE = PROP_VALUE (DIRECT (PARRAY n_array_original))',
        '(HARRAY n_array_original) <- S_enter.ALLOCATIONS',
        '$entry_lookup(S_enter.ARRAYS[n_array_original].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$entry_lookup(S_enter.ARRAYS[n_array_original].ITEMS,KINT 1) = (ALIAS n_shared_cell)',
        '$property_slot_at(pobjectprops_source.SLOTS,$ptascii("mark")) = (ppropertyslot_source_mark)',
        '$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("mark")) = (ppropertyslot_copy_mark)',
        'ppropertyslot_source_mark.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'ppropertyslot_copy_mark.STATE = PROP_VALUE (DIRECT (PINT 1))',
        '$aca160_output(S_enter.EVENTS) = eps',
        '$class_state_valid(S_enter)', '$call_descriptors_valid(S_enter)',
        '$heap_valid($heap_graph(S_enter))',
        *seek('S_enter', 'S_after', 1),
        '$lookup(S_after.ENV,$ptascii("copy160Author")) = (n_copy_cell)',
        'S_after.STORE[n_copy_cell] = DEFINED (POBJECT n_copy)',
        'S_after.STORE[n_source_cell] = DEFINED (POBJECT n_source)',
        'S_after.STORE[n_shared_cell] = DEFINED (PINT 7)',
        'S_after.CLONES = eps',
        '$objectprops_record_at(S_after.OBJECTPROPS,n_source) = (pobjectprops_after_source)',
        '$objectprops_record_at(S_after.OBJECTPROPS,n_copy) = (pobjectprops_after_copy)',
        '$property_slot_at(pobjectprops_after_source.SLOTS,$ptascii("items")) = (ppropertyslot_after_source_items)',
        '$property_slot_at(pobjectprops_after_copy.SLOTS,$ptascii("items")) = (ppropertyslot_after_copy_items)',
        'ppropertyslot_after_source_items.STATE = PROP_VALUE (DIRECT (PARRAY n_array_original))',
        'ppropertyslot_after_copy_items.STATE = PROP_VALUE (DIRECT (PARRAY n_array_copy))',
        'n_array_original =/= n_array_copy',
        '(HARRAY n_array_original) <- S_after.ALLOCATIONS',
        '(HARRAY n_array_copy) <- S_after.ALLOCATIONS',
        '$entry_lookup(S_after.ARRAYS[n_array_original].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$entry_lookup(S_after.ARRAYS[n_array_copy].ITEMS,KINT 0) = (DIRECT (PINT 11))',
        '$entry_lookup(S_after.ARRAYS[n_array_original].ITEMS,KINT 1) = (ALIAS n_shared_cell)',
        '$entry_lookup(S_after.ARRAYS[n_array_copy].ITEMS,KINT 1) = (ALIAS n_shared_cell)',
        '$property_slot_at(pobjectprops_after_source.SLOTS,$ptascii("mark")) = (ppropertyslot_after_source_mark)',
        '$property_slot_at(pobjectprops_after_copy.SLOTS,$ptascii("mark")) = (ppropertyslot_after_copy_mark)',
        'ppropertyslot_after_source_mark.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'ppropertyslot_after_copy_mark.STATE = PROP_VALUE (DIRECT (PINT 8))',
        '$aca160_output(S_after.EVENTS) = $ptascii("2|1|")',
        '$class_state_valid(S_after)', '$call_descriptors_valid(S_after)',
        '$heap_valid($heap_graph(S_after))',
        'S_done = $drive_steps(S_after,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$aca160_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-clone-cow-', dir=ROOT / '.tools'))
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
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks),
                      derived_conditions=0, derived_guards=0, fixture_sha256=sha(fixture))
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
