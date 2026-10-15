#!/usr/bin/env python3
"""Reached object-leaf array queries, physical COW edges and root ownership."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import error_handler_run as recorder
import global_constant_object_array_sources as sources
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha
text = lambda value: '$ptascii(' + json.dumps(value) + ')'


def receive(state, start, query):
    call, after = 'pconfigcall_' + state, state + '_value'
    values = [*common.reach(state, start, 0, query),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        '$dynamic_global_constant_call(' + call + ')',
        '$dynamic_global_constant_valid(' + state + ',' + call + ')',
        call + '.OWNER = eps', call + '.PACKS = eps',
        state + '.USERCONSTANTS = [puserconstant]', 'puserconstant.NAME = ' + text(query),
        'puserconstant.VALUE = PARRAY n_root',
        state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        state + '.ARRAYS[n_child].ITEMS = (ENTRY (KINT 0) (DIRECT (POBJECT n_object))) :: pentry_tail*',
        '$pvclass_get(puserconstant.CLASS,KINT 1) = (pvalueclass_child)',
        '$pvclass_get(pvalueclass_child,KINT 0) = (pvalueclass_leaf)',
        '$constant_value_class_valid(' + state + ',POBJECT n_object,pvalueclass_leaf)',
        '$dynamic_global_constant_array_tree(' + state + ',POBJECT n_object,pvalueclass_leaf)',
        '$dynamic_global_constant_value(' + state + ',' + text(query) + ') = (PARRAY n_root)',
        '$user_constant_roots(' + state + '.USERCONSTANTS) = [HARRAY n_root]',
        'H_' + state + ' = $heap_graph(' + state + ')',
        'n_rootowners_' + state + ' = $heap_owners(H_' + state + ',HARRAY n_root)',
        'n_objectowners_' + state + ' = $heap_owners(H_' + state + ',HOBJECT n_object)',
        '$(n_rootowners_' + state + ' > 0)', '$(n_objectowners_' + state + ' > 0)',
        '$heap_edge_owners(HOBJECT n_object,H_' + state + '.EDGES,[HARRAY n_child]) = 1',
        *common.public(state), *common.step(after, state, 'PARRAY n_root'),
        after + '.TODO = ptask_' + state + '*', after + '.BASE = BASE_VALUE (KNOWN PNULL)',
        'H_' + after + ' = $heap_graph(' + after + ')',
        'H_' + after + '.NODES = H_' + state + '.NODES', 'H_' + after + '.EDGES = H_' + state + '.EDGES',
        '$heap_owners(H_' + after + ',HARRAY n_root) = $(n_rootowners_' + state + ' + 1)',
        '$heap_owners(H_' + after + ',HOBJECT n_object) = n_objectowners_' + state]
    values += [after + '.' + field + ' = ' + state + '.' + field for field in (
        'ARRAYS', 'OBJECTS', 'OBJECTPROPS', 'OBJECTTABLES', 'PROPREFS',
        'CLOSURESCOPES', 'CLOSUREBINDINGS', 'CONSTANTOBJECTS', 'CONSTANTCLOSURES',
        'USERCONSTANTS', 'STORE', 'REFCELLS', 'ALLOCATIONS', 'STRINGDATA', 'STATICS',
        'DEFAULTCACHE', 'POOLS', 'SOURCES', 'FILES', 'SELECTEDCALLS')]
    return values


def instance_property(state, value):
    return ['$objectprops_at(' + state + '.OBJECTPROPS,n_object) = (ppropertyslot_all_' + state + '*)',
        '$property_slot_at(ppropertyslot_all_' + state + '*,' + text('value') + ') = (ppropertyslot_' + state + ')',
        'ppropertyslot_' + state + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(value) + '))']


def checks(program, path, name):
    instance = name == 'instance-leaf-and-nested-cow'
    query = 'GlobalInstanceArray26' if instance else 'GlobalClosureArray26'
    tag = 'PVINSTANCE' if instance else 'PVCLOSURE'
    tail = ',ENTRY (KINT 1) (DIRECT (PARRAY n_empty))' if instance else ''
    append_key, held = (2, 'item') if instance else (1, 'f')
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *receive('S', 'S_initial', query),
        'pvalueclass_leaf = ' + tag + ' n_object porigin_site',
        'n_rootowners_S = 1', 'n_objectowners_S = 1',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
        'S_one[.COMPLETION = NORMAL] = S_value',
        *common.reach('S_peer', 'S_value', 0, query), *common.step('S_peer_value', 'S_peer', 'PARRAY n_root'),
        *receive('S_during', 'S_peer_value', query),
        '$lookup(S_during.ENV,' + text('first') + ') = (n_first_cell)',
        'S_during.STORE[n_first_cell] = DEFINED (PARRAY n_copy_root)',
        'n_copy_root =/= n_root', 'HARRAY n_copy_root <- S_during.ALLOCATIONS',
        'S_during.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
        'n_copy_child =/= n_child', 'HARRAY n_copy_child <- S_during.ALLOCATIONS',
        'S_during.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))' + tail + ',ENTRY (KINT ' + str(append_key) + ') (DIRECT pvalue_tail)]',
        '$string_bytes(pvalue_tail) = (' + text('tail') + ')',
        '$heap_edge_owners(HOBJECT n_object,H_S_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
        '$lookup(S_during.ENV,' + text(held) + ') = (n_held_cell)',
        'S_during.STORE[n_held_cell] = DEFINED (POBJECT n_object)',
        *receive('S_again', 'S_during_value', query),
        'n_rootowners_S_again = 1', 'n_objectowners_S_again = 1']
    if instance:
        values += ['pconfigcall_S.SELECTION = eps',
            'pentry_tail* = [ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
            '$pvclass_get(pvalueclass_child,KINT 1) = (PVARRAY true eps)',
            '$array_immutable(S,n_empty)',
            '$global_new_record(S.CONSTANTOBJECTS,n_object) = (pconstantobject)',
            'S.CONSTANTOBJECTS = [pconstantobject]',
            'pconstantobject.SITE = porigin_site', 'pconstantobject.DECL = puserconstant.ORIGIN',
            '$global_new_completed(S,pconstantobject)', '$global_new_completed(S_again,pconstantobject)',
            *instance_property('S', 3), *instance_property('S_during', 9), *instance_property('S_again', 9),
            'S_bad_creation = S[.CONSTANTOBJECTS[0].COMPLETE = false]']
    else:
        values += ['pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT', 'pentry_tail* = eps',
            'S.CONSTANTCLOSURES = [pconstantclosure]', 'pconstantclosure.SITE = porigin_site',
            'pconstantclosure.DECL = puserconstant.ORIGIN', '$constant_callable_record_valid(S,pconstantclosure)',
            '$constant_callable_record_valid(S_again,pconstantclosure)',
            '$object_body(S.OBJECTS[n_object]) = REALCLOSURE porigin_site eps eps',
            'S_during.OBJECTS[n_object] = S.OBJECTS[n_object]',
            '$object_body(S_again.OBJECTS[n_object]) = REALCLOSURE porigin_site eps ([pstaticcell_counter])',
            'n_counter = pstaticcell_counter.CELL', '$(n_counter < |S_again.STORE|)',
            'S_again.STORE[n_counter] = DEFINED (PINT 2)',
            'S_bad_creation = S[.CONSTANTCLOSURES[0].SITE = pconfigcall_S.SITE]']
    values += ['pvalueclass_bad_site = $pvclass_put(puserconstant.CLASS,KINT 1,$pvclass_put(pvalueclass_child,KINT 0,' + tag + ' n_object pconfigcall_S.SITE))',
        'pvalueclass_bad_tag = $pvclass_put(puserconstant.CLASS,KINT 1,$pvclass_put(pvalueclass_child,KINT 0,PVOBJECT))',
        'S_bad_site = S[.USERCONSTANTS[0].CLASS = pvalueclass_bad_site]',
        'S_bad_tag = S[.USERCONSTANTS[0].CLASS = pvalueclass_bad_tag]',
        'S_bad_id = S[.ARRAYS[n_child].ITEMS[0] = ENTRY (KINT 0) (DIRECT (POBJECT (|S.OBJECTS|)))]',
        'S_bad_kind = S[.OBJECTS[n_object] = STDINSTANCE]',
        'S_bad_live = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        'HARRAY n_root <- S_bad_live.ALLOCATIONS', 'HARRAY n_child <- S_bad_live.ALLOCATIONS',
        'S_bad_alias = S_during[.ARRAYS[n_child].ITEMS[0] = ENTRY (KINT 0) (ALIAS n_held_cell)]',
        '$constant_value_class_valid(S_during,POBJECT n_object,pvalueclass_leaf)',
        '$constant_value_class_valid(S_bad_alias,PARRAY n_root,puserconstant.CLASS)',
        '$dynamic_global_constant_value(S_bad_alias,' + text(query) + ') = eps',
        '~$dynamic_global_constant_array_tree(S,POBJECT n_object,PVOBJECT)']
    for bad in ('id', 'site', 'tag', 'kind', 'creation', 'live'):
        values += ['$dynamic_global_constant_value(S_bad_' + bad + ',' + text(query) + ') = eps',
            '~$call_descriptors_valid(S_bad_' + bad + ')']
    values += ['S_bad_out = $drive(S_bad_tag,0)', 'S_bad_out.COMPLETION = UNSUPPORTED text_bad']
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, originals = args.output.resolve(), args.sources.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json'); assert not report_path.exists()
    native_path = originals / 'native-report.json'
    native = json.loads(native_path.read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    names = list(sources.family.CASES)
    paths = {name: originals / name / 'main.php' for name in names}
    for name, path in paths.items():
        assert path.read_bytes() == sources.family.CASES[name]
        row, = [row for row in native['records'] if row['id'] == name]
        assert row['source_sha256'] == sha(path)
    watched = [Path(__file__), Path(common.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/static_types.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        native_path, *paths.values()]
    if args.phase == 'check':
        watched += [out / 'prepare-report.json']
        watched += [out / name / item for name in names for item in ('protocol.watsup', 'assertions.json')]
    pins = lambda: dict(sources.family.fingerprint(), **{str(path): sha(path) for path in watched})
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'phase': args.phase, 'revision': head, 'inputs': pins(), 'records': [], 'passed': False}
    try:
        if args.phase == 'prepare':
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                try:
                    for name, path in paths.items():
                        parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())}); assert parsed['accepted']
                        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                        values = checks(checked['fixture'], path, name)
                        target = out / name; target.mkdir()
                        fixture = target / 'protocol.watsup'
                        (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
                        fixture.write_text(common.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                            ''.join('  -- if ' + value + '\n' for value in values))
                        report['records'].append({'id': name, 'fixture_sha256': sha(fixture), 'premises': len(values)})
                finally:
                    adapter.close()
            finally:
                frontend.close()
        else:
            prepared = json.loads((out / 'prepare-report.json').read_bytes())
            assert prepared['passed'] and prepared['inputs_stable'] and prepared['head_stable']
            assert all(report['inputs'][key] == value for key, value in prepared['inputs'].items())
            assert [row['id'] for row in prepared['records']] == names
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
            for row in prepared['records']:
                target = out / row['id']; fixture = target / 'protocol.watsup'
                assert sha(fixture) == row['fixture_sha256']
                record = dict(row); report['records'].append(record)
                record['process'] = recorder.recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    '--sl', *modules, str(fixture)], target / 'check', 90)
                assert record['process']['exit'] == 0 and not record['process']['timeout'] and not record['process']['group_after']
                assert (target / 'check.stdout').read_bytes() == b'true\n' and (target / 'check.stderr').read_bytes() == b''
                assert sha(fixture) == row['fixture_sha256']
                record['passed'] = True
                print(record['id'], record['premises'], 'PASS', flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['inputs'] == pins()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
