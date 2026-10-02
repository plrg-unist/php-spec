#!/usr/bin/env python3
"""Default static-method scope and a rebound outer's actual inner receiver."""
from pathlib import Path
import json

import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/closure_static_owner_cases.json'
SOURCE = json.loads(CATALOGUE.read_text())[-1]['source']
CASES = {
    'static-method-default-scope': {
        'source': SOURCE,
        'stage': ('S.TODO = (BIND_ARGS pbindcall) :: ptask_tail* '
                  '-- if pbindcall.KIND = INSTANCE_BIND -- if pbindcall.INDEX = 0'),
        'checks': [
            'pbindcall.SOURCE = (n_original)',
            'S.OBJECTS[n_original] = REALCLOSURE porigin_template pitem* pstaticcell*',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction)',
            '~$closure_static(S, pfunction)',
            '$closure_nearest_owner(S, $closure_creation_owners($all_functions(S), porigin_template), eps) = (porigin_owner)',
            '$class_method_origin(S.CLASSES, porigin_owner) = (pmethoddesc)',
            'pmethoddesc.STATIC',
            '$closure_static_method_owner(S, porigin_template)',
            '~$closure_receiver_forbidden(S, porigin_template)',
            '$closure_scope_at(S.CLOSURESCOPES, n_original) = (pclosurescope)',
            'S.CLOSURESCOPES = [pclosurescope]',
            'pclosurescope.LEXICAL = pmethoddesc.OWNER',
            'pclosurescope.CALLED = pmethoddesc.OWNER',
            'pclosurescope.RECEIVER = eps',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE pclosurescope.CALLED',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$node_children(S, HOBJECT n_original) = eps',
            '$closure_scope_row_valid(S, pclosurescope)',
            '$closure_callable(S, n_original)',
            '$call_task_valid(S, BIND_ARGS pbindcall)',
            '$closure_state_valid(S)', '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'pclosurescope_bad = pclosurescope[.RECEIVER = (n_receiver)]',
            'S_bad = S[.CLOSURESCOPES = [pclosurescope_bad]]',
            '$heap_valid($heap_graph(S_bad))',
            '~$closure_scope_row_valid(S, pclosurescope_bad)',
            '~$closure_state_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
            '~$closure_static_method_owner(S, porigin_owner)',
        ],
    },
    'rebound-outer-inner-receiver': {
        'source': SOURCE,
        'stage': ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_inner) phpType7* n_arg '
                  'poperand* porigin_site? z) :: ptask_tail* '
                  '-- if $closure_scope_at(S.CLOSURESCOPES, n_inner) = (pclosurescope)'),
        'checks': [
            'S.OBJECTS[n_inner] = REALCLOSURE porigin_template pitem* pstaticcell*',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction)',
            '~$closure_static(S, pfunction)',
            '$closure_nearest_owner(S, $closure_creation_owners($all_functions(S), porigin_template), eps) = (porigin_outer)',
            '$function_at(S.CLOSURETEMPLATES, porigin_outer) = (pfunction_outer)',
            '$closure_static_method_owner(S, porigin_outer)',
            '~$closure_static_method_owner(S, porigin_template)',
            '~$closure_receiver_forbidden(S, porigin_template)',
            'pclosurescope.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE pclosurescope.CALLED',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$node_children(S, HOBJECT n_inner) = [HOBJECT n_receiver]',
            '$target_receiver(S, CLOSURE_TARGET n_inner) = (n_receiver)',
            '$closure_binding_at(S.CLOSUREBINDINGS, n_inner) = eps',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("bound")) = (n_cell_bound)',
            'S.STORE[n_cell_bound] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("c")) = (n_cell_c)',
            'S.STORE[n_cell_c] = DEFINED PNULL',
            '$closure_scope_row_valid(S, pclosurescope)',
            '$closure_callable(S, n_inner)',
            '$call_task_valid(S, CALL_ARGS (CLOSURE_TARGET n_inner) phpType7* n_arg poperand* porigin_site? z)',
            '$closure_state_valid(S)', '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$closure_scope_row_valid(S, pclosurescope[.RECEIVER = eps])',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE,
                        ROOT / 'tests/semantics/profile.json', ROOT / '.tools/request-clock.so'))
