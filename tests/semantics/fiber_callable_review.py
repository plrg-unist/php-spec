#!/usr/bin/env python3
"""Independent source-reached scoped Fiber callback and maker lifetime controls."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_callable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}

STAGE = ('S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* '
         '-- if S.CURRENT = eps '
         '-- if $fiber_at(S, pfiberstart.OBJECT) = (pfiber) '
         '-- if pfiber.TARGET = (FIBER_METHOD_TARGET pfibercallable)')
CACHE = [
    'n = pfiberstart.OBJECT', 'pfiber.STATUS = FIBER_INIT', 'pfiber.READY',
    'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.FRAMES = eps',
    'papiquery = pfibercallable.QUERY',
    'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
    'pconfigcall.OWNER = (n)', 'pfiber.CALL = (pconfigcall)',
    'pfiber.RAW = papiquery.VALUE',
    'pfiber.CAPTURE = (pmethodcapture)', 'pfiber.PRODUCER = (pshutdownproducer)',
    'pfibercallable.CAPTURE = pfiber.CAPTURE',
    'pfibercallable.PRODUCER = pfiber.PRODUCER',
    '$class_method_origin(S.CLASSES, pfibercallable.METHOD) = (pmethoddesc)',
    '$consumer_method_valid(S, papiquery, pfibercallable.METHOD, pfibercallable.NAME)',
    '$fiber_callable_raw_valid(S, papiquery)',
    '$fiber_callable_receipt_valid(S, pfibercallable)',
    '$fiber_cache_valid(S, n, pfiber)',
    '$target_function(S, FIBER_METHOD_TARGET pfibercallable) = (pmethoddesc.FUNCTION)',
    '$call_task_valid(S, FIBER_ARGS pfiberstart)',
]
PAUSE = ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
         'S_paused[.COMPLETION = NORMAL] = S']
ENTER = [
    'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
    'S_one.ACTIVEFIBER = (n)',
    'S_one.TODO = [FIBER_ENTER n pnamedargs, FIBER_FINISH n]',
    'pnamedargs.SLOTS = eps', 'pnamedargs.NAMED = eps',
    '$fiber_enter_valid(S_one[.COMPLETION = NORMAL], n, pnamedargs)',
    '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
]


def forged(label, receipt):
    return [
        f'pfibercallable_{label} = {receipt}',
        f'pfiber_{label} = pfiber[.TARGET = (FIBER_METHOD_TARGET pfibercallable_{label})]',
        f'S_{label} = $fiber_put(S, n, pfiber_{label})',
        f'$heap_graph(S_{label}) = $heap_graph(S)',
        f'~$fiber_callable_receipt_valid(S_{label}, pfibercallable_{label})',
        f'~$fiber_cache_valid(S_{label}, n, pfiber_{label})',
        f'~$call_descriptors_valid(S_{label})',
    ]


def finish(chunks):
    events = ', '.join(f'OUTPUT $ptascii({json.dumps(chunk)})' for chunk in chunks)
    return [*review.VALID, *PAUSE, *ENTER, 'S_done = $drive(S, 4000)',
            *review.DONE, f'S_done.EVENTS = [{events}]']


CASES = {
    'cached-alias-class-and-method-snapshots-survive-writes': {
        'source': SOURCES['aliased-class-and-method-cache'], 'stage': STAGE,
        'checks': [
            *CACHE, 'pfibercallable.STATIC', 'pfibercallable.NAME = $ptascii("b")',
            'papiquery.INPUT = PSTRING $ptascii("self")',
            'papiquery.METHOD = DIRECT (PSTRING $ptascii("b"))',
            'papiquery.ORIGINAL = $ptascii("a")',
            'papiquery.SCOPE = (papiquery.CLASS.REQUESTED)',
            'papiquery.CALLED = (papiquery.CLASS.CALLED)',
            'papiquery.THIS = eps', 'papiquery.CLASS.RECEIVER = eps',
            'papiquery.OUTER = eps', 'papiquery.PREFIX = 0', 'papiquery.WIDTH = 0',
            '$class_at(S.CLASSES, papiquery.CLASS.REQUESTED) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("ScopedAlias322")',
            'pfiber.RAW = PARRAY n_raw',
            'S.ARRAYS[n_raw].ITEMS = [ENTRY (KINT 0) (ALIAS n_class), ENTRY (KINT 1) (ALIAS n_method)]',
            'S.STORE[n_class] = DEFINED (PSTRING $ptascii("missing"))',
            'S.STORE[n_method] = DEFINED (PSTRING $ptascii("missing"))',
            '$fiber_callback_nodes(pfiber) = [HARRAY n_raw]',
            '$node_children(S, HOBJECT n) = [HARRAY n_raw]',
            '$target_nodes(FIBER_METHOD_TARGET pfibercallable) = eps',
            '$heap_owners($heap_graph(S), HARRAY n_raw) = 1',
            *forged('scope', 'pfibercallable[.QUERY = papiquery[.SCOPE = eps]]'),
            *forged('line', 'pfibercallable[.QUERY = papiquery[.LINE = $(papiquery.LINE + 1)]]'),
            *forged('static', 'pfibercallable[.STATIC = false]'),
            *forged('leaf', 'pfibercallable[.NAME = $ptascii("missing")]'),
            *finish(['D|', 'C|', 'B|', '2', ':', 'missing', ':', 'missing']),
        ],
    },
    'internal-method-maker-null-callsite-survives-retirement': {
        'source': SOURCES['retired-internal-method-maker'], 'stage': STAGE,
        'checks': [
            *CACHE, '$lookup(S.ENV, $ptascii("maker")) = eps',
            'pmethodcapture.CALLSITE = eps', 'pshutdownproducer.SITE = eps',
            'pshutdownproducer.INTERNAL',
            '$consumer_producer_snapshot(pshutdownproducer)',
            '$consumer_producer_internal_at($fiber_producer_view(S, pfiber.PRODUCER), pshutdownproducer)',
            '~$consumer_capture_valid(S, pconfigcall.SITE, pfiber.CAPTURE)',
            '$fiber_callable_capture_valid(S, pfiber, pconfigcall)',
            '$fiber_producer_valid(S, pfiber)',
            'pfibercallable.STATIC', 'papiquery.THIS = eps',
            'papiquery.CLASS.RECEIVER = eps', 'papiquery.VALUE = PSTRING $ptascii("self::task")',
            'pfiber_ordinary = pfiber[.PRODUCER = (pshutdownproducer[.INTERNAL = false])]',
            'pfibercallable_ordinary = pfibercallable[.PRODUCER = pfiber_ordinary.PRODUCER]',
            'S_ordinary = $fiber_put(S, n, pfiber_ordinary[.TARGET = (FIBER_METHOD_TARGET pfibercallable_ordinary)])',
            '$heap_graph(S_ordinary) = $heap_graph(S)',
            '~$fiber_producer_valid(S_ordinary, pfiber_ordinary)',
            '~$fiber_callable_receipt_valid(S_ordinary, pfibercallable_ordinary)',
            '~$call_descriptors_valid(S_ordinary)',
            *forged('maker', 'pfibercallable[.CAPTURE = (pmethodcapture[.FUNCTION = pfibercallable.METHOD])]'),
            *forged('site', 'pfibercallable[.QUERY = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall[.SITE = pfiberstart.SITE]]]'),
            *finish(['D|', 'K|', 'I|', '17']),
        ],
    },
    'nested-api-maker-receipt-survives-cleared-old-fiber': {
        'source': SOURCES['retired-api-selected-maker'],
        'stage': STAGE + ' -- if pfibercallable.NAME = $ptascii("task")',
        'checks': [
            *CACHE, '$lookup(S.ENV, $ptascii("maker")) = eps',
            'pshutdownproducer.INTERNAL', 'pshutdownproducer.SITE = eps',
            'pshutdownproducer.TARGET = FIBER_METHOD_TARGET pfibercallable_maker',
            'papiquery_maker = pfibercallable_maker.QUERY',
            'papiquery_maker.SOURCE = CONFIG_INVOKE pconfigcall_maker',
            'pconfigcall_maker.OWNER = (n_maker)', 'n_maker =/= n',
            'S.OBJECTS[n_maker] = FIBER pfiber_maker',
            '~((HOBJECT n_maker) <- S.ALLOCATIONS)',
            'pfiber_maker.STATUS = FIBER_TERMINATED',
            'pfiber_maker.CALL = eps', 'pfiber_maker.RAW = PNULL',
            'pfiber_maker.TARGET = eps', 'pfiber_maker.PRODUCER = eps',
            'pfiber_maker.VALUE = POBJECT n',
            '$fiber_at(S, n_maker) = eps',
            '$fiber_callable_receipt_valid(S, pfibercallable_maker)',
            '$target_function(S, FIBER_METHOD_TARGET pfibercallable_maker) = (pfunction_maker)',
            'pfunction_maker.ORIGIN = pmethodcapture.FUNCTION',
            '$fiber_producer_valid(S, pfiber)',
            '$target_nodes(FIBER_METHOD_TARGET pfibercallable_maker) = eps',
            '$node_children(S, HOBJECT n) = eps',
            'pfibercallable_maker_bad = pfibercallable_maker[.QUERY = papiquery_maker[.LINE = $(papiquery_maker.LINE + 1)]]',
            'pshutdownproducer_bad = pshutdownproducer[.TARGET = FIBER_METHOD_TARGET pfibercallable_maker_bad]',
            'pfibercallable_bad = pfibercallable[.PRODUCER = (pshutdownproducer_bad)]',
            'pfiber_bad = pfiber[.PRODUCER = (pshutdownproducer_bad)][.TARGET = (FIBER_METHOD_TARGET pfibercallable_bad)]',
            'S_bad = $fiber_put(S, n, pfiber_bad)',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_callable_receipt_valid(S_bad, pfibercallable_maker_bad)',
            '~$fiber_producer_valid(S_bad, pfiber_bad)',
            '~$fiber_callable_receipt_valid(S_bad, pfibercallable_bad)',
            '~$call_descriptors_valid(S_bad)',
            *finish(['D|', 'D|', 'K|', 'J|', '23']),
        ],
    },
    'same-class-this-and-immutable-string-stay-authenticated': {
        'source': SOURCES['same-class-maker-this-snapshot'], 'stage': STAGE,
        'checks': [
            *CACHE, '~pfibercallable.STATIC',
            '$lookup(S.ENV, $ptascii("first")) = (n_first_cell)',
            '$lookup(S.ENV, $ptascii("other")) = (n_other_cell)',
            'S.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
            'S.STORE[n_other_cell] = DEFINED (POBJECT n_other)', 'n_first =/= n_other',
            'S.OBJECTS[n_first] = INSTANCE porigin_class',
            'S.OBJECTS[n_other] = INSTANCE porigin_class',
            'papiquery.THIS = (n_first)', 'papiquery.CLASS.RECEIVER = (n_first)',
            '$fiber_callback_nodes(pfiber) = eps', '$node_children(S, HOBJECT n) = eps',
            '$target_nodes(FIBER_METHOD_TARGET pfibercallable) = [HOBJECT n_first]',
            'papiquery_other = papiquery[.THIS = (n_other)][.CLASS = papiquery.CLASS[.RECEIVER = (n_other)]]',
            '$consumer_capture_this(S, pconfigcall.SITE, pfiber.CAPTURE, (n_other))',
            '$consumer_method_valid(S, papiquery_other, pfibercallable.METHOD, pfibercallable.NAME)',
            '$fiber_callable_raw_valid(S, papiquery_other)',
            '~$fiber_callable_this_valid(S, pfiber, papiquery_other)',
            *forged('other', 'pfibercallable[.QUERY = papiquery_other]'),
            'papiquery_string = papiquery[.METHOD = DIRECT (PSTRING $ptascii("xxxxxxtask"))]',
            '$consumer_method_valid(S, papiquery_string, pfibercallable.METHOD, pfibercallable.NAME)',
            '~$fiber_callable_raw_valid(S, papiquery_string)',
            *forged('string', 'pfibercallable[.QUERY = papiquery_string]'),
            *finish(['D|', 'K|', 'T', '11', '|', '11']),
        ],
    },
    'parent-callback-receiver-retires-on-authentic-fiber-root': {
        'source': SOURCES['parent-receiver-retirement'],
        'stage': ('S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n) '
                  '-- if $fiber_at(S, n) = (pfiber) '
                  '-- if pfiber.FINISH = (pfiberfinish)'),
        'checks': [
            'S.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("P"), OUTPUT $ptascii("3"), OUTPUT $ptascii("|")]', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = eps', 'pfiber.STATUS = FIBER_RUNNING',
            'pfiber.VALUE = PINT 13', 'pfiber.RETURNED',
            'pfiber.CALL = eps', 'pfiber.RAW = PNULL', 'pfiber.TARGET = eps',
            'pfiber.CAPTURE = eps', 'pfiber.PRODUCER = eps',
            'pfiberfinish.OBJECT = n', 'pfiberfinish.PENDING = eps',
            'pfiberfinish.SEQUENCE = pfiber.SEQUENCE',
            '$fiber_ordinary_root(S)', '$fiber_ordinary_carrier(S, pfiberfinish)',
            'pdestructorcall.OBJECT = n_receiver', 'pdestructorcall.USER',
            '~pdestructorcall.STORE', 'pdestructorcall.CALLER = eps',
            'pdestructorcall.ORIGIN = eps', 'pdestructorcall.RELEASE = (pdestructionrelease)',
            'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_receiver)) :: pdestructionjob_tail*',
            '$destructor_method(S, n_receiver) = (pmethoddesc)',
            'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
            '$fiber_callback_nodes(pfiber) = eps',
            '$task_nodes(DESTRUCTOR_ENTER pdestructorcall) = [HOBJECT n_receiver, HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$task_nodes(FIBER_RETURN_FINISH pfiberfinish) = eps',
            '$destructor_enter_valid(S, pdestructorcall)',
            '~$fiber_ordinary_carrier(S, pfiberfinish[.SEQUENCE = S.FIBERSEQ])',
            '~$destructor_enter_valid(S, pdestructorcall[.USER = false])',
            'S_bad = $fiber_put(S, n, pfiber[.VALUE = PNULL][.RETURNED = false])',
            '$heap_graph(S_bad) = $heap_graph(S)', '~$call_descriptors_valid(S_bad)',
            *review.VALID, *PAUSE,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.CURRENT = (pcallcontext)', 'pcallcontext.RECEIVER = (n_receiver)',
            'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
            '$destructor_context_valid(S_one[.COMPLETION = NORMAL], pcallcontext)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("P"), OUTPUT $ptascii("3"), OUTPUT $ptascii("|"), OUTPUT $ptascii("R"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("13")]',
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.VALUE = PINT 13',
            'n_receiver <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'throwing-deprecation-runtime-exception-inherits-real-exception-storage': {
        'source': SOURCES['deprecation-handler-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
                  '-- if S.OBJECTS[n_error] = THROWABLE pthrowable '
                  '-- if pthrowable.KIND = "RuntimeException"'),
        'checks': [
            'S.EVENTS = [OUTPUT $ptascii("D|")]', '$throwable_live(S, n_error)',
            '$class_instanceof(S, POBJECT n_error, $ptascii("RuntimeException"))',
            '$class_instanceof(S, POBJECT n_error, $ptascii("Exception"))',
            '$class_instanceof(S, POBJECT n_error, $ptascii("Throwable"))',
            '$class_instanceof(S, POBJECT n_error, $ptascii("Stringable"))',
            '~$class_instanceof(S, POBJECT n_error, $ptascii("Error"))',
            '$throwable_field(S, n_error, "message") = PSTRING $ptascii("selection-stop")',
            '$throwable_field(S, n_error, "code") = PINT 0',
            '$throwable_previous_id(S, n_error) = eps',
            '$objectprops_at(S.OBJECTPROPS, n_error) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $throwable_key("Exception", "message")) = (ppropertyslot_message)',
            'ppropertyslot_message.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("message"))',
            'ppropertyslot_message.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("selection-stop")))',
            '$property_slot_at(ppropertyslot*, $throwable_key("Exception", "trace")) = (ppropertyslot_trace)',
            'ppropertyslot_trace.DECL = (INTERNAL_PROPERTY "Exception" $ptascii("trace"))',
            'ppropertyslot_trace.STATE = PROP_VALUE (DIRECT (PARRAY n_trace))',
            '$trace_graph_valid(S, n_trace)',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_trace) = 1',
            'S_bad = S[.OBJECTS = $object_set(S.OBJECTS, n_error, THROWABLE pthrowable[.KIND = "Error"])]',
            '$heap_graph(S_bad) = $heap_graph(S)', '~$throwable_live(S_bad, n_error)',
            '~$call_task_valid(S_bad, THROW_SEARCH n_error)',
            '~$call_descriptors_valid(S_bad)',
            *review.VALID, *PAUSE,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one[.COMPLETION = NORMAL]))',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("E|"), OUTPUT $ptascii("selection-stop")]',
        ],
    },
    'suspended-deprecation-handler-keeps-authentic-constructor-owner': {
        'source': SOURCES['deprecation-handler-suspends'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall_suspend) :: ptask_tail* '
                  '-- if pconfigcall_suspend.KIND = INTRINSIC_FIBER_SUSPEND '
                  '-- if S.ACTIVEFIBER = (n_outer)'),
        'checks': [
            'pconfigcall_suspend.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("W")))]',
            'S.EVENTS = [OUTPUT $ptascii("D|")]',
            '$fiber_at(S, n_outer) = (pfiber_outer)',
            'pfiber_outer.STATUS = FIBER_RUNNING',
            'S.FRAMES = pframe_handler :: pframe_tail*',
            'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (CTOR_RESULT n_child) :: ptask_ctor_tail*',
            'perrorcall.RESUME = API_CALLABLE_RESULT papiquery 1',
            'papiquery.SOURCE = CONFIG_INVOKE pconfigcall_ctor',
            'pconfigcall_ctor.KIND = INTRINSIC_FIBER_CONSTRUCT',
            'pconfigcall_ctor.OWNER = (n_child)', 'n_child =/= n_outer',
            'papiquery.SCOPE =/= eps',
            '$fiber_at(S, n_child) = (pfiber_child)',
            '~pfiber_child.READY', 'pfiber_child.STATUS = FIBER_INIT',
            'pfiber_child.RAW = PNULL', 'pfiber_child.TARGET = eps',
            'S_frame = $constant_frame_scope(S, pframe_handler, pframe_tail*)',
            '$call_task_valid(S_frame, ERROR_HANDLER_RESULT perrorcall)',
            '$ctor_pair_target(S_frame, ERROR_HANDLER_RESULT perrorcall) = (n_child)',
            '$ctor_pair_valid(S_frame, ERROR_HANDLER_RESULT perrorcall, CTOR_RESULT n_child)',
            '~$ctor_pair_valid(S_frame, ERROR_HANDLER_RESULT perrorcall, CTOR_RESULT n_outer)',
            '$ctor_result_valid(S_frame, n_child)',
            '$call_tasks_valid(S_frame, pframe_handler.TODO)',
            '$task_nodes(CTOR_RESULT n_child) = [HOBJECT n_child]',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            'perrorcall_bad = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery[.SCOPE = eps] 1]',
            'pframe_bad = pframe_handler[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: (CTOR_RESULT n_child) :: ptask_ctor_tail*]',
            'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_frame_bad = $constant_frame_scope(S_bad, pframe_bad, pframe_tail*)',
            '$ctor_pair_target(S_frame_bad, ERROR_HANDLER_RESULT perrorcall_bad) = eps',
            '~$ctor_result_valid(S_frame_bad, n_child)',
            '~$call_frames_valid(S_bad, S_bad.FRAMES)',
            '~$call_descriptors_valid(S_bad)',
            *review.VALID, *PAUSE,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = eps', 'S_one.FIBERCALLERS = eps',
            'S_one.RESULT = KNOWN PNULL',
            '$destructor_operation_for(S_one) = (pdestructionoperation)',
            'pdestructionoperation.VALUE = KNOWN (PSTRING $ptascii("W"))',
            'pdestructionoperation.SOURCE = CONFIG_INVOKE pconfigcall_suspend',
            '$fiber_at(S_one, n_outer) = (pfiber_suspended)',
            'pfiber_suspended.STATUS = FIBER_SUSPENDED',
            'pfiber_suspended.VM = (pfibervm)',
            'pfibervm.FRAMES = S.FRAMES', 'pfibervm.CURRENT = S.CURRENT',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_tail*',
            'pfiberapi.OBJECT = n_outer',
            'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)',
            '$fiber_record_valid(S_one[.COMPLETION = NORMAL], n_outer, pfiber_suspended)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one[.COMPLETION = NORMAL]))',
            'S_done = $drive(S_one[.COMPLETION = NORMAL], 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("W"), OUTPUT $ptascii("|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("11")]',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    assert set(args.case) <= CASES.keys()
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Fiber callable source catalog changed during run'
    raise SystemExit(0 if passed else 1)
