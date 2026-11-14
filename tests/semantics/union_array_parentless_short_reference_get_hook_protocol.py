#!/usr/bin/env python3
"""Check raw union order, typed outer sources, COW and physical cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('union_array_parentless_short_reference_get_hook')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box298")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias298")
def $srgh_phase(S,9,n) = ($property_hook_plan(S) =/= eps)
def $srgh_phase(S,10,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NExprConstFetch (NName (BYTES text_null) metadata_null) metadata_fetch) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias298") /\ $ptlc($base64(text_null)) = $ptascii("null")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    first, second = form.split('-')
    normalized = '[(PTBRANCH ([PTBUILTIN "' + first + '"])),(PTBRANCH ([PTBUILTIN "' + second + '"]))]'
    reverse = '[(PTBRANCH ([PTBUILTIN "' + second + '"])),(PTBRANCH ([PTBUILTIN "' + first + '"]))]'
    array_null = form == 'array-null'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)',
        'S_front.COMPLETION = NORMAL', '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box298")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("items")',
        'ppropertydesc.TYPE = ' + normalized, '$property_type_name(S_front,ppropertydesc) = $ptascii("?array")',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook', 'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]', 'pfunction_get.CODE.UNIT = n_source',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second])) metadata_type',
        '$ptlc($base64(text_first)) = $ptascii("' + first + '")', '$ptlc($base64(text_second)) = $ptascii("' + second + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '~$hook_short_reference_header(phpType18,' + reverse + ')',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reverse + '])',
        '$hook_parameter_facts(metadata_hook) = [false]', '$hook_short_reference_body(expression_get,ppropertydesc.NAME)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((6,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (6)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 6]',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.COMPLETION = NORMAL', 'S_return.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook', 'S_return.ORIGIN = (ppropertyhook.HOOK)',
        '$reference_return_source(S_return,6)', '$reference_return_fetch_valid(S_return,6)', '$reference_verifies(S_return)',
        '$property_current_line($hold_task_inputs(S_return)) = 6', '$property_hook_backing(S_return,n_root,ppropertydesc)',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
        'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_field',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("items")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2', '$property_state_valid(S_fetch)', '$call_descriptors_valid(S_fetch)',
        'S_nosource = S_fetch[.PROPREFS = eps]', '~$property_state_valid(S_nosource)',
        'S_cow = $srgh_seek(S_fetch,10,n_root,30000)', '$srgh_phase(S_cow,10,n_root)', 'S_cow.COMPLETION = NORMAL',
        'S_cow.STORE[n_field] = DEFINED (PARRAY n_live)', '$lookup(S_cow.ENV,$ptascii("copy298")) = (n_cowcopycell)',
        'S_cow.STORE[n_cowcopycell] = DEFINED (PARRAY n_cowcopy)', 'n_live =/= n_cowcopy',
        '$propref_at(S_cow.PROPREFS,n_field) = (ppropref)', '$property_state_valid(S_cow)', '$heap_valid($heap_prune($heap_graph(S_cow)))',
        'S_before = $srgh_seek(S_cow,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        '$lookup(S_before.ENV,$ptascii("alias298")) = (n_field)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$lookup(S_before.ENV,$ptascii("copy298")) = (n_copycell)', 'S_before.STORE[n_copycell] = DEFINED (PARRAY n_copy)',
        'n_copy = n_cowcopy', '$property_state_valid(S_before)', '$heap_valid($heap_prune($heap_graph(S_before)))',
        'S_retiring = $srgh_seek(S_before,1,n_root,30000)', '$srgh_phase(S_retiring,1,n_root)',
        '$propref_at(S_retiring.PROPREFS,n_field) = (ppropref)',
        'S_detached = $srgh_seek(S_retiring,8,n_root,30000)', '$srgh_phase(S_detached,8,n_root)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$lookup(S_detached.ENV,$ptascii("alias298")) = (n_field)',
        '$propref_at(S_detached.PROPREFS,n_field) = eps', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 1',
        '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)', '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[source.stem]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '$lookup(S_end.ENV,$ptascii("copy298")) = eps',
        '~((HCELL n_copycell) <- S_end.ALLOCATIONS)', '$property_state_valid(S_end)', '$call_descriptors_valid(S_end)',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'phpType18_reverse = NUnionType (SEQUENCE ([NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_first) metadata_first])) metadata_type',
        'statement_reverse = NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_reverse (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_reverse = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reverse) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_reverse,ppropertydesc)', '~$reference_return_source(S_reverse,6)',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = ' + reverse + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,6)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 6)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,6)', '$property_current_line(S_noarrow) = 0',
        'phpType35_array = NIdentifier (BYTES "YXJyYXk=") metadata_type', 'phpType35_null = NIdentifier (BYTES "bnVsbA==") metadata_type',
        'phpType35_int = NIdentifier (BYTES "aW50") metadata_type',
        '~$hook_short_reference_header(phpType35_array,ppropertydesc.TYPE)',
        '~$hook_short_reference_header(NNullableType phpType35_array metadata_type,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "array"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([phpType35_array,phpType35_array])) metadata_type,[(PTBRANCH ([PTBUILTIN "array"])),(PTBRANCH ([PTBUILTIN "array"]))])',
        '$hook_short_reference_header(NUnionType (SEQUENCE ([phpType35_int,phpType35_null])) metadata_type,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([phpType35_array,phpType35_null,phpType35_int])) metadata_type,ppropertydesc.TYPE)',
        '~$hook_short_reference_header(phpType18,ppropertydesc.TYPE ++ [(PTBRANCH ([PTBUILTIN "int"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NName (BYTES "Qm94Mjk4") metadata_type,phpType35_null])) metadata_type,[(PTBRANCH ([PTCLASS ($ptascii("Box298"))])),(PTBRANCH ([PTBUILTIN "null"]))])',
    ]
    if array_null:
        checks += [
            'S_initial = $srgh_seek(S_start,9,n_root,30000)', '$srgh_phase(S_initial,9,n_root)',
            '$objectprops_at(S_initial.OBJECTPROPS,n_root) = ([ppropertyslot_initial])', 'ppropertyslot_initial.STATE = PROP_INITIAL',
            '$srgh_output(S_initial.EVENTS) = $ptascii("U|")', 'S_fetch.STORE[n_field] = DEFINED PNULL',
            '$lookup(S_cow.ENV,$ptascii("seed298")) = (n_seed)', 'S_cow.STORE[n_seed] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("leaf")))',
            'S_cow.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed),ENTRY (KINT 1) (DIRECT (PARRAY n_inner))]',
            'S_cow.ARRAYS[n_cowcopy].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed),ENTRY (KINT 1) (DIRECT (PARRAY n_copyinner))]',
            'n_inner =/= n_copyinner', 'S_cow.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 71))]',
            'S_cow.ARRAYS[n_copyinner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 67))]',
            '$propref_at(S_cow.PROPREFS,n_seed) = eps', '$heap_owners($heap_graph(S_cow),HCELL n_seed) = 3',
            'S_before.STORE[n_field] = DEFINED PNULL', 'S_detached.STORE[n_field] = DEFINED (PINT 79)',
            '~((HARRAY n_copy) <- S_end.ALLOCATIONS)', '~((HCELL n_seed) <- S_end.ALLOCATIONS)',
        ]
    else:
        checks += [
            'S_fetch.STORE[n_field] = DEFINED (PARRAY n_initial)', 'S_fetch.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 83))]',
            'S_cow.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 83)),ENTRY (KINT 1) (DIRECT (PINT 89))]',
            'S_cow.ARRAYS[n_cowcopy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 83))]',
            'S_before.STORE[n_field] = DEFINED (PARRAY n_outer)', '$lookup(S_before.ENV,$ptascii("nested298")) = (n_nestedcell)',
            'S_before.STORE[n_nestedcell] = DEFINED (PARRAY n_nestedcopy)', 'n_outer =/= n_nestedcopy',
            'S_before.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner))]',
            'S_before.ARRAYS[n_nestedcopy].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_copyinner))]', 'n_inner =/= n_copyinner',
            'S_before.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 101))]',
            'S_before.ARRAYS[n_copyinner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 97))]',
            'S_detached.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("released")))',
            '$lookup(S_end.ENV,$ptascii("nested298")) = eps', '~((HCELL n_nestedcell) <- S_end.ALLOCATIONS)',
            '(HARRAY n_nestedcopy) <- $pools_nodes(S_end.POOLS)', 'S_end.POOLS = S_before.POOLS',
        ]
    for label, state in (('return', 'S_return'), ('cleanup', 'S_retiring')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)', f'S_{label}_one = $drive_steps({state},1)',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['array-null', 'null-array'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / (args.form + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), source, SOURCES/'cases.json', *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form)
        report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
