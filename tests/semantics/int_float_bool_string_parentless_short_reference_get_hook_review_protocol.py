#!/usr/bin/env python3
"""Check strict four-scalar Get, exact raw order and detached NULL aliases."""
import argparse
import base64
import json
from itertools import permutations
from pathlib import Path
import subprocess

import literal_boolean_parentless_short_reference_get_hook_review_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('int_float_bool_string_parentless_short_reference_get_hook_review')
PREFIX = prior.PREFIX.replace('box302peer', 'box316peer').replace('f302peer', 'a316peer').replace('probe302peer', 'a316peer')
PREFIX = PREFIX.replace('def $lbr_phase(S,0) = ($property_hook_ref_plan(S) =/= eps)',
                        'def $lbr_phase(S,0) = ($property_hook_plan(S) =/= eps)')
PREFIX = PREFIX.replace('(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*',
                        '(PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*')


def header_fields(members_to_check):
    checks = []
    for members in members_to_check:
        current_mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in members) + ']'
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in members) + '])) eps'
        upper = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part.upper()) + ') eps' for part in members) + '])) eps'
        reversed_raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in reversed(members)) + '])) eps'
        checks += ['$hook_short_reference_header(' + raw + ',' + current_mask + ')',
                   '$hook_short_reference_header(' + upper + ',' + current_mask + ')',
                   '~$hook_short_reference_header(' + reversed_raw + ',' + current_mask + ')']
        for value in ('PINT 0', 'PINT 23', 'PINT 37', 'PFLOAT 0', 'PFLOAT 4611686018427387904', 'PBOOL true', 'PBOOL false',
                      'PSTRING ($ptascii("plain"))', 'PSTRING ($ptascii("12"))',
                      'PSTRING ($ptascii("12.5"))', 'PSTRING ($ptascii("2e0"))',
                      'PSTRING ($ptascii(""))', 'PSTRING ($ptascii("0"))',
                      'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'):
            for strict in ('false', 'true'):
                checks += ['$propref_class(S_aliases,' + current_mask + ',' + value + ',' + strict + ') = PROP_EXACT',
                           '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',' + strict + ') = TYPEVALUE (' + value + ')']
        for value in ('PNULL', 'PARRAY 0', 'POBJECT n_root'):
            classification = 'PROP_IMPOSSIBLE' if value == 'PNULL' else 'PROP_POSSIBLE'
            checks += ['$propref_class(S_aliases,' + current_mask + ',' + value + ',false) = ' + classification,
                       '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',false) = TYPEREJECT',
                       '$propref_class(S_aliases,' + current_mask + ',' + value + ',true) = PROP_IMPOSSIBLE',
                       '$propref_conversion(S_aliases,' + current_mask + ',' + value + ',true) = TYPEREJECT']
    return checks


def fields(fixture, source, form, headers_only=False, failed_join_only=False):
    omitted = form == 'string-bool-float-int'
    first, second, third, fourth = form.split('-')
    mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in (first, second, third, fourth)) + ']'
    reversed_mask = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in (fourth, third, second, first)) + ']'
    lines = source.read_text().splitlines()
    line = lambda statement: lines.index(statement) + 1
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_plan(S_front) = (ppropertyhook)', '$property_hook_ref_plan(S_front) = eps',
        '$lookup(S_front.ENV,$ptascii("box316peer")) = (n_rootcell)', 'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.KIND = "class"',
        'pclassdesc_root.PARENT = eps', '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + mask,
        'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        '$property_hook_reference_decl(S_front,ppropertydesc)', 'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_third) metadata_third,NIdentifier (BYTES text_fourth) metadata_fourth])) metadata_union',
        '$base64(text_first) = $ptascii("' + first + '")', '$base64(text_second) = $ptascii("' + second + '")', '$base64(text_third) = $ptascii("' + third + '")', '$base64(text_fourth) = $ptascii("' + fourth + '")',
        '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)', '$pttypename(ppropertydesc.TYPE) = $ptascii("string|int|float|bool")',
        '~$hook_short_reference_header(phpType18,' + reversed_mask + ')', '~$hook_short_reference_header(phpType18,eps)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_mask + '])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'pfunction.CODE.STRICT', 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = 6', '$source_line(metadata_expression) = 7',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((7,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (7)',
        '$function_body_tasks(S_front,pfunction) = [$at_task((PORIGIN n_source pfunction.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 7]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = ' + ('PROP_INITIAL' if omitted else 'PROP_VALUE (DIRECT (PINT 0))'),
        '$lookup(S_front.ENV,$ptascii("copy316peer")) = (n_copy)', 'S_front.STORE[n_copy] = DEFINED pvalue_saved',
        '$string_bytes(pvalue_saved) = ($ptascii("saved"))',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 7) :: ptask_return*',
        '$reference_return_source(S_return,7)', '$reference_return_fetch_valid(S_return,7)', '$reference_verifies(S_return)',
        '$property_current_line(S_return) = 7', '$property_current_line($hold_task_inputs(S_return)) = 7',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reversed_mask + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,7)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 7)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,7)', '$property_current_line(S_noarrow) = 0',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_reversed = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_fourth) metadata_fourth,NIdentifier (BYTES text_third) metadata_third,NIdentifier (BYTES text_second) metadata_second,NIdentifier (BYTES text_first) metadata_first])) metadata_union) (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_reversed) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,7)',
    ]
    states = ['S_front', 'S_return']
    if omitted:
        initialize = line('$box316peer->v = 0;')
        checks += [
            'phpType5 = ABSENT',
            f'S_failed = $lbr_seek(S_return,{initialize},30000)', f'$lbr_phase(S_failed,{initialize})',
            'S_failed.COMPLETION = NORMAL', 'S_failed.CURRENT = eps', 'S_failed.FRAMES = eps',
            'S_failed.STORE[n_copy] = DEFINED pvalue_saved', 'S_failed.PROPREFS = eps',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = ([ppropertyslot_failed])', 'ppropertyslot_failed.STATE = PROP_INITIAL',
            '$lbr_output(S_failed.EVENTS) = $ptascii("U|E|P|")',
            'S_initialized = $lbr_seek(S_failed,0,30000)', '$lbr_phase(S_initialized,0)',
            '$objectprops_at(S_initialized.OBJECTPROPS,n_root) = ([ppropertyslot_initialized])',
            'ppropertyslot_initialized.STATE = PROP_VALUE (DIRECT (PINT 0))', 'S_initialized.STORE[n_copy] = DEFINED pvalue_saved',
            'S_successreturn = $lbr_seek(S_initialized,-1,30000)', '$lbr_phase(S_successreturn,-1)',
            '$reference_return_source(S_successreturn,7)', '$reference_return_fetch_valid(S_successreturn,7)', '$reference_verifies(S_successreturn)',
        ]
        states += ['S_failed', 'S_initialized', 'S_successreturn']
        success = 'S_successreturn'
    else:
        checks += ['phpType5 = NScalarInt (INTEGER 0) metadata_default']
        success = 'S_return'
    copy_line = line('$copy316peer = 17;')
    aliases_line = line('$a316peer = 23;')
    checks += [
        'S_fetch = $lbr_seek(' + success + ',-2,30000)', '$lbr_phase(S_fetch,-2)',
        'S_fetch.RESULT = REFERENCE n_field', 'S_fetch.STORE[n_field] = DEFINED (PINT 0)',
        '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2',
        f'S_copied = $lbr_seek(S_fetch,{copy_line},30000)', f'$lbr_phase(S_copied,{copy_line})',
        'S_copied.STORE[n_copy] = DEFINED (PINT 0)', 'n_copy =/= n_field',
        '$propref_at(S_copied.PROPREFS,n_copy) = eps', '$propref_at(S_copied.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_copied),HCELL n_field) = 1',
        f'S_aliases = $lbr_seek(S_copied,{aliases_line},30000)', f'$lbr_phase(S_aliases,{aliases_line})',
        '$lookup(S_aliases.ENV,$ptascii("a316peer")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("b316peer")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED (PINT 0)', 'S_aliases.STORE[n_copy] = DEFINED (PINT 17)',
        '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)', '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)',
    ]
    states += ['S_fetch', 'S_copied', 'S_aliases']
    if headers_only:
        return checks + header_fields(permutations(('int', 'float', 'bool', 'string')))
    current = 'S_aliases'
    steps = [('integer', '$a316peer = 2.0;', 'PINT 23'),
             ('floatwrite', '$probe_float316peer = $box316peer->v;', 'PFLOAT 4611686018427387904'),
             ('floatprobe', '$b316peer = true;', 'PFLOAT 4611686018427387904'),
             ('true', '$probe_bool316peer = $box316peer->v;', 'PBOOL true'),
             ('boolprobe', '$a316peer = false;', 'PBOOL true'),
             ('false', "$a316peer = 'plain';", 'PBOOL false'),
             ('plaintext', '$probe_string316peer = $box316peer->v;', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'),
             ('stringprobe', "$a316peer = '12';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("plain"))'),
             ('inttext', "$b316peer = '12.5';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("12"))'),
             ('floattext', "$a316peer = '2e0';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("12.5"))'),
             ('exponenttext', "$b316peer = '';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2e0"))'),
             ('emptytext', "$a316peer = '0';", 'PSTRING_CARRIER INTERNED_STRING ($ptascii(""))'),
             ('zerotext', '$b316peer = 2.0;', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
             ('float', 'try { $a316peer = null; } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('null', 'try { $b316peer = []; } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('array', 'try { $a316peer = new \\stdClass(); } catch (\\TypeError $e) {', 'PFLOAT 4611686018427387904'),
             ('object', '$b316peer = 37;', 'PFLOAT 4611686018427387904')]
    for label, statement, value in steps:
        state, n_line = 'S_' + label, line(statement)
        if label in ('floatprobe', 'boolprobe', 'stringprobe'):
            tag = label.removesuffix('probe')
            start = {'floatprobe': 'S_floatwrite', 'boolprobe': 'S_true', 'stringprobe': 'S_plaintext'}[label]
            front, returned, fetched = ('S_' + tag + suffix for suffix in ('_get_front', '_get_return', '_get_fetch'))
            hook, context = 'ppropertyhook_' + tag, 'pcallcontext_' + tag
            checks += [f'{front} = $lbr_seek({start},0,30000)', f'$lbr_phase({front},0)',
                       f'$property_hook_plan({front}) = ({hook})', f'$property_hook_ref_plan({front}) = eps',
                       f'{hook}.OBJECT = n_root', f'{hook}.HOOK = ppropertyhook.HOOK',
                       f'{front}.STORE[n_field] = DEFINED ({value})', f'$propref_at({front}.PROPREFS,n_field) = (ppropref)',
                       f'$heap_owners($heap_graph({front}),HCELL n_field) = 3',
                       f'{returned} = $lbr_seek({front},-1,30000)', f'$lbr_phase({returned},-1)',
                       f'{returned}.TODO = (RETURN_REF_FETCH 7) :: ptask_{tag}_return*', f'{returned}.CURRENT = ({context})',
                       f'{context}.TARGET = PROPERTY_HOOK_TARGET {hook}', f'{context}.FUNCTION = ppropertyhook.HOOK',
                       f'$property_hook_function({returned},{hook}) = (pfunction)',
                       f'$reference_return_source({returned},7)', f'$reference_return_fetch_valid({returned},7)',
                       f'$reference_verifies({returned})', f'$property_current_line({returned}) = 7',
                       f'{returned}.STORE[n_field] = DEFINED ({value})',
                       f'{fetched} = $lbr_seek({returned},-2,30000)', f'$lbr_phase({fetched},-2)',
                       f'{fetched}.TODO = (PROPERTY_HOOK_RESULT {hook}) :: ptask_{tag}_result*',
                       f'{fetched}.RESULT = REFERENCE n_field', f'{fetched}.STORE[n_field] = DEFINED ({value})',
                       f'$propref_at({fetched}.PROPREFS,n_field) = (ppropref)', f'$heap_owners($heap_graph({fetched}),HCELL n_field) = 4']
            states += [front, returned, fetched]
            current = fetched
        checks += [f'{state} = $lbr_seek({current},{n_line},30000)', f'$lbr_phase({state},{n_line})',
                   f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_field] = DEFINED ({value})',
                   f'{state}.STORE[n_copy] = DEFINED (PINT 17)',
                   f'$propref_at({state}.PROPREFS,n_field) = (ppropref)', f'$heap_owners($heap_graph({state}),HCELL n_field) = 3']
        current = state
        states += [state]
    checks += ['$lookup(S_floatprobe.ENV,$ptascii("probe_float316peer")) = eps',
               '$lbr_output(S_floatprobe.EVENTS) = $ptascii("' + ('U|E|P|' if omitted else 'I|') + 'V|N|J|D|F|")',
               '$lookup(S_boolprobe.ENV,$ptascii("probe_bool316peer")) = eps',
               '$lookup(S_stringprobe.ENV,$ptascii("probe_string316peer")) = eps',
               '$lbr_output(S_boolprobe.EVENTS) = $ptascii("' + ('U|E|P|' if omitted else 'I|') + 'V|N|J|D|F|T|G|")',
               '$lbr_output(S_stringprobe.EVENTS) = $ptascii("' + ('U|E|P|' if omitted else 'I|') + 'V|N|J|D|F|T|G|B|P|H|")']
    detach = len(lines) - 3
    checks += [
        'S_before = $lbr_seek(S_object,-3,30000)', '$lbr_phase(S_before,-3)', 'S_before.COMPLETION = NORMAL',
        'S_before.STORE[n_field] = DEFINED (PINT 37)', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
        f'S_detached = $lbr_seek(S_before,{detach},30000)', f'$lbr_phase(S_detached,{detach})',
        '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2', 'S_detached.STORE[n_field] = DEFINED (PINT 37)',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_written.STORE[n_field] = DEFINED PNULL', 'S_written.STORE[n_copy] = DEFINED (PINT 17)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
        '~((HCELL n_field) <- S_end.ALLOCATIONS)', '~((HCELL n_copy) <- S_end.ALLOCATIONS)',
    ]
    for index in range(4):
        changed = [first, second, third, fourth]; changed[index] = 'array'
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in changed) + '])) eps'
        normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in changed) + ']'
        checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
    for left in range(4):
        for right in range(left + 1, 4):
            repeated = [first, second, third, fourth]; repeated[right] = repeated[left]
            raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in repeated) + '])) eps'
            normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in repeated) + ']'
            checks += ['~$hook_short_reference_header(' + raw + ',' + normalized + ')']
    checks += header_fields([(first, second, third, fourth)])
    for members in [('int', 'float', 'bool', 'null'), ('mixed', 'float', 'bool', 'string'), ('int', 'float', 'bool', 'string', 'null')]:
        raw = 'NUnionType (SEQUENCE ([' + ','.join('NIdentifier (BYTES ' + peer.quoted(part) + ') eps' for part in members) + '])) eps'
        normalized = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in members) + ']'
        negation = '' if members != ('mixed', 'float', 'bool', 'string') else '~'
        checks += [negation + '$hook_short_reference_header(' + raw + ',' + normalized + ')']
    for state in [*states, 'S_before', 'S_detached', 'S_written', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    joins = [('failed', 'S_return')] if failed_join_only else [('return', success), ('cleanup', 'S_before')]
    for label, state in joins:
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['int-string-bool-float', 'bool-float-int-string', 'string-bool-float-int'])
    parser.add_argument('--headers-only', action='store_true')
    parser.add_argument('--failed-join-only', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.headers_only:
        assert args.form == 'int-string-bool-float'
    if args.failed_join_only:
        assert args.form == 'string-bool-float-int' and not args.headers_only
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
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form, 'scope': 'headers-only' if args.headers_only else 'failed-join-only' if args.failed_join_only else 'lifecycle',
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
        checks = fields(checked['fixture'], source, args.form, args.headers_only, args.failed_join_only)
        report['premises'] = len(checks)
        (out/'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out/'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 360)
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
