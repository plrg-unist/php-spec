#!/usr/bin/env python3
"""Check short reference Hook execution, real markers, copies and cell retirement."""
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
SOURCES = Path(__file__).with_name('parentless_short_reference_get_hook')
sha = peer.sha
quoted = peer.quoted
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box292")')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,8,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("copy292")
def $srgh_phase(S,9,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias292")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form, body='identifier'):
    initial = 'PINT 17' if form == 'initialized' else 'PNULL'
    namespace = 'Ns292ShortReference' + form.title() + chr(92)
    name_node = 'NScalarString' if body == 'literal' else 'NIdentifier'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)',
        'S_front.COMPLETION = NORMAL', '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box292")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'ppropertyhook.LINE = 24', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = $base64(' + quoted(namespace + 'Box292') + ')',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_tag,ppropertydesc_tail]',
        '$property_effective_desc(S_front,n_root,$ptascii("tag")) = (ppropertydesc_tag)',
        '$property_hook_reference_decl(S_front,ppropertydesc_tag)',
        '$property_hook_origin(S_front,ppropertydesc_tag) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF true}',
        'pfunction_get.NAME = pclassdesc_root.NAME ++ $ptascii("::$tag::get")',
        'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY',
        'pfunction_get.LINE = 15', 'pfunction_get.ENDLINE = 16',
        'ppropertydesc_tag.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook',
        'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.ORIGIN = ppropertyhook.HOOK', 'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]',
        'pfunction_get.CODE.UNIT = n_source',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_tag) metadata_tag) phpType5_default metadata_item])) (SEQUENCE ([phpType38_get])) metadata_group)',
        '$base64(text_tag) = $ptascii("tag")',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) expression_get metadata_get',
        '$hook_parameter_facts(metadata_get) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (' + name_node + ' (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("tag")',
        '$hook_short_reference_body(expression_get,$ptascii("tag"))',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$source_line(metadata_get) = 15', '$source_line(metadata_expression) = 16',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((16,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (16)',
        '$property_hook_reference_expression_return(S_front,ppropertyhook.HOOK,16) = (expression_get)',
        '$property_hook_expression_return(S_front,ppropertyhook.HOOK,16) = eps',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 16]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initialmiddle,ppropertyslot_initialtag,ppropertyslot_initialtail])',
        'ppropertyslot_initialtag.STATE = PROP_VALUE (DIRECT (' + initial + '))',
        '$srgh_output(S_front.EVENTS) = $ptascii("N|")',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.COMPLETION = NORMAL', 'S_return.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
        'pcallcontext_get.FUNCTION = ppropertyhook.HOOK', 'S_return.ORIGIN = (ppropertyhook.HOOK)',
        'S_return.TODO = (RETURN_REF_FETCH 16) :: ptask_return*',
        'S_return.BASE = BASE_PROPERTY_PENDING (BASE_VALUE (KNOWN (POBJECT n_root))) (KNOWN (PSTRING ($ptascii("tag")))) 16',
        'S_resolved = $property_pending_resolve(S_return,BASE_VALUE (KNOWN (POBJECT n_root)),KNOWN (PSTRING ($ptascii("tag"))),PPW,16,16)',
        'S_resolved.COMPLETION = NORMAL', 'S_resolved.BASE = BASE_PROPERTY (POBJECT n_root) ($ptascii("tag"))',
        '$reference_returning(S_return)', '$reference_return_source(S_return,16)',
        '$reference_return_fetch_valid(S_return,16)', '~$reference_return_value_valid(S_return,16)',
        '$arrow_return(S_return,16) = eps',
        '$property_hook_backing(S_return,n_root,ppropertydesc_tag)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_root) = 3',
        '$base_nodes(S_return.BASE) = [HOBJECT n_root]',
        '$call_context_roots(S_return.CURRENT) = [HOBJECT n_root]',
        '$node_children(S_return,HCELL n_rootcell) = [HOBJECT n_root]',
        '$call_descriptors_valid(S_return)', '$property_state_valid(S_return)',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
        'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_tagcell',
        'S_fetch.STORE[n_tagcell] = DEFINED (' + initial + ')',
        '$heap_owners($heap_graph(S_fetch),HCELL n_tagcell) = 2',
        '$heap_owners($heap_graph(S_fetch),HOBJECT n_root) = 1',
        '$propref_at(S_fetch.PROPREFS,n_tagcell) = eps',
        '$call_reference_operand_valid(S_fetch,S_fetch.RESULT)',
        '$property_hook_result_tail(S_fetch,ppropertyhook,S_fetch.TODO)',
        '$srgh_output(S_fetch.EVENTS) = $ptascii("N|")',
        'S_copy = $srgh_seek(S_fetch,8,n_root,30000)', '$srgh_phase(S_copy,8,n_root)',
        'S_copy.CURRENT = eps', 'S_copy.FRAMES = eps', 'S_copy.HELD = eps',
        '$srgh_output(S_copy.EVENTS) = $ptascii("N|G|B|")',
        '$lookup(S_copy.ENV,$ptascii("copy292")) = (n_copy)',
        '$lookup(S_copy.ENV,$ptascii("alias292")) = (n_tagcell)',
        'n_copy =/= n_tagcell', 'S_copy.STORE[n_copy] = DEFINED (POBJECT n_leaf)',
        'S_copy.STORE[n_tagcell] = DEFINED (POBJECT n_leaf)',
        '$heap_owners($heap_graph(S_copy),HCELL n_tagcell) = 2',
        '$heap_owners($heap_graph(S_copy),HOBJECT n_leaf) = 2',
        'S_alias = $srgh_seek(S_copy,9,n_root,30000)', '$srgh_phase(S_alias,9,n_root)',
        '$lookup(S_alias.ENV,$ptascii("copy292")) = eps',
        '$lookup(S_alias.ENV,$ptascii("alias292")) = (n_tagcell)',
        '$heap_owners($heap_graph(S_alias),HCELL n_tagcell) = 2',
        '$heap_owners($heap_graph(S_alias),HOBJECT n_leaf) = 1',
        'S_raw = $srgh_seek(S_alias,0,n_root,30000)', '$srgh_phase(S_raw,0,n_root)',
        'S_raw.COMPLETION = NORMAL', 'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$lookup(S_raw.ENV,$ptascii("alias292")) = eps',
        '$objectprops_at(S_raw.OBJECTPROPS,n_root) = ([ppropertyslot_middle,ppropertyslot_tag,ppropertyslot_tail])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tag.STATE = PROP_VALUE (ALIAS n_tagcell)',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
        'S_raw.STORE[n_tagcell] = DEFINED (POBJECT n_leaf)',
        '$propref_at(S_raw.PROPREFS,n_tagcell) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_tagcell) = 1',
        '$node_children(S_raw,HCELL n_tagcell) = [HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HCELL n_tagcell,HOBJECT n_tail]',
        '$call_descriptors_valid(S_raw)', '$property_state_valid(S_raw)', '$heap_valid($heap_prune($heap_graph(S_raw)))',
        'S_storage = $srgh_seek(S_raw,1,n_root,30000)', '$srgh_phase(S_storage,1,n_root)',
        '$instance_storage_for(S_storage,n_root) = (pinstancestorage)', '$instance_storage_valid(S_storage,pinstancestorage)',
        'S_middle = $srgh_seek(S_storage,2,n_root,30000)', '$srgh_phase(S_middle,2,n_root)',
        '$srgh_output(S_middle.EVENTS) = $ptascii("N|G|B|M|")',
        '$node_children(S_middle,HOBJECT n_root) = [HCELL n_tagcell,HOBJECT n_tail]',
        '~((HOBJECT n_middle) <- S_middle.ALLOCATIONS)',
        'S_tag = $srgh_seek(S_middle,3,n_root,30000)', '$srgh_phase(S_tag,3,n_root)',
        '$srgh_output(S_tag.EVENTS) = $ptascii("N|G|B|M|U|")',
        '~((HCELL n_tagcell) <- S_tag.ALLOCATIONS)', '~((HOBJECT n_leaf) <- S_tag.ALLOCATIONS)',
        '$node_children(S_tag,HOBJECT n_root) = [HOBJECT n_tail]',
        '~(n_tail <- S_tag.DESTRUCTION.CALLED)',
        'S_done = $drive(S_tag,30000)', 'S_done.COMPLETION = NORMAL',
        '$srgh_output(S_done.EVENTS) = $ptascii("N|G|B|M|U|T|Z|")',
        '~((HOBJECT n_root) <- S_done.ALLOCATIONS)', '~((HOBJECT n_tail) <- S_done.ALLOCATIONS)',
        'S_done.DESTRUCTION.OPERATIONS = eps', '$call_descriptors_valid(S_done)', '$property_state_valid(S_done)',
        '$heap_valid($heap_prune($heap_graph(S_done)))',
        '~$reference_return_source(S_return,15)', '~$reference_return_fetch_valid(S_return,15)',
        'S_no_current = S_return[.CURRENT = eps]', '~$reference_return_source(S_no_current,16)',
        '~$reference_arrow_boundary(S_return,ppropertyhook.HOOK,15)',
        '~$reference_arrow_boundary(S_no_current,ppropertyhook.HOOK,16)',
    ]
    for label, state in [('return','S_return'),('fetch','S_fetch'),('cleanup','S_middle')]:
        checks += [
            f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
            f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
        ]
        if label == 'return':
            checks += [
                'S_return_resume = S_return_one[.COMPLETION = NORMAL]',
                '(RETURN_REF_UNWIND (REFERENCE n_tagcell) 16 false ppropertyhook.HOOK) <- S_return_resume.TODO',
                '$reference_arrow_boundary(S_return_resume,ppropertyhook.HOOK,16)',
                '$arrow_context(S_return_resume)',
                '~$reference_return_null_valid(S_return_resume,16)',
                '~$reference_return_notice(S_return_resume,REFERENCE n_tagcell)',
                '$reference_notice_count(S_return_resume.TODO) = 0',
                '$reference_notice_presence(S_return_resume)',
                '$reference_return_result_valid(S_return_resume)',
                '~$goto_scope_valid(S_return_resume,ppropertyhook.HOOK)',
                '$call_task_valid(S_return_resume,RETURN_REF_UNWIND (REFERENCE n_tagcell) 16 false ppropertyhook.HOOK)',
                '~$call_task_valid(S_return_resume,RETURN_REF_UNWIND (REFERENCE n_tagcell) 16 true ppropertyhook.HOOK)',
                '$call_entry_check(S_return_resume) = S_return_resume',
            ]
        checks += [
            f'$drive(S_{label}_zero[.COMPLETION = NORMAL],30000) = S_done',
            f'$drive(S_{label}_one[.COMPLETION = NORMAL],30000) = S_done',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['initialized', 'null'])
    parser.add_argument('--body', choices=['identifier', 'literal'], default='identifier')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    sources = SOURCES if args.body == 'identifier' else SOURCES.with_name('parentless_literal_short_reference_get_hook')
    source = sources / ('short-reference-' + args.form + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form, 'body': args.body,
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
        checks = fields(checked['fixture'], source, args.form, args.body); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
