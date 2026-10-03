#!/usr/bin/env python3
"""Source-derived parameter reception, callable identity and alias cleanup."""
from pathlib import Path
import json

import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/callable_string_cases.json'
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())}
STAGE = 'S.TODO = [TYPE_RECEIVE porigin_function 0]'
GUARDS = ['$call_descriptors_valid(S)', '$class_state_valid(S)',
          '$closure_state_valid(S)', '$heap_valid($heap_graph(S))']
RECEIVE = [
    '$function_at($all_functions(S), porigin_function) = (pfunction)',
    'pfunction.SIGNATURE.PARAMETERS[0].NAME = $ptascii("value")',
    '"callable" <- $ptmasks(pfunction.SIGNATURE.PARAMETERS[0].TYPE)',
    '"string" <- $ptmasks(pfunction.SIGNATURE.PARAMETERS[0].TYPE)',
    '$lookup(S.ENV, $ptascii("value")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (POBJECT n_receiver)',
    'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    *GUARDS,
    '~$call_descriptors_valid(S[.TODO = [TYPE_RECEIVE (PORIGIN 999 eps) 0]])',
    '~$call_descriptors_valid(S[.TODO = [TYPE_RECEIVE porigin_function 99]])',
    '~$call_descriptors_valid(S[.TODO = [TYPE_RECEIVE porigin_function 0, DISCARD]])',
]
ADMITTED = [
    '$stringable_instance(S, n_receiver)',
    '$typed_callable(S, POBJECT n_receiver) = (true)',
    '~$typed_object_exact(S, pfunction.SIGNATURE.PARAMETERS[0].TYPE, POBJECT n_receiver)',
    '~$user_string_coercion(S, pfunction.SIGNATURE.PARAMETERS[0].TYPE, POBJECT n_receiver, $typed_caller_strict(S))',
    '$typed_parameter_conversion(S, pfunction.SIGNATURE.PARAMETERS[0], POBJECT n_receiver) = TYPEVALUE (POBJECT n_receiver)',
    'PhpStep: S ~> S_one',
    'S_one.COMPLETION = NORMAL',
    'S_one.STORE[n_value_cell] = DEFINED (POBJECT n_receiver)',
    'S_one.EVENTS = S.EVENTS',
    'S_one.ALLOCATIONS = S.ALLOCATIONS',
    'S_one.CURRENT = S.CURRENT',
    '$call_descriptors_valid(S_one)', '$class_state_valid(S_one)',
    '$closure_state_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_done = $drive(S_one, 1000)',
    'S_done.COMPLETION = NORMAL',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'weak-dual-receive-identity': {
        'source': SOURCES['weak-dual-value-identity'], 'stage': STAGE,
        'checks': [*RECEIVE, '~$typed_caller_strict(S)', *ADMITTED,
                   'S_done.EVENTS = [OUTPUT $ptascii("Task"), OUTPUT $ptascii("I")]',
                   '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)'],
    },
    'strict-reversed-receive-identity': {
        'source': SOURCES['strict-reversed-union'], 'stage': STAGE,
        'checks': [*RECEIVE, '$typed_caller_strict(S)', *ADMITTED,
                   'S_done.EVENTS = [OUTPUT $ptascii("I")]',
                   '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)'],
    },
    'inherited-receive-owner': {
        'source': SOURCES['inherited-dual-callable'], 'stage': STAGE,
        'checks': [
            *RECEIVE, '~$typed_caller_strict(S)',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'pmethoddesc.OWNER =/= porigin_class',
            '$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("Owner")',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc_child)',
            'pclassdesc_child.NAME = $ptascii("Child")',
            *ADMITTED,
            'S_done.EVENTS = [OUTPUT $ptascii("Owner"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Child")]',
        ],
    },
    'reference-receive-alias-cleanup': {
        'source': SOURCES['typed-reference-alias-preserved'], 'stage': STAGE,
        'checks': [
            *RECEIVE, '~$typed_caller_strict(S)',
            'pfunction.SIGNATURE.PARAMETERS[0].BYREF',
            '~$typed_parameter_source(S, pfunction.SIGNATURE.PARAMETERS[0])',
            'S.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("alias")) = (n_value_cell)',
            '$lookup(psymboltable.ENV, $ptascii("object")) = (n_value_cell)',
            *ADMITTED,
            'S_done.EVENTS = [OUTPUT $ptascii("I"), OUTPUT $ptascii("N")]',
            '$lookup(S_done.ENV, $ptascii("object")) = (n_original_cell)',
            'S_done.STORE[n_original_cell] = DEFINED PNULL',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'unpacked-receive-retained-array-owner': {
        'source': SOURCES['unpacked-owned-dual-value'], 'stage': STAGE,
        'checks': [
            *RECEIVE, '~$typed_caller_strict(S)', *ADMITTED,
            'S_done.EVENTS = [OUTPUT $ptascii("I")]',
            '(HOBJECT n_receiver) <- S_done.ALLOCATIONS',
            '$lookup(S_done.ENV, $ptascii("arguments")) = (n_arguments_cell)',
            'S_done.STORE[n_arguments_cell] = DEFINED (PARRAY n_container)',
            '$entry_lookup(S_done.ARRAYS[n_container].ITEMS, KINT 0) = (pitem_receiver)',
            '$entry_value(S_done, pitem_receiver) = POBJECT n_receiver',
        ],
    },
    'strict-noncallable-direct-receive-error': {
        'source': SOURCES['strict-noncallable-stringable'], 'stage': STAGE,
        'checks': [
            *RECEIVE, '$typed_caller_strict(S)',
            '$stringable_instance(S, n_receiver)',
            '$typed_callable(S, POBJECT n_receiver) = (false)',
            '$typed_parameter_conversion(S, pfunction.SIGNATURE.PARAMETERS[0], POBJECT n_receiver) = TYPEREJECT',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = THROWN "TypeError" n_message* z_error',
            '$(z_error > 0)',
            'S_one.STORE = S.STORE',
            'S_one.EVENTS = S.EVENTS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_valid($heap_graph(S_one))',
        ],
    },
}


def run(cases=None):
    protocol.run(CASES if cases is None else cases,
                 extra_inputs=(Path(__file__), CATALOGUE))


if __name__ == '__main__':
    run()
