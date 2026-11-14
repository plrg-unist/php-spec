#!/usr/bin/env python3
"""Check typed short Get source receipts, real type sources and receiver detach."""
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
SOURCES = Path(__file__).with_name('typed_parentless_short_reference_get_hook')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box296")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("i296")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, nullable):
    namespace = 'Ns296' + ('Nullable' if nullable else 'Scalar') + 'ShortReference'
    type_int = '[(PTBRANCH ([PTBUILTIN "int"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
    initial = 'PNULL' if nullable else 'PINT 17'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)',
        'S_front.COMPLETION = NORMAL', '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box296")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = $base64(' + peer.quoted(namespace + '\\Box296') + ')',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_i,ppropertydesc_f,ppropertydesc_b,ppropertydesc_s]',
        'ppropertydesc_i.TYPE = ' + type_int,
        '$property_hook_origin(S_front,ppropertydesc_i) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_i.TYPE, BYREF true}',
        'ppropertydesc_i.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook',
        'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]', 'pfunction_get.CODE.UNIT = n_source',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_i) metadata_i) phpType5 metadata_item])) (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) (NIdentifier (BYTES text_get) metadata_get) (SEQUENCE eps) expression_get metadata_hook])) metadata_group)',
        '$base64(text_i) = $ptascii("i")', '$hook_short_reference_header(phpType18,ppropertydesc_i.TYPE)',
        '$hook_parameter_facts(metadata_hook) = [false]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$property_hook_reference_expression_return(S_front,ppropertyhook.HOOK,6) = (expression_get)',
        '$property_hook_expression_return(S_front,ppropertyhook.HOOK,6) = eps',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((6,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (6)',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 6]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_i,ppropertyslot_f,ppropertyslot_b,ppropertyslot_s])',
        'ppropertyslot_i.STATE = ' + ('PROP_INITIAL' if nullable else 'PROP_VALUE (DIRECT (PINT 17))'),
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
        'S_return.ORIGIN = (ppropertyhook.HOOK)', 'S_return.TODO = (RETURN_REF_FETCH 6) :: ptask_return*',
        '$reference_return_source(S_return,6)', '$reference_return_fetch_valid(S_return,6)',
        '$property_current_line(S_return) = 6',
        '$property_current_line($hold_task_inputs(S_return)) = 6',
        '~$reference_return_value_valid(S_return,6)', '$reference_verifies(S_return)',
        '$property_hook_backing(S_return,n_root,ppropertydesc_i)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_root) = 3',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
        'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_i',
        'S_fetch.STORE[n_i] = DEFINED (' + initial + ')',
        '$heap_owners($heap_graph(S_fetch),HCELL n_i) = 2',
        '$propref_at(S_fetch.PROPREFS,n_i) = (ppropref_i)',
        'ppropref_i.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("i")) ppropertydesc_i.ORIGIN]',
        '$call_reference_operand_valid(S_fetch,S_fetch.RESULT)', '$call_descriptors_valid(S_fetch)',
        '$property_state_valid(S_fetch)', '$heap_valid($heap_prune($heap_graph(S_fetch)))',
        'S_before = $srgh_seek(S_fetch,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)',
        'S_before.COMPLETION = NORMAL', '$lookup(S_before.ENV,$ptascii("i296")) = (n_i)',
        '$propref_at(S_before.PROPREFS,n_i) = (ppropref_i)',
        'S_detached = $srgh_seek(S_before,8,n_root,30000)', '$srgh_phase(S_detached,8,n_root)',
        'S_detached.COMPLETION = NORMAL', '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
        '$lookup(S_detached.ENV,$ptascii("i296")) = (n_i)', '$propref_at(S_detached.PROPREFS,n_i) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_i) = 1',
        '$call_descriptors_valid(S_detached)', '$property_state_valid(S_detached)',
        '$heap_valid($heap_prune($heap_graph(S_detached)))',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + ('P|U|V|N|W|C|D|R|Z|' if nullable else 'G|W|I|F|B|S|K|D|R|Z|') + '")',
        '~((HCELL n_i) <- S_end.ALLOCATIONS)',
        '~$property_hook_reference_decl(S_front,ppropertydesc_i[.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]])',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_get[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]]) :: S_return.FUNCTIONS]',
        '$property_hook_reference_expression_return(S_wrongreturn,ppropertyhook.HOOK,6) = eps',
        '$property_current_line(S_wrongreturn) = 0',
        '~$reference_return_source(S_wrongreturn,6)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 6)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_get[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]) :: S_return.FUNCTIONS]',
        '$property_hook_reference_expression_return(S_noarrow,ppropertyhook.HOOK,6) = eps',
        '$property_current_line(S_noarrow) = 0',
        '~$reference_return_source(S_noarrow,6)',
    ]
    for name, kind in (('i', 'int'), ('f', 'float'), ('b', 'bool'), ('s', 'string')):
        normalized = '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
        checks += [f'ppropertydesc_{name}.TYPE = {normalized}',
                   f'$property_hook_reference_decl(S_front,ppropertydesc_{name})']
    for name, state in (('return', 'S_return'), ('fetch', 'S_fetch'), ('detach', 'S_before')):
        checks += [f'S_{name}_zero = $drive_steps({state},0)', f'S_{name}_zero.COMPLETION = BUDGET',
                   f'S_{name}_zero[.COMPLETION = NORMAL] = {state}',
                   f'S_{name}_one = $drive_steps(S_{name}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{name}_one.COMPLETION = BUDGET',
                   f'S_{name}_resumed = S_{name}_one[.COMPLETION = NORMAL]',
                   f'S_{name}_joined = $drive_steps(S_{name}_resumed,30000)',
                   f'S_{name}_direct = $drive_steps({state},30001)',
                   f'S_{name}_joined = S_{name}_direct']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['scalar', 'nullable'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / (args.form + '-aliases.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), source, *modules, *(ROOT / p for p in (
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
        checks = fields(checked['fixture'], source, args.form == 'nullable')
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
