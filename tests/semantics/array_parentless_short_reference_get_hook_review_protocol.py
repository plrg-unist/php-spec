#!/usr/bin/env python3
"""Check array short reference Get, real COW cells, type sources and detach."""
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
SOURCES = Path(__file__).with_name('array_parentless_short_reference_get_hook_review')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box297peer")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias297peer")
def $srgh_phase(S,9,n) = ($property_hook_plan(S) =/= eps)
def $srgh_phase(S,10,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NExprConstFetch (NName (BYTES text_null) metadata_null) metadata_fetch) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias297peer") /\ $ptlc($base64(text_null)) = $ptascii("null")
def $srgh_phase(S,11,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprArrayDimFetch (NExprVariable (BYTES text_name) metadata_name) ABSENT metadata_dim) expression_rhs metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("probe297peer")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    nullable = form == 'nullable'
    abrupt = form == 'uninitialized'
    normalized = '[(PTBRANCH ([PTBUILTIN "array"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
    phase = 9 if abrupt else 5
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        f'S_front = $srgh_seek(S_start,{phase},0,30000)', f'$srgh_phase(S_front,{phase},0)', 'S_front.COMPLETION = NORMAL',
        ('$property_hook_plan(S_front) = (ppropertyhook)' if abrupt else '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))'),
        '$lookup(S_front.ENV,$ptascii("box297peer")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("items")',
        'ppropertydesc.TYPE = ' + normalized, '$property_hook_reference_decl(S_front,ppropertydesc)',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook', 'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("items")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$hook_parameter_facts(metadata_hook) = [false]',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)', 'S_return.COMPLETION = NORMAL',
        'S_return.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
        'S_return.ORIGIN = (ppropertyhook.HOOK)', 'S_return.TODO = (RETURN_REF_FETCH 7) :: ptask_return*',
        '$property_hook_reference_expression_return(S_return,ppropertyhook.HOOK,7) = (expression_get)',
        '$reference_return_source(S_return,7)', '$reference_verifies(S_return)',
        '$property_current_line($hold_task_inputs(S_return)) = 7',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_wrongtype = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NIdentifier (BYTES "aW50") metadata_group) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_wrongtype = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_wrongtype) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_wrongtype,ppropertydesc)', '~$reference_return_source(S_wrongtype,7)',
        '$property_current_line(S_wrongtype) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,7)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 7)',
        '~$hook_short_reference_header(phpType18,[(PTBRANCH ([PTBUILTIN "int"]))])',
        '~$hook_short_reference_header(NName (BYTES "Qm94Mjk3") metadata_group,[(PTBRANCH ([PTCLASS ($ptascii("Box297"))]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "YXJyYXk=") metadata_group,NIdentifier (BYTES "bnVsbA==") metadata_group])) metadata_group,[(PTBRANCH ([PTBUILTIN "array"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NNullableType (NIdentifier (BYTES "YXJyYXk=") metadata_group) metadata_group,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "array"]))])',
    ]
    if abrupt:
        message = '$base64(' + peer.quoted('Cannot access uninitialized non-nullable property Ns297UninitializedArrayShortReferencePeer\\Box297::$items by reference') + ')'
        checks += [
            '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])', 'ppropertyslot_initial.STATE = PROP_INITIAL',
            'S_error = $reference_return_fetch($hold_task_inputs(S_return),S_return.BASE,7)',
            'S_error.COMPLETION = THROWN "Error" (' + message + ') 7',
            'S_error.OBJECTPROPS = S_return.OBJECTPROPS', 'S_error.PROPREFS = S_return.PROPREFS',
            'S_error.STORE = S_return.STORE', 'S_error.REFCELLS = S_return.REFCELLS',
            'S_caught = $srgh_seek(S_return,5,n_root,30000)', '$srgh_phase(S_caught,5,n_root)', 'S_caught.COMPLETION = NORMAL',
            '$lookup(S_caught.ENV,$ptascii("probe297peer")) = (n_probe)', '$lookup(S_caught.ENV,$ptascii("shadow297peer")) = (n_probe)',
            'S_caught.STORE[n_probe] = DEFINED (PARRAY n_probe_array)', 'S_caught.ARRAYS[n_probe_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]',
            '$propref_at(S_caught.PROPREFS,n_probe) = eps', '$objectprops_at(S_caught.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
            'S_caught.CURRENT = eps', 'S_caught.FRAMES = eps', 'S_caught.HELD = eps',
            '$heap_owners($heap_graph(S_caught),HOBJECT n_root) = 1', '$call_descriptors_valid(S_caught)', '$property_state_valid(S_caught)',
            'S_post = $srgh_seek(S_caught,11,n_root,30000)', '$srgh_phase(S_post,11,n_root)', 'S_post.COMPLETION = NORMAL',
            '$lookup(S_post.ENV,$ptascii("probe297peer")) = (n_probe)', '$lookup(S_post.ENV,$ptascii("shadow297peer")) = (n_probe)',
            'S_post.STORE[n_probe] = DEFINED (PARRAY n_probe_array)', '$propref_at(S_post.PROPREFS,n_probe) = eps',
            '$objectprops_at(S_post.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
            'S_post.CURRENT = eps', 'S_post.FRAMES = eps', 'S_post.HELD = eps',
            '$srgh_output(S_post.EVENTS) = $ptascii("U|V|E|K|")', '$property_state_valid(S_post)',
        ]
    else:
        checks += [
            'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
            'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_field',
            'S_fetch.STORE[n_field] = DEFINED (' + ('PNULL' if nullable else 'PARRAY n_shared') + ')',
            '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
            'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("items")) ppropertydesc.ORIGIN]',
            '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2', '$call_descriptors_valid(S_fetch)', '$property_state_valid(S_fetch)',
            'S_nosource = S_fetch[.PROPREFS = eps]', '~$property_state_valid(S_nosource)',
        ]
        if not nullable:
            checks += ['$lookup(S_fetch.ENV,$ptascii("copy297peer")) = (n_copycell_initial)',
                       'S_fetch.STORE[n_copycell_initial] = DEFINED (PARRAY n_shared)',
                       '$heap_owners($heap_graph(S_fetch),HARRAY n_shared) = 2']
    if nullable:
        checks += [
            'S_cow = $srgh_seek(S_return,10,n_root,30000)', '$srgh_phase(S_cow,10,n_root)', 'S_cow.COMPLETION = NORMAL',
            '$lookup(S_cow.ENV,$ptascii("alias297peer")) = (n_cowcell)', 'S_cow.STORE[n_cowcell] = DEFINED (PARRAY n_live)',
            '$lookup(S_cow.ENV,$ptascii("copy297peer")) = (n_copycell)', 'S_cow.STORE[n_copycell] = DEFINED (PARRAY n_copy)',
            'n_live =/= n_copy', 'S_cow.ARRAYS[n_live].ITEMS = [ENTRY (KSTRING ($ptascii("nested"))) (DIRECT (PARRAY n_live_inner))]',
            'S_cow.ARRAYS[n_copy].ITEMS = [ENTRY (KSTRING ($ptascii("nested"))) (DIRECT (PARRAY n_copy_inner))]',
            'n_live_inner =/= n_copy_inner', 'S_cow.ARRAYS[n_live_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 37))]',
            'S_cow.ARRAYS[n_copy_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31))]',
            '$propref_at(S_cow.PROPREFS,n_cowcell) = (ppropref_cow)', 'ppropref_cow.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("items")) ppropertydesc.ORIGIN]',
            '$property_state_valid(S_cow)', '$heap_valid($heap_prune($heap_graph(S_cow)))',
        ]
    checks += [
        'S_before = $srgh_seek(S_return,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        'S_before.CURRENT = eps', 'S_before.FRAMES = eps', '$lookup(S_before.ENV,$ptascii("alias297peer")) = (n_alias)',
        '$propref_at(S_before.PROPREFS,n_alias) = (ppropref_before)',
        'ppropref_before.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("items")) ppropertydesc.ORIGIN]',
        '$lookup(S_before.ENV,$ptascii("copy297peer")) = (n_copycell_before)', 'S_before.STORE[n_copycell_before] = DEFINED (PARRAY n_copy_before)',
        'S_before.STORE[n_alias] = DEFINED (' + ('PNULL' if nullable else 'PARRAY n_live_before') + ')',
        '$property_state_valid(S_before)', '$heap_valid($heap_prune($heap_graph(S_before)))',
    ]
    if form == 'array':
        checks += [
            'n_live_before =/= n_copy_before', '$lookup(S_before.ENV,$ptascii("seed297peer")) = (n_seed)',
            'S_before.STORE[n_seed] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("leaf")))', '$propref_at(S_before.PROPREFS,n_seed) = eps',
            'S_before.ARRAYS[n_live_before].ITEMS = [ENTRY (KSTRING ($ptascii("slot"))) (ALIAS n_seed),ENTRY (KSTRING ($ptascii("nested"))) (DIRECT (PARRAY n_live_inner_before)),ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PINT 17))]',
            'S_before.ARRAYS[n_copy_before].ITEMS = [ENTRY (KSTRING ($ptascii("slot"))) (ALIAS n_seed),ENTRY (KSTRING ($ptascii("nested"))) (DIRECT (PARRAY n_copy_inner_before))]',
            'n_live_inner_before =/= n_copy_inner_before', 'S_before.ARRAYS[n_live_inner_before].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
            'S_before.ARRAYS[n_copy_inner_before].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23))]',
            '$heap_owners($heap_graph(S_before),HCELL n_seed) = 3',
        ]
    elif abrupt:
        checks += ['n_live_before =/= n_copy_before', 'S_before.ARRAYS[n_live_before].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 47)),ENTRY (KINT 1) (DIRECT (PINT 53))]',
                   'S_before.ARRAYS[n_copy_before].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 47))]',
                   'S_before.STORE[n_probe] = DEFINED (PARRAY n_probe_after)', 'S_before.ARRAYS[n_probe_after].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41)),ENTRY (KINT 1) (DIRECT (PINT 43))]',
                   '$propref_at(S_before.PROPREFS,n_probe) = eps']
    else:
        checks += ['n_copy_before = n_copy', '~((HARRAY n_live) <- S_before.ALLOCATIONS)', '~((HARRAY n_live_inner) <- S_before.ALLOCATIONS)']
    checks += [
        'S_detached = $srgh_seek(S_before,8,n_root,30000)', '$srgh_phase(S_detached,8,n_root)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$lookup(S_detached.ENV,$ptascii("alias297peer")) = (n_alias)',
        '$propref_at(S_detached.PROPREFS,n_alias) = eps', '$heap_owners($heap_graph(S_detached),HCELL n_alias) = 1',
        'S_detached.STORE[n_alias] = DEFINED (' + ('PNULL' if abrupt else ('PSTRING_CARRIER INTERNED_STRING ($ptascii("released"))' if nullable else 'PINT 29')) + ')',
        '(HARRAY n_copy_before) <- S_detached.ALLOCATIONS', '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)',
        '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[source.stem]['stdout'] + '")',
        '~((HCELL n_alias) <- S_end.ALLOCATIONS)',
        ('~((HARRAY n_copy_before) <- S_end.ALLOCATIONS)' if form == 'array' else '(HARRAY n_copy_before) <- $pools_nodes(S_end.POOLS)'),
        '$call_descriptors_valid(S_end)', '$property_state_valid(S_end)',
    ]
    if form != 'array':
        checks += ['$lookup(S_end.ENV,$ptascii("copy297peer")) = eps', '~((HCELL n_copycell_before) <- S_end.ALLOCATIONS)',
                   'S_end.POOLS = S_before.POOLS', '(HARRAY n_copy_before) <- S_end.ALLOCATIONS']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)', f'S_{label}_one = $drive_steps({state},1)']
    boundary = 'S_before' if abrupt else ('S_cow' if nullable else 'S_return')
    checks += [f'S_rejoin = $drive_steps({boundary},1)', '$drive_steps(S_rejoin[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['array', 'nullable', 'uninitialized'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    names = {'array': 'strict-array-cow-literal', 'nullable': 'strict-nullable-array-literal', 'uninitialized': 'strict-uninitialized-array-literal'}
    source = SOURCES / (names[args.form] + '.php')
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
