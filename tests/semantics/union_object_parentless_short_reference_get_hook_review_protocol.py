#!/usr/bin/env python3
"""Check ordered object/null source authority, shared identity and real type removal."""
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
SOURCES = Path(__file__).with_name('union_object_parentless_short_reference_get_hook_review')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box300peer")')
PREFIX = PREFIX.replace('-- if ~$srgh_phase(S,n_stage,n_object) /\\ $(n > 0)',
                        '-- if ~$srgh_phase(S,n_stage,n_object) /\\ $(n > 0) /\\ S.TODO =/= eps')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("ref300peer")
def $srgh_phase(S,9,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("keep300peer")
def $srgh_phase(S,10,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarInt (INTEGER z) metadata_rhs) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("ref300peer") /\ z <- [77,83]
def $srgh_phase(S,11,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NExprNew phpType28 phpType6 metadata_rhs) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias300peer")
def $srgh_phase(S,12,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarInt (INTEGER z) metadata_rhs) metadata_assign)) :: ptask*
  -- if ($base64(text_name) = $ptascii("alias300peer") /\ z = 79) \/ ($base64(text_name) = $ptascii("ref300peer") /\ z = 89)
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    omitted = form == 'object-null'
    order = ['object', 'null'] if omitted else ['null', 'object']
    normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + name + '"]))' for name in order) + ']'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box300peer")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + normalized,
        'ppropertydesc.TYPE = [ptbranch_first,ptbranch_second]', 'ppropertydesc.NAME = $ptascii("slot")',
        '$property_hook_reference_decl(S_front,ppropertydesc)', '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'pfunction_get.CODE.STRICT', 'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook', 'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]', 'pfunction_get.CODE.UNIT = n_source',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([phpType69_first,phpType69_second])) metadata_union',
        'phpType69_first = NIdentifier (BYTES text_first) metadata_first',
        'phpType69_second = NIdentifier (BYTES text_second) metadata_second',
        '$base64(text_first) = $ptascii("' + order[0] + '")', '$base64(text_second) = $ptascii("' + order[1] + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("?object")',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("slot")',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((7,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 7) :: ptask_return*', '$reference_return_source(S_return,7)',
        '$reference_return_fetch_valid(S_return,7)', '$reference_verifies(S_return)', '$property_current_line($hold_task_inputs(S_return)) = 7',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = [ptbranch_second,ptbranch_first]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,7)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 7)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,7)', '$property_current_line(S_noarrow) = 0',
        '~$property_hook_reference_decl(S_return,ppropertydesc[.TYPE = [ptbranch_second,ptbranch_first]])',
        '~$property_hook_reference_decl(S_return,ppropertydesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '$property_hook_function(S_return,ppropertyhook[.OBJECT = |S_return.OBJECTS|]) = eps',
        '~$hook_short_reference_header(phpType18,[ptbranch_second,ptbranch_first])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([phpType69_second,phpType69_first])) metadata_union,ppropertydesc.TYPE)',
        '$hook_short_reference_header(NUnionType (SEQUENCE ([phpType69_second,phpType69_first])) metadata_union,[ptbranch_second,ptbranch_first])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([phpType69_first,phpType69_first])) metadata_union,[ptbranch_first,ptbranch_first])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([phpType69_first,phpType69_second,phpType69_first])) metadata_union,[ptbranch_first,ptbranch_second,ptbranch_first])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NName (BYTES text_first) metadata_first,phpType69_second])) metadata_union,ppropertydesc.TYPE)',
        '$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") metadata_first,NIdentifier (BYTES "bnVsbA==") metadata_second])) metadata_union,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "b2JqZWN0") metadata_first,NIdentifier (BYTES "YXJyYXk=") metadata_second])) metadata_union,[(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "array"]))])',
        '~$hook_short_reference_header(NNullableType (NIdentifier (BYTES "b2JqZWN0") metadata_first) metadata_union,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "object"]))])',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_wrongorder = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([phpType69_second,phpType69_first])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_wrongsource = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_wrongorder) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_wrongsource,ppropertydesc)', '~$reference_return_source(S_wrongsource,7)',
        'phpType38_explicit = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get ($srgh_explicit(metadata_hook))',
        'statement_explicit = NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38_explicit])) metadata_group',
        'S_explicit = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_explicit) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_explicit,ppropertydesc)', '~$reference_return_source(S_explicit,7)',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)', 'S_fetch.COMPLETION = NORMAL',
        'S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("slot")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2', '$call_descriptors_valid(S_fetch)', '$property_state_valid(S_fetch)',
        'S_nosource = S_fetch[.PROPREFS = eps]', '~$property_state_valid(S_nosource)',
        'S_reject = $srgh_seek(S_fetch,10,n_root,30000)', '$srgh_phase(S_reject,10,n_root)', 'S_reject.COMPLETION = NORMAL',
        '$lookup(S_reject.ENV,$ptascii("ref300peer")) = (n_field)', '$lookup(S_reject.ENV,$ptascii("alias300peer")) = (n_field)',
        'S_reject.STORE[n_field] = DEFINED PNULL', '$heap_owners($heap_graph(S_reject),HCELL n_field) = 3',
        '$lookup(S_reject.ENV,$ptascii("copy300peer")) = (n_copycell)', 'S_reject.STORE[n_copycell] = DEFINED (POBJECT n_old)',
        '$heap_owners($heap_graph(S_reject),HOBJECT n_old) = 1', '$propref_at(S_reject.PROPREFS,n_field) = (ppropref)',
        'S_aftercatch = $srgh_seek(S_reject,11,n_root,30000)', '$srgh_phase(S_aftercatch,11,n_root)', 'S_aftercatch.COMPLETION = NORMAL',
        'S_aftercatch.STORE[n_field] = DEFINED PNULL', '$propref_at(S_aftercatch.PROPREFS,n_field) = (ppropref)',
        'S_before = $srgh_seek(S_aftercatch,' + ('0' if omitted else '9') + ',n_root,30000)',
        '$srgh_phase(S_before,' + ('0' if omitted else '9') + ',n_root)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (POBJECT n_live)', 'n_live =/= n_old',
        'S_before.STORE[n_copycell] = DEFINED (POBJECT n_old)', '$heap_owners($heap_graph(S_before),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 1', '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
        '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        'S_unset_one = $drive_steps(S_before,1)', 'S_unset_one.COMPLETION = BUDGET',
        'S_detached = $srgh_seek(S_unset_one,12,n_root,30000)', '$srgh_phase(S_detached,12,n_root)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2', 'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)',
        '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)', '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_finalunset = $srgh_seek(S_detached,8,n_root,30000)', '$srgh_phase(S_finalunset,8,n_root)',
        'S_finalunset.STORE[n_field] = DEFINED (PINT ' + ('79' if omitted else '89') + ')',
        '~((HOBJECT n_live) <- S_finalunset.ALLOCATIONS)', '(HOBJECT n_old) <- S_finalunset.ALLOCATIONS',
        'S_end = $drive_steps(S_finalunset,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copycell) <- S_end.ALLOCATIONS)', '~((HOBJECT n_old) <- S_end.ALLOCATIONS)',
        '$call_descriptors_valid(S_end)', '$property_state_valid(S_end)', '$heap_valid($heap_prune($heap_graph(S_end)))',
    ]
    checks += (['ppropertyslot_initial.STATE = PROP_INITIAL', 'S_fetch.STORE[n_field] = DEFINED PNULL'] if omitted else [
        'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (POBJECT n_initial))', 'S_fetch.STORE[n_field] = DEFINED (POBJECT n_initial)',
        '$lookup(S_reject.ENV,$ptascii("box300peer")) = eps', '$lookup(S_reject.ENV,$ptascii("keep300peer")) = (n_keep)',
        'S_reject.STORE[n_keep] = DEFINED (POBJECT n_root)', '$heap_owners($heap_graph(S_reject),HOBJECT n_root) = 1',
    ])
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_zero[.COMPLETION = NORMAL],30000) = S_end',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['object-null', 'null-object'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('strict-' + args.form + '-literal.php')
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
