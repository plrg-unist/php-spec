#!/usr/bin/env python3
"""Reach typed later sends, source-free body writes and two-payload error traces."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review
import iterator_call_unpack_noninitial_fixed_reference_state as previous

CATALOG = Path(__file__).with_name('iterator_call_unpack_noninitial_typed_reference_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__), Path(previous.__file__)]
SOURCES = {row['id'].removeprefix('iterator-call-unpack-noninitial-typed-reference-'): row['source']
           for row in json.loads(CATALOG.read_bytes())}
ADMISSION = previous.ADMISSION
POST = previous.POST
ZERO = previous.ZERO
ONE = previous.ONE
BASE = previous.BASE
LIVE = previous.LIVE
POSITIONAL = previous.POSITIONAL
CLASS_TYPE = ('[(PTBRANCH ([(PTCLASS $ptascii("TypedLaterB42"))])), '
              '(PTBRANCH ([PTBUILTIN "null"]))]')
ARRAY_TYPE = '[(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]'


def rejection_checks(array):
    payload = 'PARRAY n_array' if array else 'POBJECT n_current'
    target = 'TypedLaterB42' if array else 'TypedLaterA42'
    given = 'array' if array else 'TypedLaterB42'
    shape = (['S.STORE[n_right] = DEFINED (PARRAY n_array)',
              'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current))]',
              '$node_children(S, HARRAY n_array) = [HOBJECT n_current]',
              '$heap_owners($heap_graph(S), HARRAY n_array) = 1']
             if array else ['S.STORE[n_right] = DEFINED (POBJECT n_current)'])
    trace_children = '[HOBJECT n_earlier, HARRAY n_array]' if array else '[HOBJECT n_earlier, HOBJECT n_current]'
    return [
        '$receiving_function(S, porigin) = (pfunction)',
        'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 2',
        'pcallcontext.HOLES = eps', 'pcallcontext.LINE = 26',
        'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
        'pcallcontext.CALLSITE = (porigin_call)',
        'psparam = pfunction.SIGNATURE.PARAMETERS[1]',
        r'psparam.BYREF /\ ~psparam.VARIADIC',
        'psparam.TYPE = [(PTBRANCH ([(PTCLASS $ptascii("' + target + '"))])), '
        '(PTBRANCH ([PTBUILTIN "null"]))]',
        '$default_parameter_line(S, porigin, 1) = 16',
        '$lookup(S.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        'n_left =/= n_right', 'n_left <- S.REFCELLS', 'n_right <- S.REFCELLS',
        'S.STORE[n_left] = DEFINED (POBJECT n_earlier)', *shape,
        '$object_name(S, n_earlier) = $ptascii("TypedLaterA42")',
        '$object_name(S, n_current) = $ptascii("TypedLaterB42")',
        'n_current =/= n_earlier',
        '~$typed_reference_cell_source(S, n_left)',
        '~$typed_reference_cell_source(S, n_right)',
        '~$typed_parameter_source(S, psparam)',
        '$typed_parameter_conversion(S, psparam, ' + payload + ') = TYPEREJECT',
        '$heap_owners($heap_graph(S), HCELL n_left) = 1',
        '$heap_owners($heap_graph(S), HCELL n_right) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
        'S.DESTRUCTION.CALLED = [n_data]',
        '$object_name(S, n_data) = $ptascii("TypedLaterIterator42")',
        '~((HOBJECT n_data) <- S.ALLOCATIONS)',
        '$call_task_valid(S, TYPE_RECEIVE porigin 1)', *ADMISSION, *ZERO, *ONE,
        'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        '$throwable_field(S_one, n_error, "line") = PINT 16',
        '$throwable_field(S_one, n_error, "code") = PINT 0',
        '$string_bytes($throwable_field(S_one, n_error, "message")) = '
        '($ptascii("typedLaterTarget42(): Argument #2 ($right) must be of type ?' + target + ', '
        + given + ' given, called in ") ++ $call_sourcefile(S.FILES, porigin_call) '
        '++ $ptascii(" on line 26"))',
        '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
        '$entry_lookup(S_one.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_trace_frame))',
        '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("function")) = '
        '(DIRECT (PSTRING $ptascii("typedLaterTarget42")))',
        '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("args")) = '
        '(DIRECT (PARRAY n_trace_args))',
        'S_one.ARRAYS[n_trace_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier)), '
        'ENTRY (KINT 1) (DIRECT (' + payload + '))]',
        '$node_children(S_one, HARRAY n_trace_args) = ' + trace_children,
        '$trace_graph_valid(S_one, n_trace)',
        '$heap_owners($heap_graph(S_one), HCELL n_left) = 1',
        '$heap_owners($heap_graph(S_one), HCELL n_right) = 1',
        '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
        *(['$heap_owners($heap_graph(S_one), HARRAY n_array) = 2',
           '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1']
          if array else ['$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2']),
        'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
        'S_one.EVENTS = S.EVENTS', *POST,
        'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S, 4001) = S_done',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("16"), '
        'OUTPUT $ptascii("|HELD|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
        '$heap_owners($heap_graph(S_done), HCELL n_left) = 0',
        '$heap_owners($heap_graph(S_done), HCELL n_right) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_earlier) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
        *(['$heap_owners($heap_graph(S_done), HARRAY n_array) = 0'] if array else []),
        '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
        'n_earlier <- S_done.DESTRUCTION.CALLED', 'n_current <- S_done.DESTRUCTION.CALLED',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


CASES = {
    'later-nullable-class-warning-captures-before-receive': {
        'source': SOURCES['positional-class-private-overwrite'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *BASE, *POSITIONAL, *LIVE,
            '$object_name(S, n_current) = $ptascii("TypedLaterB42")',
            'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'psparam_left = pfunction.SIGNATURE.PARAMETERS[0]',
            'psparam_right = pfunction.SIGNATURE.PARAMETERS[1]',
            'psparam_right.TYPE = ' + CLASS_TYPE,
            '$iterator_unpack_reference_type(psparam_right.TYPE)',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (KNOWN (POBJECT n_current))',
            *ADMISSION,
            'pfunction_plain = pfunction[.SIGNATURE.PARAMETERS = [psparam_left, '
            'psparam_right[.TYPE = [(PTBRANCH ([(PTCLASS $ptascii("TypedLaterB42"))]))]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_plain]], piteratorunpack)',
            'pfunction_reversed = pfunction[.SIGNATURE.PARAMETERS = [psparam_left, '
            'psparam_right[.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), '
            '(PTBRANCH ([(PTCLASS $ptascii("TypedLaterB42"))]))]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_reversed]], piteratorunpack)',
            'pfunction_variadic = pfunction[.SIGNATURE.PARAMETERS = '
            '[psparam_left, psparam_right[.VARIADIC = true]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_variadic]], piteratorunpack)',
            *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = KNOWN (POBJECT n_current)]'
            '[.SNAPSHOT = (POBJECT n_current)]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 26',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'typedLaterTarget42() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'later-class-body-overwrite-has-no-persistent-type-source': {
        'source': SOURCES['positional-class-private-overwrite'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("typedLaterTarget42") '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("R|"))'),
        'checks': [
            '$receiving_function(S, pcallcontext.FUNCTION) = (pfunction)',
            'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
            'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps', 'pcallcontext.LINE = 26',
            'psparam = pfunction.SIGNATURE.PARAMETERS[1]', 'psparam.TYPE = ' + CLASS_TYPE,
            '$lookup(S.ENV, $ptascii("left")) = (n_left)',
            '$lookup(S.ENV, $ptascii("right")) = (n_right)',
            'n_left =/= n_right', 'n_left <- S.REFCELLS', 'n_right <- S.REFCELLS',
            'S.STORE[n_left] = DEFINED PNULL', 'S.STORE[n_right] = DEFINED (PINT 17)',
            '~$typed_reference_cell_source(S, n_left)', '~$typed_reference_cell_source(S, n_right)',
            '~$typed_parameter_source(S, psparam)',
            '$typed_parameter_conversion(S, psparam, PINT 17) = TYPEREJECT',
            'S.DESTRUCTION.CALLED = [n_data, n_earlier, n_current]',
            '$object_name(S, n_data) = $ptascii("TypedLaterIterator42")',
            '$object_name(S, n_earlier) = $ptascii("TypedLaterA42")',
            '$object_name(S, n_current) = $ptascii("TypedLaterB42")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S), HCELL n_left) = 1',
            '$heap_owners($heap_graph(S), HCELL n_right) = 1', *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R|")]',
            'S_one.STORE = S.STORE', 'S_one.PROPREFS = S.PROPREFS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'later-class-receive-rejection-materializes-both-object-arguments': {
        'source': SOURCES['class-mismatch-trace-retains-two-objects'],
        'stage': ('S.TODO = [TYPE_RECEIVE porigin 1] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("typedLaterTarget42")'),
        'checks': rejection_checks(False),
    },
    'later-class-receive-rejection-materializes-object-and-array-child': {
        'source': SOURCES['array-mismatch-trace-retains-object-and-array-child'],
        'stage': ('S.TODO = [TYPE_RECEIVE porigin 1] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("typedLaterTarget42")'),
        'checks': rejection_checks(True),
    },
    'parked-wrong-type-second-warning-injects-before-receive': {
        'source': SOURCES['wrong-type-parked-injection-precedes-receive'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
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
            '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'psparam = pfunction.SIGNATURE.PARAMETERS[1]', 'psparam.TYPE = ' + ARRAY_TYPE,
            '$object_name(S, n_current) = $ptascii("TypedLaterB42")',
            '$lookup(S.ENV, $ptascii("marker")) = (n_marker)',
            'S.STORE[n_marker] = DEFINED (PINT 17)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_error))]',
            '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            '$typed_conversion_at(S_scope, psparam.TYPE, POBJECT n_current, false) = TYPEREJECT',
            '$iterator_unpack_reference_allowed(S_scope, piteratorunpack)',
            '$iterator_unpack_warning_hold(S_scope, piteratorunpack) = (KNOWN (POBJECT n_current))',
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
            '~$call_descriptors_valid(S_bad)', *ONE,
            'S_one.ACTIVEFIBER = (n_fiber)',
            '$fiber_at(S_one, n_fiber) = (pfiber_running)',
            'pfiber_running.STATUS = FIBER_RUNNING', 'pfiber_running.VM = eps',
            'S_one.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)',
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            'S_one.STORE = S.STORE', 'S_one.STORE[n_marker] = DEFINED (PINT 17)',
            'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
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
    process_caps = {}

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        if directory.name == 'parked-wrong-type-second-warning-injects-before-receive':
            cap = 180
        process_caps[directory.name] = cap
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
    report['budgets']['process_seconds'] = max(process_caps.values())
    report.update(author_inputs=before, author_inputs_stable=stable,
                  case_process_seconds=process_caps, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
