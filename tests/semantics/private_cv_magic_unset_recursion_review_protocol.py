#!/usr/bin/env python3
"""Reach private recursive unset before its guard-preserving visibility error."""
import argparse
import json

import fiber_state_review as review
import private_cv_magic_unset_recursion_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


ERROR = 'Cannot access private property PrivateCVUnset86::$secret'
PREFIX = ('M', 'secret', ';', 'U')
TAIL = ('E', ERROR, ';', 'A', '8', ';', 'C', 'keep', ';',
        'M', 'secret', ';', 'U', 'E', ERROR, ';', 'A', '8', ';',
        'F', 'keep', ';', '2', 'Z')
assert ''.join(PREFIX + TAIL).encode() == sources.SOURCE_EXPECTED


review.CASES = {
    'private-unset-active-guard-keeps-denied-storage-and-error-scope': {
        'source': sources.SOURCE.decode(),
        'stage': ('S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX)
                  + ' -- if S.TODO = UNSET_ARRAY :: ptask_tail*'
                  + ' -- if S.BASE = BASE_PROPERTY_PENDING pbase (VARIABLE ptbytes_selector z_name) z_receiver'
                  + ' -- if S.ORIGIN = (porigin_inner) -- if $property_current_line(S) = 6'),
        'checks': [
            'porigin_helper = PORIGIN 0 ([PCINDEX 1])',
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_unset = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 2])',
            'pcallcontext.FUNCTION = porigin_helper',
            'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 1',
            'S.SOURCEPENDING = eps', 'S.RESULT = KNOWN PNULL',
            'S.FRAMES = [pframe_unset, pframe_main]',
            'pframe_unset.CONTEXT = (pcallcontext_unset)',
            'pframe_main.CONTEXT = eps',
            'pframe_main.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_main_tail*',
            'pframe_main.ORIGIN = (ppropertyunset.SITE)',
            'ppropertyunset.LINE = 19',
            'ppropertyunset.NAME = $ptascii("secret")',
            'ppropertyunset.CLASS = porigin_class',
            'ppropertyunset.METHOD = porigin_unset',
            'n_receiver = ppropertyunset.OBJECT',
            'pcallcontext_unset.TARGET = PROPERTY_UNSET_TARGET ppropertyunset',
            'pcallcontext_unset.FUNCTION = porigin_unset',
            'pcallcontext_unset.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext_unset.CALLED_CLASS = (porigin_class)',
            'pcallcontext_unset.RECEIVER = (n_receiver)',
            'pcallcontext_unset.CALLSITE = (ppropertyunset.SITE)',
            '$property_unset_frame(S, pcallcontext_unset, pframe_main, ppropertyunset)',
            '$property_unset_entered(S, S.CURRENT, S.FRAMES, ppropertyunset)',
            '$property_unset_guard(S, S.CURRENT, S.FRAMES, n_receiver, ppropertyunset.NAME)',
            '$call_receiver_roots(pcallcontext_unset) = eps',
            '$call_receiver_roots(pcallcontext) = eps',
            '$target_nodes(pcallcontext_unset.TARGET) = eps',
            '$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_receiver]',
            '$base_nodes(S.BASE) = eps',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(S.TODO)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$property_unset_method(S, n_receiver) = (pmethoddesc_unset)',
            'pmethoddesc_unset.FUNCTION.ORIGIN = porigin_unset',
            '$property_magic_method_source(S, pmethoddesc_unset, "__unset")',
            '$property_effective_desc(S, n_receiver, ppropertyunset.NAME) = (ppropertydesc_secret)',
            'ppropertydesc_secret.ORIGIN = ppropertyunset.PROPERTY',
            'ppropertydesc_secret.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_secret.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            'ppropertydesc_secret.KEY =/= ppropertyunset.NAME',
            '$property_lookup_scope(S) = eps',
            '$closure_source_class(S, porigin_inner) = eps',
            '$property_resolve(S, n_receiver, ppropertyunset.NAME) = PROPERTY_DENIED ppropertydesc_secret',
            '$property_resolve_scope(S, n_receiver, ppropertyunset.NAME, (porigin_class)) = PROPERTY_ACCESS ppropertydesc_secret.KEY',
            '~$property_hook_unset_declared(S, n_receiver, ppropertydesc_secret.KEY)',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_secret.KEY) = (ppropertyslot_secret)',
            'ppropertyslot_secret.STATE = PROP_VALUE (DIRECT (PINT 8))',
            '$property_unset_needed(S, n_receiver, ppropertyunset.NAME)',
            '$property_effective_desc(S, n_receiver, $ptascii("plain")) = (ppropertydesc_plain)',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_plain.KEY) = (ppropertyslot_plain)',
            'ppropertyslot_plain.STATE = PROP_VALUE (DIRECT (PINT 99))',
            '$lookup(S.ENV, $ptascii("current")) = (n_current)',
            'S.STORE[n_current] = DEFINED (POBJECT n_receiver)',
            '$lookup(S.ENV, $ptascii("member")) = (n_member)',
            'S.STORE[n_member] = DEFINED pvalue_member',
            '$string_bytes(pvalue_member) = ($ptascii("secret"))',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("name")) = (n_name)',
            'S.STORE[n_name] = DEFINED pvalue_name',
            '$string_bytes(pvalue_name) = ($ptascii("plain"))',
            '$lookup(S_global.ENV, $ptascii("keep")) = (n_keep)',
            'S.STORE[n_keep] = DEFINED pvalue_keep',
            '$string_bytes(pvalue_keep) = ($ptascii("keep"))',
            '$lookup(S_global.ENV, $ptascii("count")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            '$origin_node(S.SOURCES, porigin_inner) = (expression_inner)',
            'expression_inner = NExprPropertyFetch (NExprVariable (BYTES text_current) metadata_current) (NExprVariable (BYTES text_member) metadata_member) metadata_inner',
            '$base64(text_current) = $ptascii("current")',
            '$base64(text_member) = $ptascii("member")',
            'ptbytes_selector = $ptascii("member")', 'z_name = 6',
            '$property_pending_source_base(S, S.BASE, expression_inner)',
            '$property_magic_cv_source(S, porigin_inner, 6)',
            '$property_magic_cv_name(S[.RESULT = VARIABLE ptbytes_selector z_name], porigin_inner, 6) = (ppropertyunset.NAME)',
            '$property_unset_pending_receiver(S, pbase) = (n_receiver)',
            'ppropertyunset_inner = ppropertyunset[.SITE = porigin_inner][.LINE = 6]',
            '$property_unset_capture(S, ppropertyunset_inner)',
            '$property_unset_pending(S)',
            '~$property_unset_public_clear_pending(S)',
            '$property_unset_plan(S) = eps',
            '$property_unset_public_guarded_plan(S) = eps',
            '$property_unset_private_guarded_plan(S) = (S_error)',
            'S_error.COMPLETION = THROWN "Error" ($ptascii(' + json.dumps(ERROR) + ')) 6',
            'S_error.OBJECTPROPS = S.OBJECTPROPS',
            'S_error.CURRENT = S.CURRENT', 'S_error.FRAMES = S.FRAMES',
            'S_error.TODO = S.TODO', 'S_error.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_error), HOBJECT n_receiver) = 2',
            'PhpStep: S ~> S_error[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$property_unset_private_guarded_plan(S[.SOURCES = eps]) = eps',
            '$property_unset_private_guarded_plan(S[.ORIGIN = (ppropertyunset.SITE)]) = eps',
            '$property_unset_private_guarded_plan(S[.BASE = BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ppropertyunset.NAME)) z_receiver]) = eps',
            '$property_unset_private_guarded_plan(S[.BASE = BASE_PROPERTY_PENDING pbase (VARIABLE ptbytes_selector 7) z_receiver]) = eps',
            '$property_unset_private_guarded_plan(S[.RESULT = KNOWN (PINT 1)]) = eps',
            'S_noguard = S[.FRAMES = [pframe_unset[.CONTEXT = eps], pframe_main]]',
            '~$property_unset_guard(S_noguard, S_noguard.CURRENT, S_noguard.FRAMES, n_receiver, ppropertyunset.NAME)',
            '$property_unset_private_guarded_plan(S_noguard) = eps',
            '$property_unset_plan(S_noguard) = (ppropertyunset_inner)',
            'S_saved = $constant_frame_scope(S, pframe_main, eps)',
            '$property_unset_valid(S_saved, ppropertyunset)',
            '$property_unset_tail(S_saved, ppropertyunset, S_saved.TODO)',
            '~$property_unset_capture(S_saved, ppropertyunset)',
            *review.VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            *review.DONE,
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
            '$trace_slot(S_done, S_done.ENV, $ptascii("count")) = PINT 2',
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
