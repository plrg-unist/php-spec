#!/usr/bin/env python3
"""Check typed literal-name short returns, raw type authority and abrupt cleanup."""
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
SOURCES = Path(__file__).with_name('typed_parentless_short_reference_get_hook_review')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box296peer")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("i296peer") \/ $base64(text_name) = $ptascii("tag296peer")
def $srgh_phase(S,9,n) = ($property_hook_plan(S) =/= eps)
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    nullable = form == 'nullable'
    abrupt = form == 'uninitialized'
    field = 'tag' if abrupt else 'i'
    alias = 'tag296peer' if abrupt else 'i296peer'
    phase = 9 if abrupt else 5
    normalized = '[(PTBRANCH ([PTBUILTIN "int"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        f'S_front = $srgh_seek(S_start,{phase},0,30000)', f'$srgh_phase(S_front,{phase},0)',
        'S_front.COMPLETION = NORMAL',
        ('$property_hook_plan(S_front) = (ppropertyhook)' if abrupt else '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))'),
        '$lookup(S_front.ENV,$ptascii("box296peer")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        '$property_effective_desc(S_front,n_root,$ptascii("' + field + '")) = (ppropertydesc)',
        'ppropertydesc.TYPE = ' + normalized, '$property_hook_reference_decl(S_front,ppropertydesc)',
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
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("' + field + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$hook_parameter_facts(metadata_hook) = [false]',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((7,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = (ppropertyslot_front*)',
        '$property_slot_at(ppropertyslot_front*,$ptascii("' + field + '")) = (ppropertyslot)',
        'ppropertyslot.STATE = ' + ('PROP_INITIAL' if abrupt else ('PROP_VALUE (DIRECT PNULL)' if nullable else 'PROP_VALUE (DIRECT (PINT 19))')),
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.COMPLETION = NORMAL', 'S_return.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook', 'pcallcontext_get.RECEIVER = (n_root)',
        'S_return.ORIGIN = (ppropertyhook.HOOK)', 'S_return.TODO = (RETURN_REF_FETCH 7) :: ptask_return*',
        '$property_hook_reference_expression_return(S_return,ppropertyhook.HOOK,7) = (expression_get)',
        '$reference_return_source(S_return,7)', '$reference_return_fetch_valid(S_return,7)',
        '~$reference_return_value_valid(S_return,7)', '$reference_verifies(S_return)',
        '$property_hook_backing(S_return,n_root,ppropertydesc)', '$property_current_line(S_return) = 7',
        '$call_descriptors_valid(S_return)', '$property_state_valid(S_return)',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'S_consumed = $hold_task_inputs(S_return)', '$property_current_line(S_consumed) = 7',
        '~$reference_return_source(S_return,6)', '~$call_task_valid(S_return,RETURN_REF_FETCH 6)',
        'S_wrongorigin = S_return[.ORIGIN = (PORIGIN n_source pcpath_group)]', '$property_current_line(S_wrongorigin) = 0',
        'S_nocurrent = S_return[.CURRENT = eps]', '$property_current_line(S_nocurrent) = 0',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '$property_hook_reference_expression_return(S_noarrow,ppropertyhook.HOOK,7) = eps',
        '~$reference_return_source(S_noarrow,7)', '$property_current_line(S_noarrow) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]]) :: S_return.FUNCTIONS]',
        '$property_hook_reference_expression_return(S_wrongreturn,ppropertyhook.HOOK,7) = eps',
        '~$reference_return_source(S_wrongreturn,7)', '$property_current_line(S_wrongreturn) = 0',
    ]
    scalar = 'NIdentifier (BYTES "aW50") metadata_group'
    null = 'NIdentifier (BYTES "bnVsbA==") metadata_group'
    for label, header in (
        ('absent', 'ABSENT'), ('wrongscalar', 'NIdentifier (BYTES "ZmxvYXQ=") metadata_group'),
        ('nullablemismatch', scalar if nullable else 'NNullableType (' + scalar + ') metadata_group'),
        ('legacyname', 'NIdentifier (BYTES "aW50ZWdlcg==") metadata_group'),
        ('array', 'NIdentifier (BYTES "YXJyYXk=") metadata_group'),
        ('class', 'NName (BYTES "Qm94Mjk2") metadata_group'),
        ('union', 'NUnionType (SEQUENCE ([' + scalar + ',' + null + '])) metadata_group'),
    ):
        promoted = label == 'union' and nullable
        negation = '' if promoted else '~'
        checks += [
            f'phpType18_{label} = {header}', f'{negation}$hook_short_reference_header(phpType18_{label},ppropertydesc.TYPE)',
            f'statement_{label} = NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_{label} (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
            f'S_{label} = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_{label}) :: pcunit.OCCURRENCES]]]',
            f'{negation}$property_hook_reference_decl(S_{label},ppropertydesc)',
            f'$property_hook_reference_expression_return(S_{label},ppropertyhook.HOOK,7) = ' + ('(expression_get)' if promoted else 'eps'),
            f'$property_current_line(S_{label}) = ' + ('7' if promoted else '0'),
        ]
    checks += [
        '$hook_short_reference_header(ABSENT,eps)', '~$hook_short_reference_header(phpType18,eps)',
        '$hook_short_reference_header(phpType18_array,[(PTBRANCH ([PTBUILTIN "array"]))])',
        '~$hook_short_reference_header(phpType18_class,[(PTBRANCH ([PTCLASS ($ptascii("Box296"))]))])',
        '$hook_short_reference_header(phpType18_union,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    ]
    if abrupt:
        message = '$base64(' + peer.quoted('Cannot access uninitialized non-nullable property Ns296UninitializedShortReferencePeer\\Box296::$tag by reference') + ')'
        checks += [
            'S_error = $reference_return_fetch($hold_task_inputs(S_return),S_return.BASE,7)',
            'S_error.COMPLETION = THROWN "Error" (' + message + ') 7',
            'S_error.OBJECTPROPS = S_return.OBJECTPROPS', 'S_error.PROPREFS = S_return.PROPREFS',
            'S_error.STORE = S_return.STORE', 'S_error.REFCELLS = S_return.REFCELLS',
            'S_error.EVENTS = S_return.EVENTS',
            'S_caught = $srgh_seek(S_return,5,n_root,30000)', '$srgh_phase(S_caught,5,n_root)',
            'S_caught.COMPLETION = NORMAL', 'S_caught.CURRENT = eps',
            '$lookup(S_caught.ENV,$ptascii("probe296peer")) = (n_probe)',
            '$lookup(S_caught.ENV,$ptascii("shadow296peer")) = (n_probe)',
            'S_caught.STORE[n_probe] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("stay")))',
            '$objectprops_at(S_caught.OBJECTPROPS,n_root) = (ppropertyslot_front*)',
            'S_caught.PROPREFS = S_front.PROPREFS', 'S_caught.HELD = eps', 'S_caught.FRAMES = eps',
            '$heap_owners($heap_graph(S_caught),HOBJECT n_root) = 1',
            '$call_descriptors_valid(S_caught)', '$property_state_valid(S_caught)',
            '$srgh_output(S_caught.EVENTS) = $ptascii("U|V|Q|")',
        ]
        boundary = 'S_before'
    else:
        checks += [
            'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
            'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_field',
            'S_fetch.STORE[n_field] = DEFINED (' + ('PNULL' if nullable else 'PINT 19') + ')',
            '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
            'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("i")) ppropertydesc.ORIGIN]',
            '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2',
            '$call_descriptors_valid(S_fetch)', '$property_state_valid(S_fetch)',
            'S_nosource = S_fetch[.PROPREFS = eps]', '~$property_state_valid(S_nosource)',
            'S_wrongsource = S_fetch[.PROPREFS = [{CELL n_field,SOURCES ([OBJECT_PROP_SOURCE n_root ($ptascii("f")) ppropertydesc.ORIGIN])}]]',
            '~$property_state_valid(S_wrongsource)',
        ]
        boundary = 'S_fetch' if nullable else 'S_return'
    checks += [
        'S_before = $srgh_seek(S_return,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)',
        'S_before.COMPLETION = NORMAL', 'S_before.CURRENT = eps', 'S_before.FRAMES = eps',
        '$lookup(S_before.ENV,$ptascii("' + alias + '")) = (n_alias)',
        '$propref_at(S_before.PROPREFS,n_alias) = (ppropref_before)',
        'ppropref_before.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("' + field + '")) ppropertydesc.ORIGIN]',
        'S_detached = $srgh_seek(S_before,8,n_root,30000)', '$srgh_phase(S_detached,8,n_root)',
        'S_detached.COMPLETION = NORMAL', '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
        '$lookup(S_detached.ENV,$ptascii("' + alias + '")) = (n_alias)',
        '$propref_at(S_detached.PROPREFS,n_alias) = eps', '$heap_owners($heap_graph(S_detached),HCELL n_alias) = 1',
        '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)',
        '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())['strict-' + form + '-literal']['stdout'] + '")',
        '~((HCELL n_alias) <- S_end.ALLOCATIONS)', '$call_descriptors_valid(S_end)', '$property_state_valid(S_end)',
    ]
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)']
    checks += [f'S_rejoin = $drive_steps({boundary},1)',
               '$drive_steps(S_rejoin[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['scalar', 'nullable', 'uninitialized'])
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
