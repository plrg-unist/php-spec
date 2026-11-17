#!/usr/bin/env python3
"""Check ordered scalar unions, failed initialization, weak coercion and detach."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import mixed_parentless_short_reference_get_hook_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('int_string_parentless_short_reference_get_hook')
PREFIX = prior.PREFIX.replace('305', '306')


def fields(fixture, source, form):
    omitted = form == 'string-int'
    first, second = form.split('-')
    mask = '[(PTBRANCH ([PTBUILTIN "' + first + '"])),(PTBRANCH ([PTBUILTIN "' + second + '"]))]'
    reversed_mask = '[(PTBRANCH ([PTBUILTIN "' + second + '"])),(PTBRANCH ([PTBUILTIN "' + first + '"]))]'
    lines = source.read_text().splitlines()
    line = lambda statement: lines.index(statement) + 1
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box306")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_v]', 'ppropertydesc_v.TYPE = ' + mask,
        'ppropertydesc_v.NAME = $ptascii("v")', 'ppropertydesc_v.KEY = ppropertydesc_v.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc_v)',
        'ppropertydesc_v.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second])) metadata_union',
        '$base64(text_first) = $ptascii("' + first + '")', '$base64(text_second) = $ptascii("' + second + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc_v.TYPE)', '$pttypename(ppropertydesc_v.TYPE) = $ptascii("string|int")',
        '~$hook_short_reference_header(phpType18,' + reversed_mask + ')',
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
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_INITIAL' if omitted else 'PROP_VALUE (DIRECT (PINT 0))'),
        '$lookup(S_front.ENV,$ptascii("copy306")) = (n_copy)',
        'S_front.STORE[n_copy] = DEFINED pvalue_saved', '$string_bytes(pvalue_saved) = ($ptascii("saved"))',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)', 'S_return.COMPLETION = NORMAL',
        '$reference_return_source(S_return,6)', '$reference_return_fetch_valid(S_return,6)', '$reference_verifies(S_return)',
        '$property_current_line($hold_task_inputs(S_return)) = 6',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = ' + reversed_mask + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,6)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 6)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,6)', '$property_current_line(S_noarrow) = 0',
    ]
    states = ['S_front', 'S_return']
    if omitted:
        initialize_line = line('$box306->v = 0;')
        checks += [
            'phpType5 = ABSENT',
            f'S_failed = $srgh_seek(S_return,11,{initialize_line},30000)', f'$srgh_phase(S_failed,11,{initialize_line})',
            'S_failed.COMPLETION = NORMAL', 'S_failed.CURRENT = eps', 'S_failed.FRAMES = eps',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = ([ppropertyslot_failed])', 'ppropertyslot_failed.STATE = PROP_INITIAL',
            'S_failed.STORE[n_copy] = DEFINED pvalue_saved', 'S_failed.PROPREFS = eps',
            'S_initialized = $srgh_seek(S_failed,5,0,30000)', '$srgh_phase(S_initialized,5,0)',
            '$objectprops_at(S_initialized.OBJECTPROPS,n_root) = ([ppropertyslot_initialized])',
            'ppropertyslot_initialized.STATE = PROP_VALUE (DIRECT (PINT 0))', 'S_initialized.STORE[n_copy] = DEFINED pvalue_saved',
            'S_successreturn = $srgh_seek(S_initialized,6,n_root,30000)', '$srgh_phase(S_successreturn,6,n_root)',
            '$reference_return_source(S_successreturn,6)', '$reference_return_fetch_valid(S_successreturn,6)', '$reference_verifies(S_successreturn)',
        ]
        states += ['S_failed', 'S_initialized', 'S_successreturn']
        success = 'S_successreturn'
    else:
        checks += ['phpType5 = NScalarInt (INTEGER 0) metadata_default']
        success = 'S_return'
    checks += [
        'S_fetch = $srgh_seek(' + success + ',7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)', 'S_fetch.COMPLETION = NORMAL',
        'S_fetch.RESULT = REFERENCE n_v', 'S_fetch.STORE[n_v] = DEFINED (PINT 0)',
        '$propref_at(S_fetch.PROPREFS,n_v) = (ppropref_v)',
        'ppropref_v.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc_v.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_v) = 2',
        'S_copy = $srgh_seek(S_fetch,8,n_root,30000)', '$srgh_phase(S_copy,8,n_root)', 'S_copy.COMPLETION = NORMAL',
        '$lookup(S_copy.ENV,$ptascii("copy306")) = (n_copy)', 'n_copy =/= n_v', 'S_copy.STORE[n_copy] = DEFINED (PBOOL false)',
        '$propref_at(S_copy.PROPREFS,n_copy) = eps', '$propref_at(S_copy.PROPREFS,n_v) = (ppropref_v)',
        'S_copy.STORE[n_v] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S_copy),HCELL n_v) = 1',
        'S_aliases = $srgh_seek(S_copy,11,' + str(line("$a306 = '12';")) + ',30000)',
        '$srgh_phase(S_aliases,11,' + str(line("$a306 = '12';")) + ')',
        '$lookup(S_aliases.ENV,$ptascii("a306")) = (n_v)', '$lookup(S_aliases.ENV,$ptascii("b306")) = (n_v)',
        'S_aliases.STORE[n_v] = DEFINED (PINT 0)', '$propref_at(S_aliases.PROPREFS,n_v) = (ppropref_v)',
        '$heap_owners($heap_graph(S_aliases),HCELL n_v) = 3',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
    ]
    states += ['S_fetch', 'S_copy', 'S_aliases']
    current = 'S_aliases'
    for label, statement, value in [('string', '$b306 = 17;', 'pvalue_numeric_string'),
                                     ('integer', '$a306 = 2.0;', 'PINT 17'),
                                     ('float', '$b306 = true;', 'PINT 2'),
                                     ('true', '$a306 = false;', 'PINT 1'),
                                     ('false', 'try { $a306 = null; } catch (\\TypeError $e) {', 'PINT 0'),
                                     ('null', 'try { $b306 = []; } catch (\\TypeError $e) {', 'PINT 0'),
                                     ('array', 'try { $a306 = new \\stdClass(); } catch (\\TypeError $e) {', 'PINT 0'),
                                     ('object', '$b306 = 37;', 'PINT 0')]:
        state = 'S_' + label
        n_line = line(statement)
        checks += [f'{state} = $srgh_seek({current},11,{n_line},30000)', f'$srgh_phase({state},11,{n_line})',
                   f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_v] = DEFINED ({value})',
                   f'$propref_at({state}.PROPREFS,n_v) = (ppropref_v)', f'$heap_owners($heap_graph({state}),HCELL n_v) = 3']
        current = state
        states += [state]
    detach_line = len(lines) - 3
    checks += [
        '$string_bytes(pvalue_numeric_string) = ($ptascii("12"))', '$typed_tag(pvalue_numeric_string) = "string"',
        'S_before = $srgh_seek(S_object,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_v] = DEFINED (PINT 37)', '$propref_at(S_before.PROPREFS,n_v) = (ppropref_v)',
        '$heap_owners($heap_graph(S_before),HCELL n_v) = 3',
        f'S_detached = $srgh_seek(S_before,11,{detach_line},30000)', f'$srgh_phase(S_detached,11,{detach_line})',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_v) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_v) = 2', 'S_detached.STORE[n_v] = DEFINED (PINT 37)',
        'S_written = $srgh_seek(S_detached,9,n_root,30000)', '$srgh_phase(S_written,9,n_root)',
        'S_written.STORE[n_v] = DEFINED (PBOOL false)', 'S_written.STORE[n_copy] = DEFINED (PBOOL false)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_v) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
    ]
    for strict in ('false', 'true'):
        for value in ('PINT 0', 'pvalue_numeric_string'):
            checks += ['$propref_class(S_aliases,' + mask + ',' + value + ',' + strict + ') = PROP_EXACT']
        for value in ('PNULL',):
            checks += ['$propref_class(S_aliases,' + mask + ',' + value + ',' + strict + ') = PROP_IMPOSSIBLE']
        checks += ['$propref_class(S_aliases,' + mask + ',PARRAY 0,' + strict + ') = ' + ('PROP_POSSIBLE' if strict == 'false' else 'PROP_IMPOSSIBLE')]
        for value in ('PFLOAT 4611686018427387904', 'PBOOL false', 'PBOOL true'):
            checks += ['$propref_class(S_aliases,' + mask + ',' + value + ',' + strict + ') = ' + ('PROP_POSSIBLE' if strict == 'false' else 'PROP_IMPOSSIBLE')]
    checks += ['$propref_conversion(S_aliases,' + mask + ',PARRAY 0,false) = TYPEREJECT']
    for left, right in [('int', 'int'), ('string', 'string'), ('array', 'int'), ('mixed', 'null'), ('null', 'mixed')]:
        raw = 'NUnionType (SEQUENCE ([NIdentifier (BYTES ' + peer.quoted(left) + ') eps,NIdentifier (BYTES ' + peer.quoted(right) + ') eps])) eps'
        normalized = '[(PTBRANCH ([PTBUILTIN "' + left + '"])),(PTBRANCH ([PTBUILTIN "' + right + '"]))]'
        checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
    checks += ['$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps,NIdentifier (BYTES "c3RyaW5n") eps])) eps,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))])',
               '$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps,NIdentifier (BYTES "bnVsbA==") eps,NIdentifier (BYTES "c3RyaW5n") eps])) eps,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "string"]))])']
    for state in [*states, 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in [('return', success), ('cleanup', 'S_before')] + ([('failed', 'S_return')] if omitted else []):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['int-string', 'string-int'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES/(args.form + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(peer.__file__), source, SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
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
