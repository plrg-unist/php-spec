#!/usr/bin/env python3
"""Reach a guard-free indirect GET lease inside its real Notice callback."""
import argparse
import json

import fiber_state_review as review
import indirect_magic_get_append_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


NOTICE = 'Indirect modification of overloaded property IndirectMagic84::$secret has no effect'
ERROR = 'Cannot use a scalar value as an array'
ENTRY = ('G', 'secret', ';', 'N', '8', ':', NOTICE, ';', 'G', 'secret', ';', '7', ';', 'U')
PREFIX = ENTRY
TAIL = ('A', '7', ';', 'E', ERROR, ':', 'keep', ';',
        *ENTRY, 'A', '7', ';', 'C', 'keep', ';',
        *ENTRY, 'A', '7', ';', 'R', ERROR, ':', 'keep', ';', '3', 'Z')
assert ''.join(PREFIX + TAIL).encode() == sources.SOURCE_EXPECTED


review.CASES = {
    'indirect-get-notice-cleared-guard-and-single-base-lease': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_notice = PORIGIN 0 ([PCINDEX 1])',
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_get = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 1])',
            'pcallcontext.FUNCTION = porigin_notice',
            'pcallcontext.LEXICAL_CLASS = eps',
            'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.ARGC = 4',
            'S.FRAMES = [pframe_main]',
            'pframe_main.CONTEXT = eps',
            'pframe_main.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_client*',
            'perrorcall.RESUME = PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 7))',
            'perrorcall.TARGET = (pcallcontext.TARGET)',
            'perrorcall.SITE = ppropertyget.SITE',
            'pframe_main.ORIGIN = (ppropertyget.SITE)',
            'perrorcall.LEVEL = 8',
            'perrorcall.LINE = 17',
            'perrorcall.MESSAGE = $ptascii(' + json.dumps(NOTICE) + ')',
            'perrorcall.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE 17',
            'ppropertyget.LINE = 17',
            'ppropertyget.NAME = $ptascii("secret")',
            'ppropertyget.CLASS = porigin_class',
            'ppropertyget.METHOD = porigin_get',
            'ppropertyget.DECL = eps',
            'n_receiver = ppropertyget.OBJECT',
            '$error_context_call(S, pcallcontext) = (perrorcall)',
            '$call_receiver_roots(pcallcontext) = eps',
            '$target_nodes(pcallcontext.TARGET) = eps',
            '$task_nodes(perrorcall.RESUME) = eps',
            '$task_nodes(ERROR_HANDLER_RESULT perrorcall) = eps',
            '$task_nodes(PROPERTY_GET_BASE ppropertyget) = [HOBJECT n_receiver]',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(S.TODO)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$property_get_method(S, n_receiver) = (pmethoddesc_get)',
            'pmethoddesc_get.FUNCTION.ORIGIN = porigin_get',
            'pmethoddesc_get.OWNER = porigin_class',
            '~pmethoddesc_get.FUNCTION.SIGNATURE.BYREF',
            'pmethoddesc_get.FUNCTION.SIGNATURE.RETURNS = eps',
            'pmethoddesc_get.FUNCTION.SIGNATURE.PARAMETERS = [psparam_get]',
            'psparam_get.TYPE = eps',
            '$ppmethod_get_signature(pmethoddesc_get.FUNCTION.SIGNATURE)',
            '$property_effective_desc(S, n_receiver, ppropertyget.NAME) = (ppropertydesc)',
            'ppropertydesc.VISIBILITY = PROPERTY_PRIVATE',
            '~ppropertydesc.STATIC',
            '~ppropertydesc.READONLY',
            'ppropertydesc.SETVISIBILITY = eps',
            'ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            '~$property_hook_unset_declared(S, n_receiver, ppropertydesc.KEY)',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc.KEY) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PINT 7))',
            '$property_get_indirect_source(S, ppropertyget)',
            '$property_get_source(S, ppropertyget)',
            '$property_get_history(S, ppropertyget)',
            '~$property_get_owned_source(S, ppropertyget)',
            '~$property_get_reference_source(S, ppropertyget)',
            '~$property_get_cv_name_source(S, ppropertyget)',
            '~$property_get_guard_tasks(S.TODO, n_receiver, ppropertyget.NAME)',
            '~$property_get_guard_frames(S.FRAMES, n_receiver, ppropertyget.NAME)',
            'ppropertyget.SITE = PORIGIN 0 pcpath_site',
            '$property_get_indirect_parent(S, ppropertyget.SITE) = (porigin_parent)',
            'porigin_parent = PORIGIN 0 pcpath_parent',
            'pcpath_site = pcpath_parent ++ [PCFIELD 0, PCFIELD 0]',
            '$origin_node(S.SOURCES, ppropertyget.SITE) = (expression_property)',
            'expression_property = NExprPropertyFetch (NExprVariable (BYTES text_receiver) metadata_receiver) (NIdentifier (BYTES text_name) metadata_name) metadata_property',
            '$base64(text_receiver) = $ptascii("object")',
            '$base64(text_name) = $ptascii("secret")',
            '$origin_node(S.SOURCES, porigin_parent) = (NExprAssign expression_target expression_rhs metadata_assign)',
            'expression_target = NExprArrayDimFetch expression_property ABSENT metadata_dim',
            'expression_rhs = NScalarInt (INTEGER 1) metadata_rhs',
            '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_dim)',
            'ptask_client* = DIM_CAPTURE :: (ORIGIN_RETURN (porigin_dim)) :: (DIM_APPEND z_dim) :: (ORIGIN_RETURN (porigin_parent)) :: (ASSIGN_PREP expression_target expression_rhs) :: ptask_tail*',
            '$property_get_indirect_tail(S, ppropertyget, ptask_client*)',
            '$lookup(S.ENV, $ptascii("level")) = (n_level)',
            'S.STORE[n_level] = DEFINED (PINT 8)',
            '$lookup(S.ENV, $ptascii("message")) = (n_message)',
            'S.STORE[n_message] = DEFINED pvalue_message',
            '$string_bytes(pvalue_message) = (perrorcall.MESSAGE)',
            '$lookup(S.ENV, $ptascii("line")) = (n_line)',
            'S.STORE[n_line] = DEFINED (PINT 17)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("keep")) = (n_keep)',
            'S.STORE[n_keep] = DEFINED pvalue_keep',
            '$string_bytes(pvalue_keep) = ($ptascii("keep"))',
            '$lookup(S_global.ENV, $ptascii("count")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            'S_saved = $constant_frame_scope(S, pframe_main, eps)',
            '$error_call_valid(S_saved, perrorcall)',
            '$property_get_base_valid(S_saved, ppropertyget)',
            '$property_get_valid(S_saved, ppropertyget, true)',
            '$property_get_indirect_base_tail(S_saved, ppropertyget, S_saved.TODO)',
            '$property_get_base_count(S_saved.TODO, n_receiver, ppropertyget.SITE) = 1',
            '$property_get_carriers(S_saved.TODO, n_receiver, ppropertyget.SITE) = 0',
            '~$property_get_tail_valid(S_saved, ppropertyget)',
            '~$property_get_capture(S_saved, ppropertyget)',
            'S_resume = S_saved[.TODO = perrorcall.RESUME :: (PROPERTY_GET_BASE ppropertyget) :: ptask_client*]',
            '$property_get_tail_valid(S_resume, ppropertyget)',
            '$property_get_base_valid(S_resume, ppropertyget)',
            '$call_task_valid(S_resume, perrorcall.RESUME)',
            '~$property_get_indirect_source(S[.SOURCES = eps], ppropertyget)',
            '~$error_call_valid(S_saved, perrorcall[.LEVEL = 2])',
            '~$error_call_valid(S_saved, perrorcall[.MESSAGE = $ptascii("wrong")])',
            '~$error_call_valid(S_saved, perrorcall[.LINE = 18])',
            '~$error_call_valid(S_saved, perrorcall[.SITE = porigin_notice])',
            'ppropertyget_bad_method = ppropertyget[.METHOD = porigin_notice]',
            '~$error_call_valid(S_saved, perrorcall[.RESUME = PROPERTY_GET_COPY ppropertyget_bad_method (KNOWN (PINT 7))])',
            '~$error_call_valid(S_saved, perrorcall[.RESUME = PROPERTY_GET_COPY ppropertyget (KNOWN (PBOOL true))])',
            'S_missing_base = S_saved[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_client*]',
            '~$error_call_valid(S_missing_base, perrorcall)',
            'S_bad_client = S_saved[.TODO = [(ERROR_HANDLER_RESULT perrorcall), PROPERTY_GET_BASE ppropertyget, DIM_CAPTURE, ORIGIN_RETURN (porigin_dim), DIM_APPEND z_dim, ORIGIN_RETURN (porigin_parent), ASSIGN_PREP expression_target (NScalarInt (INTEGER 2) metadata_rhs)] ++ ptask_tail*]',
            '~$error_call_valid(S_bad_client, perrorcall)',
            'ppropertyget_bad_name = ppropertyget[.NAME = $ptascii("other")]',
            '~$error_call_valid(S_saved, perrorcall[.RESUME = PROPERTY_GET_COPY ppropertyget_bad_name (KNOWN (PINT 7))])',
            *review.VALID,
            'S_paused = $drive(S, 0)',
            'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            *review.DONE,
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
            '$trace_slot(S_done, S_done.ENV, $ptascii("count")) = PINT 3',
            '$trace_slot(S_done, S_done.ENV, $ptascii("keep")) = pvalue_keep',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'n_receiver <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    parser.add_argument('--process-seconds', type=int, default=1800)
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=args.process_seconds) else 1)
