#!/usr/bin/env python3
"""Independent Traversable ownership, callback line and cold unwind checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_traversable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


def generator_forgery(name, traversal='pfibertraversal', operation='pgeneratorop'):
    return [
        f'pfibertraversal_{name} = {traversal}',
        f'pgeneratorop_{name} = {operation}',
        f'pframe_{name} = pframe[.TODO = (GENERATOR_RESUME pgeneratorop_{name}) :: '
        f'(FIBER_TRAVERSE_GENERATOR pfibertraversal_{name} "rewind") :: ptask_saved*]',
        f'S_{name} = S[.FRAMES = [pframe_{name}]]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_traversal_generator_valid(S_{name}, pgeneratorop_{name})',
        f'~$call_descriptors_valid(S_{name})',
    ]


def parked_forgery(name, expression):
    return [
        f'pfibertraversal_{name} = {expression}',
        f'pframe_{name} = pframe_unpack[.TODO = '
        f'(FIBER_TRAVERSE_RESULT pfibertraversal_{name} "key") :: ptask_unpack*]',
        f'pfibervm_{name} = pfibervm[.FRAMES = [pframe_{name}, pframe_base]]',
        f'pfiber_{name} = pfiber_parent[.VM = (pfibervm_{name})]',
        f'S_{name} = S[.OBJECTS[n_parent] = FIBER pfiber_{name}]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_vm_valid(S_{name}, pfibervm_{name}, (n_parent), eps)',
        f'~$call_descriptors_valid(S_{name})',
    ]


MULTILINE = SOURCES['peer-fiber-start-multiline-iterator-callback-trace-uses-unpack-opline']


def multiline_key(line):
    return {
        'source': MULTILINE,
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "key") :: ptask_tail* '
                  f'-- if z = {line}'),
        'checks': [
            'pfiberstart = pfibertraversal.START',
            'porigin = pfiberstart.SITE', 'z = pfibertraversal.LINE',
            'pcalltarget = METHOD_TARGET pfibertraversal.OBJECT porigin_key',
            '$useriter_method_selected(S, pfibertraversal.OBJECT, porigin_key, "key")',
            '$intrinsic_argument(S, porigin, pfiberstart.INDEX) = '
            '((expression, true, eps, pfibertraversal.SITE, z))',
            '~$fiber_traversal_source_line(S, porigin, z)',
            '$fiber_traversal_pending_line(S, porigin, z)',
            '$call_line_valid(S, (porigin), z)',
            '$fiber_traversal_pending(S, pcalltarget, porigin)',
            '$fiber_traversal_call_count(S.TODO, porigin) = 1',
            '$call_task_valid(S, CALL_ARGS pcalltarget eps 0 eps (porigin) z)',
            *review.VALID,
            'H = $heap_graph(S)', 'z_wrong = $(z + 1)',
            'pfibertraversal_wrong = pfibertraversal[.LINE = z_wrong]',
            'S_wrong = S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z_wrong) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_wrong "key") :: ptask_tail*]',
            '$heap_graph(S_wrong) = H',
            '~$fiber_traversal_pending(S_wrong, pcalltarget, porigin)',
            '~$call_task_valid(S_wrong, CALL_ARGS pcalltarget eps 0 eps (porigin) z_wrong)',
            '~$call_descriptors_valid(S_wrong)',
            'S_entered_budget = $drive_steps(S, 1)',
            'S_entered_budget.COMPLETION = BUDGET',
            'S_entered = S_entered_budget[.COMPLETION = NORMAL]',
            'S_entered.CURRENT = (pcallcontext)',
            'pcallcontext.CALLSITE = (porigin)', 'pcallcontext.LINE = z',
            'S_entered.FRAMES = pframe :: pframe_tail*',
            '$fiber_traversal_frame(S_entered, pcallcontext, pframe, pframe_tail*)',
            '$fiber_traversal_context(S_entered, pcallcontext)',
            '$call_line_valid(S_entered, (porigin), z)',
            '$call_descriptors_valid(S_entered)',
            'S_entered_wrong = S_entered[.CURRENT = (pcallcontext[.LINE = z_wrong])]',
            '$heap_graph(S_entered_wrong) = $heap_graph(S_entered)',
            '~$fiber_traversal_context(S_entered_wrong, pcallcontext[.LINE = z_wrong])',
            '~$call_descriptors_valid(S_entered_wrong)',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("key"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("12"), OUTPUT $ptascii("|"), OUTPUT $ptascii("0"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("key"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("22"), OUTPUT $ptascii("|"), OUTPUT $ptascii("0"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("17")]',
        ],
    }


def quiet_unwind(source, line, captured, explicit):
    return {
        'source': source,
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "key") :: ptask_tail* '
                  '-- if S.CURRENT = eps '
                  f'-- if pfibertraversal.LINE = {line}'),
        'checks': [
            'pfiberstart = pfibertraversal.START',
            ('pfibertraversal.CAPTURE = (n_capture)' if captured else
             'pfibertraversal.CAPTURE = eps'),
            ('$exit_method_site(S, pfiberstart.SITE)' if explicit else
             '~$exit_method_site(S, pfiberstart.SITE)') if captured else
            '$fiber_method_site(S, pfiberstart.SITE, eps)',
            '~$destructor_operational(S)', 'S.FIBERSEQ = 1',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.FRAMES = eps',
            'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
            'pfiber_target.STATUS = FIBER_INIT',
            'n_iterator = pfibertraversal.OBJECT',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_iterator) = 2',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_iterator)',
            'pfibertraversal.SENT = {SLOTS eps, NAMED eps}',
            '$fiber_traversal_result_valid(S, pfibertraversal, "key")',
            *review.VALID,
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_removed = S[.TODO = (THROW_SEARCH n_throwable) :: ptask_tail*]',
            '$fiber_start_unpack_unwind_valid(S_removed, '
            'FIBER_TRAVERSE_RESULT pfibertraversal "key")',
            'S_after_budget = $drive_steps(S, 1)', 'S_after_budget.COMPLETION = BUDGET',
            'S_after = S_after_budget[.COMPLETION = NORMAL]',
            'S_after.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_after.DESTRUCTION.RELEASES = eps', 'S_after.DESTRUCTION.OPERATIONS = eps',
            '~((HOBJECT n_iterator) <- S_after.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_after), HOBJECT n_iterator) = 0',
            '(HOBJECT pfiberstart.OBJECT) <- S_after.ALLOCATIONS',
            'S_after.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            'S_done = $drive(S_after, 4000)', *review.DONE,
        ],
    }


def parked_counterexample_case(checks):
    original = CASES['traversable-parked-key-keeps-cv-borrowed-and-reads-mutated-current']
    return {
        'source': original['source'],
        'stage': original['stage'],
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfibervm.CURRENT = (pcallcontext_key)',
            'pfiberstart = pfibertraversal.START', 'n_pack = pfibertraversal.OBJECT',
            'pfibertraversal.INPUT = VARIABLE ($ptascii("pack")) z_input',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_pack) = 5',
            *review.VALID, *checks, *ZERO,
        ],
    }


CASES = {
    'traversable-generator-data-owner-moves-across-real-yield': {
        'source': SOURCES['peer-fiber-start-generator-unpack-freezes-ref-selector-and-retires-last-receiver'],
        'stage': ('S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: ptask_body* '
                  '-- if S.RESULT = KNOWN (PSTRING ($ptascii("7"))) '
                  '-- if S.FRAMES = [pframe] '
                  '-- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: '
                  '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: ptask_saved* '
                  '-- if ptask_saved* = (FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.CURRENT = (pcallcontext)',
            'pfiberstart = pfibertraversal.START', 'n_generator = pfibertraversal.OBJECT',
            'pfibertraversal.CAPTURE = eps',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_generator)',
            'pfibertraversal.CURRENT = KNOWN PNULL',
            'pfibertraversal.ITEMS = eps', 'pfibertraversal.SENT = pfiberstart.SENT',
            'pfiberstart.SENT = {SLOTS eps, NAMED eps}',
            'pfiberstart.INDEX = 0', 'pfiberstart.PACKS = eps',
            '$intrinsic_count(S, pfiberstart.SITE) = (1)',
            'pgeneratorop.OBJECT = n_generator', 'pgeneratorop.STARTPACK',
            'pgeneratorop.NAME = "rewind"', 'pgeneratorop.SITE = pfiberstart.SITE',
            'pgeneratorop.LINE = pfibertraversal.LINE',
            'pgeneratorop.LOOP = eps', 'pgeneratorop.ARGUMENTS = eps',
            '~pgeneratorop.ADVANCE',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING', 'pgenerator.FRAME = eps',
            'pgenerator.FUNCTION = pcallcontext.FUNCTION',
            'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps',
            'pcallcontext.NAMED = eps', 'pcallcontext.RECEIVER = eps',
            '$generator_active(S)', '$generator_operation_trace(S, pgeneratorop) = eps',
            'pfiberarray.KIND = INTRINSIC_FIBER_START',
            'pfiberarray.NAME = $ptascii("StArT")',
            'pfiberarray.INPUT = (n_receiver)', 'pfiberstart.OBJECT = n_receiver',
            'pfiberarray.SITE = pfiberstart.SITE', 'n_selector = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("StArT"))))]',
            '$entry_lookup(S.ARRAYS[n_selector].ITEMS, KINT 0) = (ALIAS n_receiver_ref)',
            '$entry_lookup(S.ARRAYS[n_selector].ITEMS, KINT 1) = (ALIAS n_method_ref)',
            '$entry_value(S, ALIAS n_receiver_ref) = POBJECT n_other',
            '$entry_value(S, ALIAS n_method_ref) = PSTRING ($ptascii("resume"))',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_INIT',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("pair")) = (n_pair_cell)',
            'S.STORE[n_pair_cell] = DEFINED PNULL',
            '~((HARRAY n_selector) <- S.ALLOCATIONS)',
            'H = $heap_graph(S)', '$heap_owners(H, HARRAY n_selector) = 0',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_generator) = 2',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]',
            '$task_nodes(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") = '
            '[HOBJECT n_receiver, HOBJECT n_generator]',
            '$task_nodes(FIBER_ARRAY_START_RELEASE pfiberarray) = eps',
            'S_scope = $constant_frame_scope(S, pframe, eps)',
            '$fiber_traversal_input(S_scope, pfibertraversal)',
            '$fiber_traversal_valid(S_scope, pfibertraversal)',
            '$fiber_traversal_generator_header(pgeneratorop, pfibertraversal, "rewind")',
            '$fiber_traversal_generator_valid(S, pgeneratorop)',
            '$call_task_valid(S_scope, GENERATOR_RESUME pgeneratorop)',
            '$call_task_valid(S_scope, FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind")',
            'S_orphan = S_scope[.TODO = (FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: ptask_saved*]',
            '~$call_task_valid(S_orphan, FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind")',
            '~$call_descriptors_valid(S_orphan)',
            *generator_forgery('site', 'pfibertraversal[.SITE = pfiberstart.SITE]'),
            *generator_forgery('line', 'pfibertraversal[.LINE = $(pfibertraversal.LINE + 1)]',
                              'pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]'),
            *generator_forgery('index', 'pfibertraversal[.START.INDEX = 1]'),
            *generator_forgery('current', 'pfibertraversal[.CURRENT = KNOWN (PINT 9)]'),
            *generator_forgery('tag', operation='pgeneratorop[.STARTPACK = false]'),
            *generator_forgery('advance', operation='pgeneratorop[.ADVANCE = true]'),
            *generator_forgery('method', operation='pgeneratorop[.NAME = "current"]'),
            'pframe_missing = pframe[.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_saved*]',
            'S_missing = S[.FRAMES = [pframe_missing]]',
            '~$generator_operation_site(S_missing, pgeneratorop)',
            '~$call_descriptors_valid(S_missing)',
            'pframe_duplicate = pframe[.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: '
            '(GENERATOR_RESUME pgeneratorop) :: ptask_saved*]',
            'S_duplicate = S[.FRAMES = [pframe_duplicate]]',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_generator) = 3',
            '~$fiber_traversal_generator_valid(S_duplicate, pgeneratorop)',
            '~$call_descriptors_valid(S_duplicate)',
            *review.VALID, *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.CURRENT = eps', 'S_one.FRAMES = eps',
            'S_one.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: ptask_saved*',
            'S_one.OBJECTS[n_generator] = GENERATOR pgenerator_one',
            'pgenerator_one.PHASE = GENERATOR_PAUSED',
            'pgenerator_one.VALUE = (PSTRING ($ptascii("7")))',
            'pgenerator_one.KEY = (PSTRING ($ptascii("value")))',
            '$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "generator") :: ptask_saved*',
            '$task_nodes(FIBER_TRAVERSE_RESULT pfibertraversal "generator") = '
            '[HOBJECT n_receiver, HOBJECT n_generator, HOBJECT n_generator]',
            '$heap_owners($heap_graph(S_two), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S_two), HOBJECT n_receiver) = 1',
            '$fiber_traversal_result_valid(S_two, pfibertraversal, "generator")',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            *FINISH,
            events('G|', 'C|', '7', '|', 'D', '|', 'X', '|', 'F|', 'Y', '|', '1', '|', '0'),
            '~((HOBJECT n_generator) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'traversable-parked-key-keeps-cv-borrowed-and-reads-mutated-current': {
        'source': SOURCES['peer-fiber-start-iterator-key-parks-parent-before-reading-current-reference'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_parent) '
                  '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
                  '-- if pfiber_parent.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "key") :: ptask_unpack*'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiber_parent.STATUS = FIBER_SUSPENDED',
            'pfibervm.CURRENT = (pcallcontext_key)',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_key*',
            'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)',
            'pfiberapi.SENT = (PSTRING ($ptascii("S")))',
            'pfiberapi.OBJECT = n_parent', 'pfiberapi.SEQUENCE = pfiber_parent.SEQUENCE',
            'pfiberstart = pfibertraversal.START', 'n_pack = pfibertraversal.OBJECT',
            'pfibertraversal.CAPTURE = eps', 'pfibertraversal.ITEMS = eps',
            'pfibertraversal.SENT = {SLOTS eps, NAMED eps}',
            'pfiberstart.SENT = pfibertraversal.SENT',
            'pfiberstart.INDEX = 0', 'pfiberstart.PACKS = eps',
            'pfibertraversal.INPUT = VARIABLE ($ptascii("pack")) z_input',
            '$operand_nodes(pfibertraversal.INPUT) = eps',
            'pfibertraversal.CURRENT = REFERENCE n_current',
            'S.STORE[n_current] = DEFINED (PSTRING ($ptascii("11")))',
            'pcallcontext_key.RECEIVER = (n_pack)',
            '$context_target(pcallcontext_key) = METHOD_TARGET n_pack porigin_key',
            'pcallcontext_key.CALLSITE = (pfiberstart.SITE)',
            'pcallcontext_key.LINE = pfibertraversal.LINE',
            'pcallcontext_key.ARGC = 0', 'pcallcontext_key.EXTRA = eps',
            'pcallcontext_key.NAMED = eps',
            '$useriter_method_selected(S, n_pack, porigin_key, "key")',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("pack")) = (n_pack_cell)',
            'S.STORE[n_pack_cell] = DEFINED (POBJECT n_pack)',
            'pframe_unpack.LOCALS = (psymboltable_parent)',
            '$lookup(psymboltable_parent.ENV, $ptascii("pack")) = (n_parent_pack_cell)',
            'S.STORE[n_parent_pack_cell] = DEFINED (POBJECT n_pack)',
            'n_pack_cell =/= n_parent_pack_cell',
            'pfiber_parent.RAW = POBJECT n_parent_closure',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_pack) = 5',
            '$heap_count(HOBJECT n_pack, $node_children(S, HCELL n_pack_cell)) = 1',
            '$heap_count(HOBJECT n_pack, $node_children(S, HCELL n_parent_pack_cell)) = 1',
            '$heap_count(HOBJECT n_pack, $node_children(S, HOBJECT n_parent_closure)) = 1',
            '$heap_count(HOBJECT n_pack, $call_context_roots((pcallcontext_key))) = 1',
            '$fiber_traversal_nodes(pfibertraversal, true) = [HCELL n_current, HOBJECT n_pack]',
            '$heap_count(HOBJECT n_pack, '
            '$task_nodes(FIBER_TRAVERSE_RESULT pfibertraversal "key")) = 1',
            '$heap_owners(H, HCELL n_current) = 2',
            '$heap_count(HCELL n_current, $node_children(S, HOBJECT n_pack)) = 1',
            '$heap_owners(H, HOBJECT n_parent) = 2',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '$fiber_traversal_input(S_view, pfibertraversal)',
            '$fiber_traversal_frame(S_view, pcallcontext_key, pframe_unpack, [pframe_base])',
            '$fiber_traversal_context(S_view, pcallcontext_key)',
            '$call_line_valid(S_view, pcallcontext_key.CALLSITE, pcallcontext_key.LINE)',
            '$call_arity_valid(S_view, pcallcontext_key)',
            '$call_extent_valid(S_view, pcallcontext_key)',
            '$named_context_valid(S_view, pcallcontext_key)',
            '$fiber_continue_valid(S_view, pfiberapi)',
            '$fiber_vm_valid(S, pfibervm, (n_parent), eps)',
            *review.VALID, *ZERO, *FINISH,
            events('W|', 'C|', 'K|', 'S', '|', '0', '|', '11', '|', 'T', '|',
                   '', '|', '1', '|', '23', '|', '17'),
        ],
    },
}

# Separate expensive saved-VM observations at the inherited process cap.
# Pure negative queries share the unchanged source/stage and the ownership
# case's complete resume; each independently admits its state and preserves zero budget.
CASES.update({
    'traversable-parked-site-forgery': parked_counterexample_case([
        *parked_forgery('site', 'pfibertraversal[.SITE = pfiberstart.SITE]'),
    ]),
    'traversable-parked-line-forgery': parked_counterexample_case([
        *parked_forgery('line', 'pfibertraversal[.LINE = $(pfibertraversal.LINE + 1)]'),
    ]),
    'traversable-parked-index-forgery': parked_counterexample_case([
        *parked_forgery('index', 'pfibertraversal[.START.INDEX = 1]'),
    ]),
    'traversable-parked-variable-forgery': parked_counterexample_case([
        *parked_forgery('variable', 'pfibertraversal[.INPUT = '
                        'VARIABLE ($ptascii("target")) z_input]'),
    ]),
    'traversable-parked-missing-continuation': parked_counterexample_case([
            'pframe_missing = pframe_unpack[.TODO = ptask_unpack*]',
            'pfibervm_missing = pfibervm[.FRAMES = [pframe_missing, pframe_base]]',
            'S_missing = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_missing)]]',
            '~$fiber_vm_valid(S_missing, pfibervm_missing, (n_parent), eps)',
            '~$call_descriptors_valid(S_missing)',
    ]),
    'traversable-parked-duplicate-callback-scheduling': parked_counterexample_case([
            '$context_target(pcallcontext_key) = METHOD_TARGET n_pack porigin_key',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            'S_pending = S_scope[.ORIGIN = (pfiberstart.SITE)][.TODO = '
            '(CALL_ARGS (METHOD_TARGET n_pack porigin_key) eps 0 eps '
            '(pfiberstart.SITE) pfibertraversal.LINE) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "key") :: ptask_unpack*]',
            '$fiber_traversal_pending(S_pending, METHOD_TARGET n_pack porigin_key, pfiberstart.SITE)',
            'S_duplicate = S_pending[.TODO = S_pending.TODO ++ '
            '[CALL_ARGS (METHOD_TARGET n_pack porigin_key) eps 0 eps '
            '(pfiberstart.SITE) pfibertraversal.LINE]]',
            '$fiber_traversal_call_count(S_duplicate.TODO, pfiberstart.SITE) = 2',
            '~$fiber_traversal_pending(S_duplicate, METHOD_TARGET n_pack porigin_key, pfiberstart.SITE)',
            'pframe_duplicate = pframe_unpack[.TODO = '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "key") :: '
            '(CALL_ARGS (METHOD_TARGET n_pack porigin_key) eps 0 eps '
            '(pfiberstart.SITE) pfibertraversal.LINE) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_saved_duplicate = S[.OBJECTS[n_parent] = '
            'FIBER pfiber_parent[.VM = (pfibervm_duplicate)]]',
            '$fiber_traversal_call_count(pframe_duplicate.TODO, pfiberstart.SITE) = 1',
            '$heap_owners($heap_graph(S_saved_duplicate), HOBJECT n_pack) = 6',
            '~$fiber_vm_valid(S_saved_duplicate, pfibervm_duplicate, (n_parent), eps)',
            '~$call_descriptors_valid(S_saved_duplicate)',
    ]),
})
CASES.update({f'multiline-key-line-{line}-authenticates-real-continuation': multiline_key(line)
              for line in (12, 22)})
CASES.update({
    'cold-ordinary-method-key-unwind': quiet_unwind(MULTILINE, 12, False, False),
    'cold-explicit-fcc-key-unwind': quiet_unwind(MULTILINE, 22, True, True),
    'cold-direct-fcc-key-unwind': quiet_unwind(
        SOURCES['peer-fiber-start-direct-fcc-quiet-iterator-error-retains-selected-receiver'],
        14, True, False),
})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Traversable START originals changed during run'
    raise SystemExit(0 if passed else 1)
