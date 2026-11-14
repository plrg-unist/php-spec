#!/usr/bin/env python3
"""Check object identity, real typed cells, failed binding and receiver cleanup."""
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
SOURCES = Path(__file__).with_name('object_parentless_short_reference_get_hook')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box299")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias299")
def $srgh_phase(S,9,n) = ($property_hook_plan(S) =/= eps)
def $srgh_phase(S,10,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarInt (INTEGER 53) metadata_int) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("probe299")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    nullable = form == 'nullable'
    abrupt = form == 'uninitialized'
    phase = 9 if abrupt else 5
    normalized = '[(PTBRANCH ([PTBUILTIN "object"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        f'S_front = $srgh_seek(S_start,{phase},0,30000)', f'$srgh_phase(S_front,{phase},0)',
        'S_front.COMPLETION = NORMAL',
        ('$property_hook_plan(S_front) = (ppropertyhook)' if abrupt else '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))'),
        '$lookup(S_front.ENV,$ptascii("box299")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps', 'pclassdesc_root.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.NAME = $ptascii("item")', 'ppropertydesc.TYPE = ' + normalized,
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
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_item) metadata_itemname) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_item) = ppropertydesc.NAME',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$hook_parameter_facts(metadata_hook) = [false]',
        '$source_line(metadata_hook) = 5', '$source_line(metadata_expression) = 6',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((6,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (6)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 6]',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.COMPLETION = NORMAL', 'S_return.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook', 'S_return.ORIGIN = (ppropertyhook.HOOK)',
        '$reference_return_source(S_return,6)', '$reference_return_fetch_valid(S_return,6)',
        '$property_hook_backing(S_return,n_root,ppropertydesc)', '$property_current_line(S_return) = 6',
        '$property_current_line($hold_task_inputs(S_return)) = 6', '$reference_verifies(S_return)',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,6)', '$property_current_line(S_noarrow) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,6)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 6)',
        '~$reference_return_source(S_return,5)', '~$call_task_valid(S_return,RETURN_REF_FETCH 5)',
    ]
    object_header = 'NIdentifier (BYTES "b2JqZWN0") metadata_group'
    null_header = 'NIdentifier (BYTES "bnVsbA==") metadata_group'
    for label, header in (
        ('absent', 'ABSENT'), ('array', 'NIdentifier (BYTES "YXJyYXk=") metadata_group'),
        ('class', 'NName (BYTES "Qm94Mjk5") metadata_group'),
        ('nullablemismatch', object_header if nullable else 'NNullableType (' + object_header + ') metadata_group'),
        ('union', 'NUnionType (SEQUENCE ([' + object_header + ',' + null_header + '])) metadata_group'),
    ):
        checks += [
            f'phpType18_{label} = {header}', f'~$hook_short_reference_header(phpType18_{label},ppropertydesc.TYPE)',
            f'statement_{label} = NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_{label} (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
            f'S_{label} = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_{label}) :: pcunit.OCCURRENCES]]]',
            f'~$property_hook_reference_decl(S_{label},ppropertydesc)', f'~$reference_return_source(S_{label},6)',
        ]
    checks += [
        '~$hook_short_reference_header(NName (BYTES "Qm94Mjk5") metadata_group,[(PTBRANCH ([PTCLASS ($ptascii("Box299"))]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([' + object_header + ',' + null_header + '])) metadata_group,[(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") metadata_group,' + null_header + '])) metadata_group,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    ]
    if abrupt:
        message = '$base64(' + peer.quoted('Cannot access uninitialized non-nullable property Ns299UninitializedObjectShortReference\\Box299::$item by reference') + ')'
        checks += [
            '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])', 'ppropertyslot_initial.STATE = PROP_INITIAL',
            'S_error = $reference_return_fetch($hold_task_inputs(S_return),S_return.BASE,6)',
            'S_error.COMPLETION = THROWN "Error" (' + message + ') 6',
            'S_error.OBJECTPROPS = S_return.OBJECTPROPS', 'S_error.PROPREFS = S_return.PROPREFS',
            'S_error.STORE = S_return.STORE', 'S_error.REFCELLS = S_return.REFCELLS',
            'S_failed = $srgh_seek(S_return,10,n_root,30000)', '$srgh_phase(S_failed,10,n_root)',
            '$lookup(S_failed.ENV,$ptascii("probe299")) = (n_oldcell)', '$lookup(S_failed.ENV,$ptascii("shadow299")) = (n_oldcell)',
            'S_failed.STORE[n_oldcell] = DEFINED (POBJECT n_probe)', '$propref_at(S_failed.PROPREFS,n_oldcell) = eps',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
            '$srgh_output(S_failed.EVENTS) = $ptascii("U|V|E|K|")', '$property_state_valid(S_failed)',
            'S_bound = $srgh_seek(S_failed,5,n_root,30000)', '$srgh_phase(S_bound,5,n_root)',
            'S_bound.STORE[n_oldcell] = DEFINED (PINT 53)', '$propref_at(S_bound.PROPREFS,n_oldcell) = eps',
            'S_fetch = $srgh_seek(S_bound,7,n_root,30000)',
        ]
    else:
        checks += ['S_fetch = $srgh_seek(S_return,7,n_root,30000)']
    checks += [
        '$srgh_phase(S_fetch,7,n_root)', 'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_field',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("item")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2', '$property_state_valid(S_fetch)', '$call_descriptors_valid(S_fetch)',
        'S_nosource = S_fetch[.PROPREFS = eps]', '~$property_state_valid(S_nosource)',
        'S_before = $srgh_seek(S_fetch,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        '$lookup(S_before.ENV,$ptascii("alias299")) = (n_field)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        'S_before.STORE[n_field] = DEFINED (POBJECT n_second)',
        '$lookup(S_before.ENV,$ptascii("second299")) = (n_secondcell)', 'S_before.STORE[n_secondcell] = DEFINED (POBJECT n_second)',
        '$lookup(S_before.ENV,$ptascii("copy299")) = (n_copycell)', 'S_before.STORE[n_copycell] = DEFINED (POBJECT n_copy)',
        'n_copy =/= n_second', '$propref_at(S_before.PROPREFS,n_copycell) = eps',
        '$objectprops_at(S_before.OBJECTPROPS,n_copy) = (ppropertyslot_copy*)',
        '$property_slot_at(ppropertyslot_copy*,$ptascii("tag")) = (ppropertyslot_copytag)',
        'ppropertyslot_copytag.STATE = PROP_VALUE (DIRECT (PINT ' + ('37' if nullable else '59' if abrupt else '19') + '))',
        '$property_state_valid(S_before)', '$heap_valid($heap_prune($heap_graph(S_before)))',
        'S_retiring = $srgh_seek(S_before,1,n_root,30000)', '$srgh_phase(S_retiring,1,n_root)',
        '$propref_at(S_retiring.PROPREFS,n_field) = (ppropref)',
        'S_detached = $srgh_seek(S_retiring,8,n_root,30000)', '$srgh_phase(S_detached,8,n_root)',
        'S_detached.COMPLETION = NORMAL', '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
        '$lookup(S_detached.ENV,$ptascii("alias299")) = (n_field)',
        '$propref_at(S_detached.PROPREFS,n_field) = eps', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 1',
        '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)', '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[source.stem]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HOBJECT n_copy) <- S_end.ALLOCATIONS)', '~((HOBJECT n_second) <- S_end.ALLOCATIONS)',
        '$property_state_valid(S_end)', '$call_descriptors_valid(S_end)',
    ]
    if nullable:
        checks += ['S_fetch.STORE[n_field] = DEFINED PNULL', 'S_detached.STORE[n_field] = DEFINED (PARRAY n_released)']
    else:
        checks += ['S_fetch.STORE[n_field] = DEFINED (POBJECT n_initial)',
                   'S_detached.STORE[n_field] = DEFINED ' + ('PNULL' if abrupt else '(PSTRING_CARRIER INTERNED_STRING ($ptascii("released")))')]
    for label, state in (('return', 'S_return'), ('cleanup', 'S_retiring')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['object', 'nullable', 'uninitialized'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('object-identity.php' if args.form == 'object' else args.form + '-object.php')
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
