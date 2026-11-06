#!/usr/bin/env python3
"""Indexed CV SEND2 copies, ordinary-cell limits, and real payload lifetime."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_later_cv_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_later_cv_magic_controls.json'
MISSING = 'magic-later-cv-missing-before-warning'
MISSING_ROW = next(row for row in json.loads(CONTROLS.read_text())['cases'] if row['id'] == MISSING)
CASE = 'magic-later-cv-unwrapped-pending-leaf'
ROW = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == CASE)
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) (porigin_site) z_site) :: ptask_send_tail* '
        '-- if S.CURRENT = eps')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14_new phpType24_new ABSENT phpType44_new phpType42_new phpType23_new metadata_class_new) phpType6_new metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) '
       '-- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SEND)
for label, front in [('new', NEW), ('return', RETURN)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$later202_' + label + '_')


def checks(fixture, filename):
    out = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'porigin_site = pmagicmethodcall.SITE',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_later]',
        'phpType7_later = NArg ABSENT expression_later (BOOLEAN false) (BOOLEAN false) metadata_later',
        'expression_later = NExprVariable (BYTES text_later) metadata_variable',
        '$base64(text_later) = $ptascii("later")',
        '$call_argument_origin(S,(porigin_site),1) = (porigin_later)',
        'porigin_later = PORIGIN n_unit pcpath_later',
        '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$source_emission_cv(S,n_unit,pcpath_later,expression_later)',
        '~(pcpath_later <- $call_argument_paths(pcode.EXPRESSIONS))',
        '$magic_method_argument_source(S,porigin_later,1,expression_later)',
        '$magic_method_copy_source(S,porigin_site,pmagicmethodcall.ARGUMENTS,1)',
        '$magic_method_later_cv(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_cv_pending(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall)',
        'z_later = $runtime_line(S[.ORIGIN = (porigin_later)],eps,expression_later)',
        'S.RESULT = VARIABLE ($ptascii("later")) $variable_line(BYTES text_later,metadata_variable)',
        '$lookup(S.ENV,$ptascii("later")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        '~(n_cell <- S.REFCELLS)',
        'S.OBJECTS[n_payload] = INSTANCE porigin_payload',
        '(HOBJECT n_payload) <- S.ALLOCATIONS',
        '$node_children(S,HOBJECT n_payload) = eps',
        '~((HOBJECT 0) <- S.ALLOCATIONS)', 'n_payload =/= 0',
        '$magic_method_value(S,POBJECT n_payload)',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) (porigin_site) z_site) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$factory182_output(S.EVENTS) = $ptascii("LEAF;SHIFT;")',
        '$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        'S_copy = $call_send_parameter(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        'S_copy = S[.RESULT = KNOWN (POBJECT n_payload)]',
        '$value_nodes(POBJECT n_payload) = [HOBJECT n_payload]',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    # These are sharp derived states at the real send, before resolve can warn.
    denied = [
        ('missing', 'S[.ENV = eps]'),
        ('undefined', 'S[.STORE = $set_cell(S.STORE,n_cell,UNDEFINED)]'),
        ('known', 'S[.RESULT = KNOWN (POBJECT n_payload)]'),
        ('reference', 'S[.RESULT = REFERENCE n_cell]'),
        ('name', 'S[.RESULT = VARIABLE ($ptascii("owner")) $variable_line(BYTES text_later,metadata_variable)]'),
        ('line', 'S[.RESULT = VARIABLE ($ptascii("later")) $($variable_line(BYTES text_later,metadata_variable) + 1)]'),
        ('debt', 'S[.LITERALREFDEBTS = [n_cell]]'),
        ('property', 'S[.PROPREFS = [{CELL n_cell,SOURCES eps}]]'),
        ('coercion', 'S[.REFCOERCIONS = [{CELL n_cell,SITE porigin_site,LINE z_later,VALUE $ptascii("old")}]]'),
        ('backing', 'S[.PARAMETERBACKINGS = [{FUNCTION pmagicmethodcall.METHOD,INDEX 0,CELL n_cell,LINE z_later,VALUE $ptascii("old")}]]'),
        ('plain_string', 'S[.STORE = $set_cell(S.STORE,n_cell,DEFINED (PSTRING $ptascii("bytes")))]'),
        ('owned_nul', 'S[.STRINGDATA = [[65,0,66]]][.STORE = $set_cell(S.STORE,n_cell,DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) [65,0,66]))]'),
        ('no_code', 'S[.CODE = eps]'),
        ('no_source', 'S[.SOURCES = eps]'),
        ('not_send', 'S[.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN (POBJECT n_payload)]) (porigin_site) z_site) :: ptask_send_tail*]'),
    ]
    for label, state in denied:
        out += [
            'S_' + label + ' = ' + state,
            '~$call_send_value_allowed(S_' + label + ',MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        ]
    out += [
        'S_refused = $call_send_parameter(S_undefined,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        'S_refused.COMPLETION = UNSUPPORTED "by-value argument send domain"',
        'S_refused.EVENTS = S.EVENTS',
        '~$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_site),z_later)',
        '~$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),$(z_later + 1))',
        '$magic_method_argument_source(S,porigin_later,0,expression_later)',
        '$magic_unpack_explicit_source(S,porigin_later,expression_later)',
        '~$magic_method_later_cv([phpType7_first,NArg ABSENT expression_later (BOOLEAN false) (BOOLEAN true) metadata_later])',
        '$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET (pmagicmethodcall[.ARGUMENTS = [phpType7_first,NArg ABSENT expression_later (BOOLEAN false) (BOOLEAN true) metadata_later]]),1,expression_later,(porigin_site),(porigin_later),z_later)',
        '$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0,expression_later,(porigin_site),(porigin_later),z_later)',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_one.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN (POBJECT n_payload)]) (porigin_site) z_site) :: ptask_send_tail*',
        'S_one.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        '$heap_owners($heap_graph(S_one),HOBJECT n_payload) = 2',
        '~((HCELL n_cell) <- $task_nodes(S_one.TODO[0]))',
        '$call_descriptors_valid(S_one)', '$gc_state_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        'S_new_found = $later202_new_seek(S_one,2048)', 'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall',
        'pvalue_sent* = [PINT 7,POBJECT n_payload]',
        'S_new.STORE[n_cell] = DEFINED PNULL',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array([PINT 7,POBJECT n_payload],0)',
        '$node_children(S_new,HARRAY n_arguments) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S_new),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$factory182_output(S_new.EVENTS) = $ptascii("LEAF;SHIFT;HANDLER;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $later202_return_seek(S_new,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_return,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_payload) = 1',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$factory182_output(S_return.EVENTS) = $ptascii("LEAF;SHIFT;HANDLER;OWNER;")',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return out


def warning_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'porigin_site = pmagicmethodcall.SITE',
        'pmagicmethodcall.NAME = $ptascii("missing")',
        'pmagicmethodcall.ARGUMENTS[1] = NArg ABSENT expression_later (BOOLEAN false) (BOOLEAN false) metadata_later',
        '$call_argument_origin(S,(porigin_site),1) = (porigin_later)',
        'z_later = $call_send_line(S,(porigin_site),1)',
        '$magic_method_argument_source(S,porigin_later,1,expression_later)',
        '$magic_method_cv_pending(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall)',
        '$lookup(S.ENV,$ptascii("later")) = eps',
        '$error_handler_eligible(S,2)',
        '$error_missing_operand(S,S.RESULT)',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;")',
        '~$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        '$error_read_plan(S) = eps', '~$error_read_pending(S)',
        'S_refused = $call_send_parameter(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(porigin_site),(porigin_later),z_later)',
        'S_refused.COMPLETION = UNSUPPORTED "by-value argument send domain"',
        'S_refused.EVENTS = S.EVENTS',
        'S_done = $drive_steps(S,64)',
        'S_done.COMPLETION = UNSUPPORTED "by-value argument send domain"',
        'S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = $ptascii("SHIFT;")',
        '$call_descriptors_valid(S_done)', '$gc_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


def render(case, fixture, filename):
    clauses = warning_boundary(fixture, filename) if case['source'] == MISSING_ROW['source'] else checks(fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROW['source']}, MISSING: {'source': MISSING_ROW['source']}},
                 extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
