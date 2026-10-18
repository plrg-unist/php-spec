#!/usr/bin/env python3
"""Validate the consumed buffer receipt inside its real payload destructor."""
from pathlib import Path

import generator_buffered_throw_state as author

CATALOG = author.CATALOG
INPUTS = [*author.INPUTS, Path(__file__)]
CASES = {
    'buffered-throw-receipt-remains-valid-inside-payload-destructor': {
        'source': author.ROWS[author.DIRECT]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_payload) '
                  '-- if $object_name(S, n_payload) = $ptascii("BufferedThrowPayload20") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)]) '
                  '-- if pgeneratorop.NAME = "throw"'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.GENERATORINPUTS = eps',
            'pdestructorcall.OBJECT = n_payload',
            'pdestructorcall.CALLER = pframe_caller.CONTEXT',
            'pdestructionoperation.CALLER = pframe_caller.CONTEXT',
            'pdestructionoperation.CALLER =/= S.CURRENT',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructorcall.PENDING = (n_exception)',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_payload), PENDING false})',
            'pdestructionoperation.CLEANUP = eps',
            'pdestructionoperation.ORIGIN = (porigin_yield)',
            'pframe_caller.ORIGIN = (porigin_yield)',
            'pgeneratorop.LINE = 8', 'pgeneratorop.ARGUMENTS = eps',
            'n_child = pgeneratorop.OBJECT',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_RUNNING',
            'pgenerator_child.FRAME = eps', 'pgenerator_child.VALUE = (PINT 5)',
            'pgenerator_child.DELEGATE = eps', '~pgenerator_child.PENDING_INIT',
            '$generator_input_site(S, n_child, porigin_yield)',
            '~$generator_input_throw_here(S, pdestructionoperation)',
            '$generator_input_throw_frames(S, pdestructionoperation, S.FRAMES)',
            '$generator_input_throw_receipt(S, pdestructionoperation)',
            'S_caller = $constant_frame_scope(S, pframe_caller, pframe_tail*)',
            '$generator_input_throw_here(S_caller, pdestructionoperation)',
            '$generator_input_throw_tail(S_caller, pdestructionoperation, pframe_caller.TODO)',
            '$destructor_operation_live(S, pdestructionoperation)',
            '~$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_context_valid(S, pcallcontext)',
            '$gc_operation_metadata_valid(S, pdestructionoperation)',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            '$heap_count(HOBJECT n_payload, $generator_inputs_nodes(S.GENERATORINPUTS)) = 0',
            '~$generator_input_throw_receipt(S, pdestructionoperation[.CALLER = S.CURRENT])',
            '~$gc_operation_metadata_valid(S, pdestructionoperation[.ORIGIN = eps])',
            '~$generator_input_throw_receipt(S, pdestructionoperation[.SOURCE = GENERATOR_ARGS pgeneratorop[.LINE = 0] eps ([KNOWN (POBJECT n_exception)])])',
            'S.EVENTS = ' + author.outputs(author.EVENTS[author.DIRECT][:11]),
            *author.VALID, *author.BUDGET,
            '$generator_input_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            'S_one.GENERATORINPUTS = eps',
            *author.DONE,
            'S_done.EVENTS = ' + author.outputs(author.EVENTS[author.DIRECT]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


if __name__ == '__main__':
    author.CASES = CASES
    author.INPUTS = INPUTS
    raise SystemExit(0 if author.run(None) else 1)
