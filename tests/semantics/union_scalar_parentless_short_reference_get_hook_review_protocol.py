#!/usr/bin/env python3
"""Check four ordered nullable headers, strict aliases, copies and quiet detach."""
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
SOURCES = Path(__file__).with_name('union_scalar_parentless_short_reference_get_hook_review')
PREFIX = peer.PREFIX.replace('$ptascii("root292")', '$ptascii("box301peer")')
PREFIX = PREFIX.replace('-- if ~$srgh_phase(S,n_stage,n_object) /\\ $(n > 0)',
                        '-- if ~$srgh_phase(S,n_stage,n_object) /\\ $(n > 0) /\\ S.TODO =/= eps')
PREFIX = PREFIX.replace('def $srgh_phase(S,n_stage,n) = false -- otherwise', r'''def $srgh_phase(S,13,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarString (BYTES text_value) metadata_value) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("i301peer") /\ $base64(text_value) = $ptascii("bad")
def $srgh_phase(S,14,n) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarString (BYTES text_value) metadata_value) metadata_assign)) :: ptask*
  -- if $base64(text_name) = $ptascii("aliasi301peer") /\ $base64(text_value) = $ptascii("free-int")
def $srgh_phase(S,15,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("i301peer")
def $srgh_phase(S,n_stage,n) = false -- otherwise''')


def fields(fixture, source, form):
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box301peer")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_i,ppropertydesc_f,ppropertydesc_b,ppropertydesc_s]',
    ]
    for line, (name, kind) in enumerate((('i', 'int'), ('f', 'float'), ('b', 'bool'), ('s', 'string')), 4):
        order = [kind, 'null'] if form == 'scalar-null' else ['null', kind]
        normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + item + '"]))' for item in order) + ']'
        desc = 'ppropertydesc_' + name
        checks += [
            desc + '.NAME = $ptascii("' + name + '")', desc + '.TYPE = ' + normalized,
            '$property_hook_reference_decl(S_front,' + desc + ')',
            desc + '.ORIGIN = PORIGIN n_source pcpath_' + name,
            'pcpath_group_' + name + ' = pcpath_' + name + '[0:$nabs($( |pcpath_' + name + '| - 2))]',
            'pcpath_' + name + ' = pcpath_group_' + name + ' ++ [PCFIELD 3,PCINDEX 0]',
            '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group_' + name + ') = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_' + name + ' (SEQUENCE ([NPropertyItem phpType40_' + name + ' ABSENT metadata_item_' + name + '])) (SEQUENCE ([phpType38_' + name + '])) metadata_group_' + name + ')',
            'phpType18_' + name + ' = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first_' + name + ') metadata_first_' + name + ',NIdentifier (BYTES text_second_' + name + ') metadata_second_' + name + '])) metadata_union_' + name,
            '$base64(text_first_' + name + ') = $ptascii("' + order[0] + '")',
            '$base64(text_second_' + name + ') = $ptascii("' + order[1] + '")',
            '$hook_short_reference_header(phpType18_' + name + ',' + desc + '.TYPE)',
            desc + '.TYPE = [ptbranch_first_' + name + ',ptbranch_second_' + name + ']',
            '~$hook_short_reference_header(phpType18_' + name + ',[ptbranch_second_' + name + ',ptbranch_first_' + name + '])',
            '~$property_hook_reference_decl(S_front,' + desc + '[.TYPE = [ptbranch_second_' + name + ',ptbranch_first_' + name + ']])',
            '$pttypename(' + desc + '.TYPE) = $ptascii("?' + kind + '")',
            '$property_hook_origin(S_front,' + desc + ') = (porigin_hook_' + name + ')',
            '$function_at($all_functions(S_front),porigin_hook_' + name + ') = (pfunction_' + name + ')',
            'pfunction_' + name + '.SIGNATURE = {PARAMETERS eps, RETURNS ' + desc + '.TYPE, BYREF true}',
            'pfunction_' + name + '.CODE.STRICT',
            'phpType38_' + name + ' = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_' + name + ' (SEQUENCE eps) expression_' + name + ' metadata_hook_' + name,
            '$hook_parameter_facts(metadata_hook_' + name + ') = [false]',
            'expression_' + name + ' = NExprPropertyFetch (NExprVariable (BYTES text_this_' + name + ') metadata_this_' + name + ') (NScalarString (BYTES text_field_' + name + ') metadata_field_' + name + ') metadata_expression_' + name,
            '$base64(text_this_' + name + ') = $ptascii("this")', '$base64(text_field_' + name + ') = $ptascii("' + name + '")',
            '$source_line(metadata_hook_' + name + ') = ' + str(line),
            '$code_expression(pfunction_' + name + '.CODE.EXPRESSIONS,pfunction_' + name + '.BODY) = ((' + str(line) + ',false))',
            '$arrow_line(pfunction_' + name + '.CODE.EXPRESSIONS,pfunction_' + name + '.BODY) = (' + str(line) + ')',
        ]
    checks += [
        'ppropertyhook.PROPERTY = ppropertydesc_i.ORIGIN', 'ppropertyhook.HOOK = porigin_hook_i',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_i)',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        '$reference_return_source(S_return,4)', '$reference_return_fetch_valid(S_return,4)', '$reference_verifies(S_return)',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_i[.SIGNATURE.RETURNS = [ptbranch_second_i,ptbranch_first_i]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,4)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 4)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_i[.CODE.EXPRESSIONS = $srgh_noarrow(pfunction_i.CODE.EXPRESSIONS,pfunction_i.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,4)', '$property_current_line(S_noarrow) = 0',
        'S_copies = $srgh_seek(S_return,13,n_root,30000)', '$srgh_phase(S_copies,13,n_root)', 'S_copies.COMPLETION = NORMAL',
        '$lookup(S_copies.ENV,$ptascii("aliasi301peer")) = (n_i)',
        '$lookup(S_copies.ENV,$ptascii("i301peer")) = (n_i)',
        '$lookup(S_copies.ENV,$ptascii("f301peer")) = (n_f)',
        '$lookup(S_copies.ENV,$ptascii("b301peer")) = (n_b)',
        '$lookup(S_copies.ENV,$ptascii("s301peer")) = (n_s)',
        'S_before = $srgh_seek(S_copies,0,n_root,30000)', '$srgh_phase(S_before,0,n_root)', 'S_before.COMPLETION = NORMAL',
        'S_unset_one = $drive_steps(S_before,1)', 'S_unset_one.COMPLETION = BUDGET',
        'S_detached = $srgh_seek(S_unset_one,14,n_root,30000)', '$srgh_phase(S_detached,14,n_root)', 'S_detached.COMPLETION = NORMAL',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
        'S_untyped = $srgh_seek(S_detached,15,n_root,30000)', '$srgh_phase(S_untyped,15,n_root)', 'S_untyped.COMPLETION = NORMAL',
        'S_untyped.STORE[n_i] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("free-int")))',
        'S_untyped.STORE[n_f] = DEFINED (PARRAY n_released)', 'S_untyped.STORE[n_b] = DEFINED (PINT 67)',
        'S_untyped.STORE[n_s] = DEFINED (PBOOL false)',
        'S_end = $drive_steps(S_untyped,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$srgh_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '$call_descriptors_valid(S_end)', '$property_state_valid(S_end)', '$heap_valid($heap_prune($heap_graph(S_end)))',
    ]
    copy_values = {'i': 'PINT 17', 'f': 'PFLOAT $float_of_int(19)', 'b': 'PBOOL true', 's': 'PSTRING_CARRIER INTERNED_STRING ($ptascii("kept"))'}
    current_values = {'i': 'PINT 23', 'f': 'PFLOAT $float_of_int(29)', 'b': 'PBOOL false', 's': 'PSTRING_CARRIER INTERNED_STRING ($ptascii("changed"))'}
    reset_values = {'i': 'PINT 37', 'f': 'PFLOAT $float_of_int(41)', 'b': 'PBOOL true', 's': 'PSTRING_CARRIER INTERNED_STRING ($ptascii("live"))'}
    for name in ('i', 'f', 'b', 's'):
        checks += [
            'S_copies.STORE[n_' + name + '] = DEFINED (' + current_values[name] + ')',
            '$lookup(S_copies.ENV,$ptascii("copy' + name + '301peer")) = (n_copy_' + name + ')',
            'S_copies.STORE[n_copy_' + name + '] = DEFINED (' + copy_values[name] + ')',
            '$propref_at(S_copies.PROPREFS,n_copy_' + name + ') = eps',
            '$propref_at(S_copies.PROPREFS,n_' + name + ') = (ppropref_' + name + ')',
            'ppropref_' + name + '.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("' + name + '")) ppropertydesc_' + name + '.ORIGIN]',
            '$heap_owners($heap_graph(S_copies),HCELL n_' + name + ') = ' + ('3' if name == 'i' else '2'),
            'S_before.STORE[n_' + name + '] = DEFINED (' + reset_values[name] + ')',
            '$propref_at(S_before.PROPREFS,n_' + name + ') = (ppropref_' + name + ')',
            'S_detached.STORE[n_' + name + '] = DEFINED (' + reset_values[name] + ')',
            '$propref_at(S_detached.PROPREFS,n_' + name + ') = eps',
            '$heap_owners($heap_graph(S_detached),HCELL n_' + name + ') = ' + ('2' if name == 'i' else '1'),
            '~((HCELL n_' + name + ') <- S_end.ALLOCATIONS)', '~((HCELL n_copy_' + name + ') <- S_end.ALLOCATIONS)',
        ]
    checks += [
        'S_missing = S_copies[.PROPREFS = $propref_detach(S_copies.PROPREFS,n_f,OBJECT_PROP_SOURCE n_root ($ptascii("f")) ppropertydesc_f.ORIGIN)]',
        '~$property_state_valid(S_missing)', '$property_state_valid(S_copies)', '$call_descriptors_valid(S_copies)',
        '$property_state_valid(S_detached)', '$call_descriptors_valid(S_detached)',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "ZmFsc2U=") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "bWl4ZWQ=") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTBUILTIN "mixed"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NName (BYTES "TGVhZjMwMQ==") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTCLASS ($ptascii("Leaf301"))])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps,NIdentifier (BYTES "c3RyaW5n") eps])) eps,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))])',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") eps,NIdentifier (BYTES "bnVsbA==") eps,NIdentifier (BYTES "c3RyaW5n") eps])) eps,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "string"]))])',
    ]
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['scalar-null', 'null-scalar'])
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
