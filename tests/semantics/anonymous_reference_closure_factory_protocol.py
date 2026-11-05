#!/usr/bin/env python3
"""Own Closure RETURNREF, parent mode and actual returned CELL ownership."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_reference_closure_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
FRONT = ('S.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell_return) z_return false porigin_return) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = CLOSURE_TARGET n_closure')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)
ARROW_FRONT = ('S.TODO = (RETURN_REF_UNWIND (KNOWN (POBJECT n_child)) z_return false porigin_return) :: ptask_tail* '
               '-- if S.CURRENT = (pcallcontext) '
               '-- if pcallcontext.TARGET = CLOSURE_TARGET n_closure')


def context(fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        'P.CLASSES = [pclassdesc_child,pclassdesc_owner]',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("capture")) = (pmethoddesc)',
        '~pmethoddesc.FUNCTION.SIGNATURE.BYREF',
        'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
        'pfunction_closure.ORIGIN = PORIGIN 0 pcpath_closure',
        'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
        'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
        'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
        '$origin_node([P.FOLD.SOURCE],pclassdesc_owner.ORIGIN) = (pcnode_owner)',
        '$plclasscontext(P.FOLD.SOURCE,pcpath_owner,$base64(' + filename + '),pclassdesc_owner.LINE) = (ptcontext_owner)',
        '$anonymous_named_header(pcnode_owner,ptcontext_owner) = ((pchheader,z_owner))',
        'ptcontext = $ppmethod_context(P,pchheader,$ptascii("capture"),2)',
        'P_method = P[.CLOSURE = false][.RETURNREF = false][.GOTOROOT = pcpath_method][.CLASSCONTEXT = (ptcontext)][.FOLD = P.FOLD[.CLOSURE = false][.FUNCTION = pclassdesc_owner.NAME ++ $ptascii("::capture")][.CLASSCONTEXT = (ptcontext)]]',
        '$anonymous_factory_context(P_method,pcpath_new)',
        '~$anonymous_factory_context(P_method[.RETURNREF = true],pcpath_new)',
        'P_closure = P_method[.CLOSURE = true][.RETURNREF = true][.GOTOROOT = pcpath_closure][.FOLD = P_method.FOLD[.CLOSURE = true][.FUNCTION = pfunction_closure.NAME]]',
        '$anonymous_factory_context(P_closure,pcpath_new)',
        '~$anonymous_factory_context(P_closure[.RETURNREF = false],pcpath_new)',
        '~$anonymous_factory_context(P_closure[.FOLD.FUNCTION = $ptascii("forged")],pcpath_new)',
        '~$anonymous_factory_context(P_closure[.FOLD.CLASSCONTEXT = eps],pcpath_new)',
        '~$anonymous_factory_context(P_method[.FOLD.FUNCTION = $ptascii("forged")],pcpath_new)',
    ]


def returned_cell(row, fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_owner]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        'pfunction_closure.SIGNATURE.BYREF',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pfunction_closure.ORIGIN',
        'pcallcontext.INSTANCE = (n_closure)',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.RECEIVER = (n_receiver)',
        '(HOBJECT n_receiver) <- $node_children(S,HOBJECT n_closure)',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = eps',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_owner.ORIGIN)',
        '$reference_returning(S)', '$reference_return_used(S)',
        '$lookup(S.ENV,$ptascii("child")) = (n_cell_return)',
        'n_cell_return <- S.REFCELLS',
        'S.STORE[n_cell_return] = DEFINED (POBJECT n_child)',
        'S.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_owner.ORIGIN',
        '(HCELL n_cell_return) <- S.ALLOCATIONS',
        '(HOBJECT n_child) <- S.ALLOCATIONS',
        '(HOBJECT n_child) <- $node_children(S,HCELL n_cell_return)',
        '$call_task_valid(S,RETURN_REF_UNWIND (REFERENCE n_cell_return) z_return false porigin_return)',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$class_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$call_task_valid(S,RETURN_REF_UNWIND (REFERENCE n_cell_return) z_return false pclassdesc_owner.ORIGIN)',
        'S_split = $drive_steps(S,3)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4099)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$declaration_history_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


def arrow_notice(row, fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', ARROW_FRONT,
        'pcallcontext.FUNCTION = porigin_return',
        '$arrow_return(S[.ORIGIN = (porigin_return)],z_return) = (expression_return)',
        '~$goto_scope_valid(S,porigin_return)',
        '~$reference_return_null_valid(S[.ORIGIN = (porigin_return)],z_return)',
        '$reference_arrow_boundary(S,porigin_return,z_return)',
        '$reference_return_value_valid(S[.ORIGIN = (porigin_return)],z_return)',
        '$reference_notice_source(S,porigin_return,KNOWN (POBJECT n_child),z_return,REF_NOTICE_VALUE)',
        '$call_task_valid(S,RETURN_REF_UNWIND (KNOWN (POBJECT n_child)) z_return false porigin_return)',
        '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$reference_notice_source(S,porigin_return,KNOWN (POBJECT n_child),$(z_return + 1),REF_NOTICE_VALUE)',
        '~$call_task_valid(S,RETURN_REF_UNWIND (KNOWN (POBJECT n_child)) z_return true porigin_return)',
        'S_notice_found = $drive_steps(S,1)',
        'S_notice_found.COMPLETION = BUDGET',
        'S_notice = S_notice_found[.COMPLETION = NORMAL]',
        'S_notice.TODO = [REF_RETURN_NOTICE_BEGIN porigin_return (KNOWN (POBJECT n_child)) z_return REF_NOTICE_VALUE]',
        '$call_task_valid(S_notice,REF_RETURN_NOTICE_BEGIN porigin_return (KNOWN (POBJECT n_child)) z_return REF_NOTICE_VALUE)',
        '$call_descriptors_valid(S_notice)', '$heap_valid($heap_graph(S_notice))',
        'S_split = $drive_steps(S_notice,3)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_notice,4099)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '$closure_state_valid(S_done)', '$class_state_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def render(case, fixture, filename):
    checks = (context(fixture, filename) if case['id'] == 'ref-closure-cv-receiver-lifetime-context'
              else arrow_notice(ROWS[case['id']], fixture, filename) if case['id'] == 'ref-arrow-temporary-return-notice'
              else returned_cell(ROWS[case['id']], fixture, filename))
    prefix = names.PREFIX.replace(names.FRONT, ARROW_FRONT) if case['id'] == 'ref-arrow-temporary-return-notice' else PREFIX
    return (prefix + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or ['ref-closure-cv-receiver-lifetime-context', 'ref-closure-cv-receiver-lifetime', 'ref-arrow-temporary-return-notice']
    ROWS['ref-closure-cv-receiver-lifetime-context'] = ROWS['ref-closure-cv-receiver-lifetime']
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in selected},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
