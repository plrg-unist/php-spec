#!/usr/bin/env python3
"""Check real mixed sources, uncoerced tags, COW, identity and quiet detach."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import null_parentless_short_reference_get_hook_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('mixed_parentless_short_reference_get_hook')
PREFIX = prior.PREFIX.replace('304', '305')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,11,n) = true
  -- if S.TODO = (EVAL (NExprAssign expression_left expression_right metadata)) :: ptask*
  -- if $source_line(metadata) = n
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    mixed = '[(PTBRANCH ([PTBUILTIN "mixed"]))]'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box305")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_v]', 'ppropertydesc_v.TYPE = ' + mixed,
        'ppropertydesc_v.NAME = $ptascii("v")', 'ppropertydesc_v.KEY = ppropertydesc_v.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc_v)',
        'ppropertydesc_v.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NIdentifier (BYTES text_mixed) metadata_mixed', '$base64(text_mixed) = $ptascii("mixed")',
        '$hook_short_reference_header(phpType18,ppropertydesc_v.TYPE)', '$pttypename(ppropertydesc_v.TYPE) = $ptascii("mixed")',
        '~$hook_short_reference_header(phpType18,eps)', '~$property_hook_reference_decl(S_front,ppropertydesc_v[.TYPE = eps])',
        '$property_hook_origin(S_front,ppropertydesc_v) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_v.TYPE, BYREF true}',
        '~pfunction_get.CODE.STRICT', 'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_v) metadata_v) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_v) = $ptascii("v")',
        '$source_line(metadata_expression) = 6',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((6,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (6)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 6]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_v])',
        'ppropertyslot_v.STATE = ' + ('PROP_INITIAL' if form == 'omitted' else 'PROP_VALUE (DIRECT PNULL)'),
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)', 'S_return.COMPLETION = NORMAL',
        '$reference_return_source(S_return,6)', '$reference_return_fetch_valid(S_return,6)', '~$reference_verifies(S_return)',
        '$property_current_line($hold_task_inputs(S_return)) = 6', 'S_return.OBJECTPROPS = S_front.OBJECTPROPS',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = eps]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,6)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 6)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,6)', '$property_current_line(S_noarrow) = 0',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)', 'S_fetch.COMPLETION = NORMAL',
        'S_fetch.RESULT = REFERENCE n_v', 'S_fetch.STORE[n_v] = DEFINED PNULL',
        '$propref_at(S_fetch.PROPREFS,n_v) = (ppropref_v)',
        'ppropref_v.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc_v.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_v) = 2',
        'S_copy = $srgh_seek(S_fetch,8,n_root,30000)', '$srgh_phase(S_copy,8,n_root)', 'S_copy.COMPLETION = NORMAL',
        '$lookup(S_copy.ENV,$ptascii("a305")) = eps', '$lookup(S_copy.ENV,$ptascii("b305")) = eps',
        '$lookup(S_copy.ENV,$ptascii("copy305")) = (n_copy)', 'n_copy =/= n_v', 'S_copy.STORE[n_copy] = DEFINED (PBOOL false)',
        '$propref_at(S_copy.PROPREFS,n_copy) = eps', '$propref_at(S_copy.PROPREFS,n_v) = (ppropref_v)',
        'S_copy.STORE[n_v] = DEFINED PNULL', '$heap_owners($heap_graph(S_copy),HCELL n_v) = 1',
        'S_aliases = $srgh_seek(S_copy,11,18,30000)', '$srgh_phase(S_aliases,11,18)',
        '$lookup(S_aliases.ENV,$ptascii("a305")) = (n_v)', '$lookup(S_aliases.ENV,$ptascii("b305")) = (n_v)',
        'S_aliases.STORE[n_v] = DEFINED PNULL', 'S_aliases.STORE[n_copy] = DEFINED (PBOOL false)',
        '$heap_owners($heap_graph(S_aliases),HCELL n_v) = 3',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
        '~$property_hook_reference_decl(S_front,ppropertydesc_v[.TYPE = [(PTBRANCH ([PTBUILTIN "null"]))]])',
        '~$property_hook_reference_decl(S_front,ppropertydesc_v[.KEY = $ptascii("other")])',
    ]
    if form == 'omitted':
        checks += ['phpType5 = ABSENT']
    current = 'S_aliases'
    states = ['S_front', 'S_return', 'S_fetch', 'S_copy', 'S_aliases']
    for label, line, value in [('false', 20, 'PBOOL false'), ('true', 22, 'PBOOL true'),
                               ('integer', 24, 'PINT 0'), ('string', 26, 'pvalue_string'),
                               ('float', 28, 'PFLOAT 4609434218613702656'), ('null', 30, 'PNULL')]:
        state = 'S_' + label
        checks += [f'{state} = $srgh_seek({current},11,{line},30000)', f'$srgh_phase({state},11,{line})',
                   f'{state}.STORE[n_v] = DEFINED ({value})', f'$heap_owners($heap_graph({state}),HCELL n_v) = 3']
        current = state
        states += [state]
    checks += [
        '$string_bytes(pvalue_string) = ($ptascii("0"))',
        'S_array = $srgh_seek(S_null,11,34,30000)', '$srgh_phase(S_array,11,34)',
        'S_array.STORE[n_v] = DEFINED (PARRAY n_live_array)',
        '$lookup(S_array.ENV,$ptascii("arraycopy305")) = (n_arraycopy)',
        'S_array.STORE[n_arraycopy] = DEFINED (PARRAY n_copy_array)', 'n_live_array =/= n_copy_array',
        'S_array.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        'S_array.ARRAYS[n_copy_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$propref_at(S_array.PROPREFS,n_arraycopy) = eps',
        'S_object = $srgh_seek(S_array,11,38,30000)', '$srgh_phase(S_object,11,38)',
        'S_object.STORE[n_v] = DEFINED (POBJECT n_child)', 'S_object.OBJECTS[n_child] = STDINSTANCE',
        '$lookup(S_object.ENV,$ptascii("objectcopy305")) = (n_objectcopy)',
        'S_object.STORE[n_objectcopy] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_object.OBJECTPROPS,n_child) = ([ppropertyslot_child])',
        'ppropertyslot_child.NAME = $ptascii("value")', 'ppropertyslot_child.STATE = PROP_VALUE (DIRECT (PINT 3))',
        '$heap_owners($heap_graph(S_object),HOBJECT n_child) = 2', '$propref_at(S_object.PROPREFS,n_objectcopy) = eps',
        'S_before = $srgh_seek(S_object,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_v] = DEFINED (PINT 37)', '$heap_owners($heap_graph(S_before),HCELL n_v) = 3',
        '$heap_owners($heap_graph(S_before),HOBJECT n_child) = 1',
        'S_detached = $srgh_seek(S_before,11,41,30000)', '$srgh_phase(S_detached,11,41)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_v) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_v) = 2', 'S_detached.STORE[n_v] = DEFINED (PINT 37)',
        'S_written = $srgh_seek(S_detached,9,n_root,30000)', '$srgh_phase(S_written,9,n_root)',
        'S_written.STORE[n_v] = DEFINED pvalue_tail', '$string_bytes(pvalue_tail) = ($ptascii("tail"))',
        'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
        'S_written.STORE[n_arraycopy] = DEFINED (PARRAY n_copy_array)',
        'S_written.STORE[n_objectcopy] = DEFINED (POBJECT n_child)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '(HARRAY n_copy_array) <- $pools_nodes(S_end.POOLS)', '(HARRAY n_copy_array) <- S_end.ALLOCATIONS',
        'S_end.POOLS = S_before.POOLS',
    ]
    for node in ('HCELL n_v', 'HCELL n_copy', 'HCELL n_arraycopy', 'HCELL n_objectcopy', 'HARRAY n_live_array', 'HOBJECT n_child'):
        checks += ['~((' + node + ') <- S_end.ALLOCATIONS)']
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
               '$hook_short_reference_header(NNullableType (NIdentifier (BYTES ' + peer.quoted('false') + ') eps) eps,[(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "null"]))])']
    for state in [*states, 'S_array', 'S_object', 'S_before']:
        checks += ['$propref_at(' + state + '.PROPREFS,n_v) = (ppropref_v)'] if state not in ('S_front', 'S_return') else []
    for state in [*states, 'S_array', 'S_object', 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
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
    source = SOURCES/(args.form + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(peer.__file__), source, SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT/'.tools/php-file.so'),
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
        (out/'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out/'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
