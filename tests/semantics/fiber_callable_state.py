#!/usr/bin/env python3
"""Pending constructor selection and retired bound-maker source controls."""
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
VALID = review.VALID
DONE = review.DONE
PAUSE = ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
         'S_paused[.COMPLETION = NORMAL] = S']
PENDING = [
    'pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT', 'pconfigcall.OWNER = (n)',
    '$fiber_at(S, n) = (pfiber)', 'pconfigcall.INDEX = 1',
    'pconfigcall.SENT = [NAMED_SENT (KNOWN papiquery.VALUE)]',
    'papiquery.VALUE = PSTRING $ptascii("self::task")',
    'papiquery.METHOD = DIRECT papiquery.VALUE', 'papiquery.OUTER = eps',
    'papiquery.LINE = pconfigcall.LINE',
    '$api_source_valid(S, papiquery)', '$api_query_valid(S, papiquery, 1)',
    '$fiber_callable_pending_valid(S, papiquery)',
    '$task_nodes(API_CALLABLE_RESULT papiquery 1) = $config_nodes(pconfigcall)',
    '$heap_count(HOBJECT n, $task_nodes(API_CALLABLE_RESULT papiquery 1)) = 1',
]
for field, value in [('LINE', '0'), ('INDEX', '0'), ('KIND', 'INTRINSIC_FIBER_STARTED')]:
    suffix = field.lower()
    PENDING += [
        f'pconfigcall_{suffix} = pconfigcall[.{field} = {value}]',
        f'papiquery_{suffix} = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_{suffix}]',
        f'S_{suffix} = S[.TODO = (API_CALLABLE_RESULT papiquery_{suffix} 1) :: ptask_tail*]',
        f'$heap_graph(S_{suffix}) = $heap_graph(S)',
        f'~$call_task_valid(S_{suffix}, API_CALLABLE_RESULT papiquery_{suffix} 1)',
        f'~$call_descriptors_valid(S_{suffix})',
    ]
PENDING += [
    'papiquery_scope = papiquery[.SCOPE = eps]',
    'S_scope = S[.TODO = (API_CALLABLE_RESULT papiquery_scope 1) :: ptask_tail*]',
    '$heap_graph(S_scope) = $heap_graph(S)',
    '~$fiber_callable_pending_valid(S_scope, papiquery_scope)',
    '~$call_descriptors_valid(S_scope)',
    '~$api_source_valid(S, papiquery[.SOURCE = CONFIG_INVOKE pconfigcall[.OWNER = eps]])',
    '~$api_source_valid(S, papiquery[.VALUE = PSTRING $ptascii("parent::task")])',
    *VALID, *PAUSE,
]
STAGE = ('S.TODO = (API_CALLABLE_RESULT papiquery 1) :: ptask_tail* '
         '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
         '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT')

CASES = {
    'constructor-deprecation-result-authenticates-original-source': {
        'source': SOURCES['private-self-string'], 'stage': STAGE,
        'checks': [
            *PENDING,
            'ptask_tail* = (CTOR_RESULT n) :: ptask_after*',
            '$ctor_result_valid(S, n)',
            '$ctor_pair_target(S, API_CALLABLE_RESULT papiquery 1) = (n)',
            '$ctor_pair_valid(S, API_CALLABLE_RESULT papiquery 1, CTOR_RESULT n)',
            '~$ctor_pair_valid(S, API_CALLABLE_RESULT papiquery 1, CTOR_RESULT $nabs($(n + 1)))',
            'S_wrong_result = S[.TODO = (API_CALLABLE_RESULT papiquery 1) :: (CTOR_RESULT $nabs($(n + 1))) :: ptask_after*]',
            '$task_nodes(CTOR_RESULT n) = [HOBJECT n]',
            '~$call_descriptors_valid(S_wrong_result)',
            '~$ctor_result_valid(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n)], n)',
            '~pfiber.READY', 'pfiber.RAW = PNULL', 'pfiber.TARGET = eps',
            'pfiber.STATUS = FIBER_INIT', 'S.EVENTS = [OUTPUT $ptascii("D|")]',
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.OBJECTS[n] = FIBER pfiber_selected', 'pfiber_selected.READY',
            'pfiber_selected.RAW = papiquery.VALUE',
            'pfiber_selected.TARGET = (FIBER_METHOD_TARGET pfibercallable)',
            'pfibercallable.QUERY = $consumer_query_selected(S, papiquery)',
            'pfibercallable.CAPTURE = pfiber_selected.CAPTURE',
            'pfibercallable.PRODUCER = pfiber_selected.PRODUCER',
            '$fiber_callable_receipt_valid(S_one[.COMPLETION = NORMAL], pfibercallable)',
            '$fiber_cache_valid(S_one[.COMPLETION = NORMAL], n, pfiber_selected)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("T"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT $ptascii("8")]',
        ],
    },
    'repeated-constructor-validates-callback-before-ready-error': {
        'source': SOURCES['repeated-constructor-warns-first'], 'stage': STAGE,
        'checks': [
            *PENDING, 'pfiber.READY', 'pfiber.RAW = PSTRING $ptascii("error_reporting")',
            'pfiber.TARGET = (FIBER_REPORTING_TARGET)', 'pfiber.STATUS = FIBER_INIT',
            'S.EVENTS = [OUTPUT $ptascii("D|")]', '$fiber_cache_valid(S, n, pfiber)',
            '$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Fiber")))]))], POBJECT n)',
            '$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("fIbEr")))]))], POBJECT n)',
            '$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Exception")))])), (PTBRANCH ([(PTCLASS ($ptascii("Fiber")))]))], POBJECT n)',
            '~$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Closure")))]))], POBJECT n)',
            '~$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Throwable")))]))], POBJECT n)',
            '~$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Fiber"))), (PTCLASS ($ptascii("Stringable")))]))], POBJECT n)',
            '$typed_given(S, POBJECT n) = $ptascii("Fiber")',
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.OBJECTS[n] = FIBER pfiber',
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            '$throwable_field(S_one, n_error, "message") = PSTRING $ptascii("Cannot call constructor twice")',
            '$fiber_cache_valid(S_one[.COMPLETION = NORMAL], n, pfiber)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("Cannot call constructor twice"), OUTPUT $ptascii("|"), OUTPUT $ptascii("30719"), OUTPUT $ptascii(":"), OUTPUT $ptascii("30719"), OUTPUT $ptascii(":"), OUTPUT $ptascii("19")]',
        ],
    },
    'bound-maker-retired-certificate-keeps-original-scope': {
        'source': SOURCES['author-fiber-constructor-callable-bound-maker-source-scope'],
        'stage': 'S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* -- if $fiber_at(S, pfiberstart.OBJECT) = (pfiber)',
        'checks': [
            'n = pfiberstart.OBJECT', 'S.ACTIVEFIBER = eps', 'S.CURRENT = eps',
            'pfiber.STATUS = FIBER_INIT', 'pfiber.READY',
            'pfiber.TARGET = (FIBER_METHOD_TARGET pfibercallable)',
            'papiquery = pfibercallable.QUERY', 'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
            'pfiber.CALL = (pconfigcall)', 'pfiber.RAW = papiquery.VALUE',
            'pfiber.CAPTURE = (pmethodcapture)', 'pfiber.PRODUCER = (pshutdownproducer)',
            '~pshutdownproducer.INTERNAL', 'pshutdownproducer.BINDING = (pclosurebinding)',
            '~((HOBJECT pclosurebinding.OBJECT) <- S.ALLOCATIONS)',
            'pclosurebinding.LEXICAL = (porigin_class)',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("FiberCallableChild322B")',
            'papiquery.SCOPE = (porigin_class)', 'papiquery.CALLED = (porigin_class)',
            'papiquery.THIS = eps', 'pmethodcapture.LEXICAL_CLASS = (porigin_class)',
            'pmethodcapture.CALLED_CLASS = (porigin_class)',
            '$fiber_callback_nodes(pfiber) = eps', '$target_nodes(FIBER_METHOD_TARGET pfibercallable) = eps',
            '$fiber_producer_valid(S, pfiber)', '$fiber_callable_receipt_valid(S, pfibercallable)',
            '$fiber_cache_valid(S, n, pfiber)', '$call_task_valid(S, FIBER_ARGS pfiberstart)',
            'pfibercallable_scope = pfibercallable[.QUERY = papiquery[.SCOPE = eps]]',
            'pfiber_scope = pfiber[.TARGET = (FIBER_METHOD_TARGET pfibercallable_scope)]',
            'S_scope = $fiber_put(S, n, pfiber_scope)', '$heap_graph(S_scope) = $heap_graph(S)',
            '~$fiber_callable_receipt_valid(S_scope, pfibercallable_scope)',
            '~$fiber_cache_valid(S_scope, n, pfiber_scope)', '~$call_descriptors_valid(S_scope)',
            'pfibercallable_capture = pfibercallable[.CAPTURE = eps]',
            'pfiber_capture = pfiber[.TARGET = (FIBER_METHOD_TARGET pfibercallable_capture)]',
            'S_capture = $fiber_put(S, n, pfiber_capture)', '$heap_graph(S_capture) = $heap_graph(S)',
            '~$fiber_cached_target_valid(S_capture, pfiber_capture)',
            '~$call_descriptors_valid(S_capture)',
            'pfibercallable_static = pfibercallable[.STATIC = false]',
            'pfiber_static = pfiber[.TARGET = (FIBER_METHOD_TARGET pfibercallable_static)]',
            'S_static = $fiber_put(S, n, pfiber_static)', '$heap_graph(S_static) = $heap_graph(S)',
            '~$fiber_callable_receipt_valid(S_static, pfibercallable_static)',
            '~$fiber_cache_valid(S_static, n, pfiber_static)', '~$call_descriptors_valid(S_static)',
            *VALID, *PAUSE,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = (n)', 'S_one.TODO = [FIBER_ENTER n pnamedargs, FIBER_FINISH n]',
            'pnamedargs.SLOTS = eps', 'pnamedargs.NAMED = eps',
            '$fiber_enter_valid(S_one[.COMPLETION = NORMAL], n, pnamedargs)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("FiberCallableChild322B"), OUTPUT $ptascii("|"), OUTPUT $ptascii("9")]',
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
