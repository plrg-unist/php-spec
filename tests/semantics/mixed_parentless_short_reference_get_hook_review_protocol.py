#!/usr/bin/env python3
"""Check mixed reference sources, primitive tags, COW, identity and quiet removal."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import null_parentless_short_reference_get_hook_review_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('mixed_parentless_short_reference_get_hook_review')
PREFIX = prior.PREFIX.replace('304peer', '305peer')


def fields(fixture, source, form):
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box305peer")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("v")',
        'ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]', '$property_hook_reference_decl(S_front,ppropertydesc)',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NIdentifier (BYTES text_type) metadata_type',
        '$base64(text_type) = $ptascii("mixed")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("mixed")',
        '~$hook_short_reference_header(phpType18,eps)', '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = eps])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}', 'pfunction.CODE.STRICT',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_expression) = 4', '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((4,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (4)',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_VALUE (DIRECT PNULL)' if form == 'initialized' else 'PROP_INITIAL'),
        '$lbr_output(S_front.EVENTS) = $ptascii("B|")',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 4) :: ptask_return*',
        '$reference_return_source(S_return,4)', '$reference_return_fetch_valid(S_return,4)', '~$reference_verifies(S_return)',
        '$property_current_line(S_return) = 4', '$property_current_line($hold_task_inputs(S_return)) = 4',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,4)', '$property_current_line(S_noarrow) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = eps]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,4)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 4)',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_badraw = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NIdentifier (BYTES "bnVsbA==") metadata_type) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_badraw) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,4)',
        'S_copied = $lbr_seek(S_return,10,30000)', '$lbr_phase(S_copied,10)', 'S_copied.COMPLETION = NORMAL',
        '$lbr_output(S_copied.EVENTS) = $ptascii("B|C|")',
        '$objectprops_at(S_copied.OBJECTPROPS,n_root) = ([ppropertyslot_copied])',
        'ppropertyslot_copied.STATE = PROP_VALUE (ALIAS n_field)', 'S_copied.STORE[n_field] = DEFINED PNULL',
        '$propref_at(S_copied.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$lookup(S_copied.ENV,$ptascii("copy305peer")) = (n_copy)', 'n_copy =/= n_field',
        'S_copied.STORE[n_copy] = DEFINED PNULL', '$propref_at(S_copied.PROPREFS,n_copy) = eps',
        '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1',
        'S_reffront = $lbr_seek(S_copied,-5,30000)', '$lbr_phase(S_reffront,-5)',
        '$property_hook_ref_plan(S_reffront) = ((ppropertyhook_ref,"fetch"))',
        'ppropertyhook_ref.OBJECT = n_root', 'ppropertyhook_ref.PROPERTY = ppropertydesc.ORIGIN',
        'S_reffront.STORE[n_copy] = DEFINED (PBOOL false)', 'S_reffront.STORE[n_field] = DEFINED PNULL',
        'S_refreturn = $lbr_seek(S_reffront,-1,30000)', '$lbr_phase(S_refreturn,-1)', '~$reference_verifies(S_refreturn)',
        'S_fetch = $lbr_seek(S_refreturn,-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED PNULL',
        'S_aliases = $lbr_seek(S_fetch,14,30000)', '$lbr_phase(S_aliases,14)',
        '$lookup(S_aliases.ENV,$ptascii("ref305peer")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("alias305peer")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED PNULL', 'S_aliases.STORE[n_copy] = DEFINED (PBOOL false)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        '$lbr_output(S_aliases.EVENTS) = $ptascii("B|C|V|")',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
    ]
    if form == 'omitted':
        checks += ['phpType5 = ABSENT']
    current = 'S_aliases'
    states = ['S_return', 'S_copied', 'S_reffront', 'S_aliases']
    for label, line, value in [('false', 16, 'PBOOL false'), ('true', 18, 'PBOOL true'),
                               ('integer', 20, 'PINT 0'), ('string', 22, 'pvalue_string'),
                               ('float', 24, 'PFLOAT 4609434218613702656'), ('null', 26, 'PNULL')]:
        state = 'S_' + label
        checks += [f'{state} = $lbr_seek({current},{line},30000)', f'$lbr_phase({state},{line})',
                   f'{state}.STORE[n_field] = DEFINED ({value})', f'$propref_at({state}.PROPREFS,n_field) = (ppropref)',
                   f'$heap_owners($heap_graph({state}),HCELL n_field) = 3']
        current = state
        states += [state]
    checks += [
        '$string_bytes(pvalue_string) = ($ptascii("0"))',
        'S_array = $lbr_seek(S_null,30,30000)', '$lbr_phase(S_array,30)',
        'S_array.STORE[n_field] = DEFINED (PARRAY n_live_array)',
        '$lookup(S_array.ENV,$ptascii("arraycopy305peer")) = (n_arraycopy)',
        'S_array.STORE[n_arraycopy] = DEFINED (PARRAY n_copy_array)', 'n_live_array =/= n_copy_array',
        'S_array.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        'S_array.ARRAYS[n_copy_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$propref_at(S_array.PROPREFS,n_field) = (ppropref)', '$propref_at(S_array.PROPREFS,n_arraycopy) = eps',
        'S_object = $lbr_seek(S_array,34,30000)', '$lbr_phase(S_object,34)',
        'S_object.STORE[n_field] = DEFINED (POBJECT n_child)', 'S_object.OBJECTS[n_child] = STDINSTANCE',
        '$lookup(S_object.ENV,$ptascii("objectcopy305peer")) = (n_objectcopy)',
        'S_object.STORE[n_objectcopy] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_object.OBJECTPROPS,n_child) = ([ppropertyslot_child])',
        'ppropertyslot_child.NAME = $ptascii("value")', 'ppropertyslot_child.STATE = PROP_VALUE (DIRECT (PINT 3))',
        '$heap_owners($heap_graph(S_object),HOBJECT n_child) = 2',
        '$propref_at(S_object.PROPREFS,n_field) = (ppropref)', '$propref_at(S_object.PROPREFS,n_objectcopy) = eps',
        'S_before = $lbr_seek(S_object,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (PINT 37)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3', '$heap_owners($heap_graph(S_before),HOBJECT n_child) = 1',
        '$lbr_output(S_before.EVENTS) = $ptascii("B|C|V|F|T|I|S|D|N|A|O|K|")',
        'S_detached = $lbr_seek(S_before,37,30000)', '$lbr_phase(S_detached,37)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        'S_detached.STORE[n_field] = DEFINED (PINT 37)', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_written.STORE[n_field] = DEFINED pvalue_tail', '$string_bytes(pvalue_tail) = ($ptascii("tail"))',
        'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
        'S_written.STORE[n_arraycopy] = DEFINED (PARRAY n_copy_array)',
        'S_written.STORE[n_objectcopy] = DEFINED (POBJECT n_child)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
    ]
    checks += ['(HARRAY n_copy_array) <- $pools_nodes(S_end.POOLS)',
               '(HARRAY n_copy_array) <- S_end.ALLOCATIONS', 'S_end.POOLS = S_before.POOLS']
    for node in ('HCELL n_field', 'HCELL n_copy', 'HCELL n_arraycopy', 'HCELL n_objectcopy', 'HARRAY n_live_array', 'HOBJECT n_child'):
        checks += ['~((' + node + ') <- S_end.ALLOCATIONS)']
    mixed = '[(PTBRANCH ([PTBUILTIN "mixed"]))]'
    for strict in ('false', 'true'):
        for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'pvalue_string', 'PFLOAT 4609434218613702656', 'PARRAY n_live_array', 'POBJECT n_child'):
            checks += ['$propref_class(S_object,' + mixed + ',' + value + ',' + strict + ') = PROP_EXACT']
    for first, second in [('mixed', 'null'), ('null', 'mixed'), ('null', 'null')]:
        left = 'NIdentifier (BYTES ' + peer.quoted(first) + ') eps'
        right = 'NIdentifier (BYTES ' + peer.quoted(second) + ') eps'
        normalized = '[(PTBRANCH ([PTBUILTIN "' + first + '"])),(PTBRANCH ([PTBUILTIN "' + second + '"]))]'
        checks += ['~$hook_short_reference_header(NUnionType (SEQUENCE ([' + left + ',' + right + '])) eps,' + normalized + ')']
    for kind in ('mixed', 'null'):
        checks += ['~$hook_short_reference_header(NNullableType (NIdentifier (BYTES ' + peer.quoted(kind) + ') eps) eps,[(PTBRANCH ([PTBUILTIN "' + kind + '"])),(PTBRANCH ([PTBUILTIN "null"]))])']
    checks += ['$hook_short_reference_header(NIdentifier (BYTES ' + peer.quoted('MiXeD') + ') eps,' + mixed + ')',
               '~$hook_short_reference_header(NIdentifier (BYTES ' + peer.quoted('null') + ') eps,' + mixed + ')',
               '~$hook_short_reference_header(phpType18,[(PTBRANCH ([PTBUILTIN "null"]))])']
    for state in [*states, 'S_array', 'S_object', 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$call_descriptors_valid(' + state + ')', '$property_state_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['initialized', 'omitted'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((SOURCES/'cases.json').read_text())
    source = SOURCES/cases[args.form]['source']
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(peer.__file__), source,
             SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'),
                           str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form)
        report['premises'] = len(checks)
        (out/'assertions.json').write_text(json.dumps(checks, indent=2)+'\n')
        (out/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if '+check+'\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
