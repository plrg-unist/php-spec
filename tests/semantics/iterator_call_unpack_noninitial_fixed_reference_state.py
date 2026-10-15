#!/usr/bin/env python3
"""Reach noninitial raw holds, private fixed cells and ordered abort cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_noninitial_fixed_reference_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id'].removeprefix('iterator-call-unpack-noninitial-fixed-reference-'): row['source']
           for row in json.loads(CATALOG.read_bytes())}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
BASE = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
        'piteratorunpack.CURRENT = REFERENCE n_raw',
        'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        'piteratorunpack.CALL.SENT.NAMED = eps',
        'S.STORE[n_prior] = DEFINED (POBJECT n_earlier)',
        'n_prior <- S.REFCELLS', 'n_prior =/= n_raw',
        'n_data =/= n_earlier',
        '$heap_owners($heap_graph(S), HCELL n_prior) = 1']
LIVE = ['S.STORE[n_raw] = DEFINED (POBJECT n_current)', 'n_raw <- S.REFCELLS',
        'n_data =/= n_current', 'n_earlier =/= n_current',
        '$objectprops_record_at(S.OBJECTPROPS, n_data) = (pobjectprops)',
        '$property_slot_at(pobjectprops.SLOTS, $ptascii("current")) = (ppropertyslot_current)',
        'ppropertyslot_current.STATE = PROP_VALUE (ALIAS n_raw)',
        '$property_slot_at(pobjectprops.SLOTS, $ptascii("earlier")) = (ppropertyslot_earlier)',
        'ppropertyslot_earlier.STATE = PROP_VALUE (ALIAS n_source_earlier)',
        'n_source_earlier =/= n_prior', 'n_source_earlier =/= n_raw',
        'S.STORE[n_source_earlier] = DEFINED (POBJECT n_earlier)',
        '$node_children(S, HOBJECT n_data) = [HCELL n_source_earlier, HCELL n_raw]',
        '$heap_owners($heap_graph(S), HCELL n_source_earlier) = 1',
        '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2']
POSITIONAL = ['piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]',
              'piteratorunpack.KEY = KNOWN (PINT 1)', '~piteratorunpack.NAMED',
              '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1']
HELD = ['piteratorunpack.HOLD = KNOWN (POBJECT n_current)',
        'piteratorunpack.SNAPSHOT = (POBJECT n_current)',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2']
ABORT_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
               '-- if pdestructionoperation.PENDING = (n_error) '
               '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"')

CASES = {
    'second-positional-warning-detaches-only-current-payload': {
        'source': SOURCES['positional-normal'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *BASE, *POSITIONAL, *LIVE,
            'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (KNOWN (POBJECT n_current))',
            *ADMISSION,
            '~$iterator_unpack_reference_allowed(S, piteratorunpack[.NAMED = true])',
            'piteratorunpack_occupied = piteratorunpack[.KEY = KNOWN (PSTRING $ptascii("left"))]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_occupied)',
            'piteratorunpack_holes = piteratorunpack[.CALL = piteratorunpack.CALL'
            '[.SENT = {SLOTS ([NAMED_HOLE]), NAMED eps}]]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_holes)',
            'piteratorunpack_extra = piteratorunpack[.CALL = piteratorunpack.CALL'
            '[.SENT.NAMED = [($ptascii("extra"), REFERENCE n_prior)]]]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_extra)',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'psparam_left = pfunction.SIGNATURE.PARAMETERS[0]',
            'psparam_right = pfunction.SIGNATURE.PARAMETERS[1]',
            'pfunction_typed = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = '
            '[psparam_left, psparam_right[.TYPE = [(PTBRANCH ([PTCLASS $ptascii("NoninitialB40")])), '
            '(PTBRANCH ([PTBUILTIN "null"]))]]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_typed]], piteratorunpack)',
            'pfunction_variadic = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = '
            '[psparam_left, psparam_right[.VARIADIC = true]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_variadic]], piteratorunpack)',
            *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = KNOWN (POBJECT n_current)]'
            '[.SNAPSHOT = (POBJECT n_current)]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 26',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'noninitialTarget40() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
            'piteratorunpack_array = piteratorunpack_held[.HOLD = KNOWN (PARRAY 0)]'
            '[.SNAPSHOT = (PARRAY 0)]',
            '~$iterator_unpack_hold_allowed(S_one, piteratorunpack_array, "byref")',
        ],
    },
    'second-positional-send-keeps-earlier-private-cell': {
        'source': SOURCES['positional-normal'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *BASE, *POSITIONAL, *LIVE, *HELD,
            '$iterator_unpack_hold_live(S, piteratorunpack, "byref")', *ADMISSION, *ZERO,
            'piteratorunpack_missing = piteratorunpack[.HOLD = KNOWN PNULL][.SNAPSHOT = eps]',
            'S_missing = S[.TODO = (ITERATOR_UNPACK piteratorunpack_missing "byref") :: ptask_tail*]',
            '~$call_descriptors_valid(S_missing)',
            'S_changed = S[.STORE[n_raw] = DEFINED (POBJECT n_earlier)]',
            '$heap_valid($heap_graph(S_changed))',
            '~$iterator_unpack_hold_live(S_changed, piteratorunpack, "byref")',
            '~$call_descriptors_valid(S_changed)', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw)]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.SNAPSHOT = eps', '~piteratorunpack_next.NAMED',
            'piteratorunpack_next.CALL.SENT.SLOTS = '
            '[NAMED_SENT (REFERENCE n_prior), NAMED_SENT (REFERENCE n_fresh)]',
            'n_fresh =/= n_prior', 'n_fresh =/= n_raw', 'n_fresh =/= n_source_earlier',
            'n_fresh <- S_one.REFCELLS',
            'S_one.STORE[n_fresh] = DEFINED (POBJECT n_current)',
            'S_one.STORE[n_prior] = S.STORE[n_prior]',
            'S_one.STORE[n_raw] = S.STORE[n_raw]',
            '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4001) = S_done',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("X|"), OUTPUT $ptascii("V|"), '
            'OUTPUT $ptascii("I|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("L|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("E")]',
            'n_data <- S_done.DESTRUCTION.CALLED',
            'n_earlier <- S_done.DESTRUCTION.CALLED',
            'n_current <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HCELL n_prior) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'reversed-abort-retires-current-before-earlier-without-reading-source': {
        'source': SOURCES['reversed-named-warning-throw'],
        'stage': (ABORT_STAGE +
                  ' -- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (REFERENCE n_prior)]'
                  ' -- if piteratorunpack.SNAPSHOT = (POBJECT n_current)'
                  ' -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_current), '
                  'DESTRUCTION_VALUE (HCELL n_prior)]'),
        'checks': [
            *BASE, 'piteratorunpack.NAMED',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("left")))',
            'piteratorunpack.HOLD = KNOWN (POBJECT n_current)',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$objectprops_record_at(S.OBJECTPROPS, n_data) = eps',
            'n_data <- S.DESTRUCTION.CALLED',
            '~(n_current <- S.DESTRUCTION.CALLED)', '~(n_earlier <- S.DESTRUCTION.CALLED)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$iterator_unpack_hold_allowed(S_scope, piteratorunpack, "byref")',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HCELL n_raw, HOBJECT n_data, HOBJECT n_data, HOBJECT n_current, HCELL n_prior]',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO,
            'S_erased = S[.STORE[n_raw] = UNDEFINED]',
            '$heap_graph(S_erased) = $heap_graph(S)',
            '$eager_operation_source_valid(S_erased, pdestructionoperation)',
            '$call_descriptors_valid(S_erased)', *ONE,
            'S_one.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructorcall.OBJECT = n_current',
            'pdestructorcall.PENDING = (n_error)',
            'pdestructionrelease_next.JOBS = [DESTRUCTION_VALUE (HCELL n_prior)]',
            'n_current <- S_one.DESTRUCTION.CALLED',
            '~(n_earlier <- S_one.DESTRUCTION.CALLED)',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("B|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("T|"), OUTPUT $ptascii("51"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_prior) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'parked-second-warning-keeps-prior-private-and-current-detached-owners': {
        'source': SOURCES['positional-parked-resume'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref" '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *BASE, *POSITIONAL, *LIVE,
            'piteratorunpack.HOLD = KNOWN (POBJECT n_current)',
            'piteratorunpack.SNAPSHOT = (POBJECT n_current)',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$lookup(S.ENV, $ptascii("marker")) = (n_marker)',
            'S.STORE[n_marker] = DEFINED (PINT 17)',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
            '$iterator_unpack_hold_live(S_scope, piteratorunpack, "byref")',
            '$error_entered_call_valid(S_scope, perrorcall)',
            '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', 'perrorcall.LINE = 28',
            *ADMISSION, *ZERO,
            'piteratorunpack_missing = piteratorunpack[.HOLD = KNOWN PNULL][.SNAPSHOT = eps]',
            'perrorcall_bad = perrorcall[.RESUME = ITERATOR_UNPACK piteratorunpack_missing "byref"]',
            'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
            'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.STORE[n_marker] = DEFINED (PINT 17)',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("X|"), OUTPUT $ptascii("V|"), '
            'OUTPUT $ptascii("I|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("L|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("R|"), '
            'OUTPUT $ptascii("FIB|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("17"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            'n_data <- S_done.DESTRUCTION.CALLED',
            'n_earlier <- S_done.DESTRUCTION.CALLED',
            'n_current <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HCELL n_prior) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'later-positional-key-errors-before-second-warning-or-hold': {
        'source': SOURCES['named-then-positional-error'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.NAMED '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *BASE, *LIVE,
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (REFERENCE n_prior)]',
            'piteratorunpack.KEY = KNOWN (PINT 0)',
            'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail*',
            '$throwable_live(S_one, n_error)',
            '$object_name(S_one, n_error) = $ptascii("Error")',
            '$throwable_field(S_one, n_error, "message") = PSTRING '
            '$ptascii("Cannot use positional argument after named argument during unpacking")',
            '$throwable_field(S_one, n_error, "line") = PINT 26',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            '$drive_steps(S, 2) = S_two_budget',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error"',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HCELL n_prior)]',
            '$iterator_lookup(S_two.ITERATORS, n_cursor) = eps',
            '$destructor_release_valid(S_two, pdestructionrelease)',
            '$destructor_operation_valid(S_two, pdestructionoperation)',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in INPUTS}
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = before == {str(path): digest(path) for path in INPUTS}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                     cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable,
                  head_stable=head_stable, passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
