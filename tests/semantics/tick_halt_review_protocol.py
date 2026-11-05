#!/usr/bin/env python3
"""Reach the real Halt Tick before its offset-reading callback aborts."""
import argparse
import json

import fiber_state_review as review
import tick_halt_review_cases as sources


def ascii_text(value):
    return '$ptascii(' + json.dumps(value) + ')'


def output(*chunks):
    return '[' + ', '.join('OUTPUT ' + ascii_text(chunk) for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'split-halt-marker-has-offset-before-callback-abort-and-shutdown': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if $origin_node(S.SOURCES, porigin) = (NStmtHaltCompiler phpType33 metadata) -- if S.EVENTS = eps',
        'checks': [
            'porigin = PORIGIN 0 pcpath', 'pcpath = [PCINDEX 7]',
            '$source_unit(S.SOURCES, 0) = (pcunit)',
            '$origin_node(S.SOURCES, porigin) = (statement)',
            'statement = NStmtHaltCompiler (BYTES text_payload) metadata',
            '$pphalt_valid(pcunit, pcpath, statement)',
            '$pphalt_offset(pcunit.AST) = (' + str(sources.OFFSET) + ')',
            '|$pcprogram(pcunit.AST)| = 8',
            '$source_line(metadata) = 16', '$source_end_line(metadata) = 19',
            '$base64(text_payload) = ' + ascii_text("\n<?php echo 'BAD-PAYLOAD'; ?>\n"),
            'S.ORIGIN = (porigin)',
            'ptask_tail* = (ORIGIN_RETURN porigin_saved?) :: ptask_after*',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 19',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            'S.TICKCOUNT = 0', '|S.TICKENTRIES| = 1',
            '$dynamic_halt_lookup(S, $call_sourcefile(S.FILES, porigin), S.DECLARATIONS) = HALT_OFFSET ' + str(sources.OFFSET),
            *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_next = $drive_steps(S, 1)', 'S_next.TICKCOUNT = 0',
            'S_next.TODO = (TICK_NEXT ptickdispatch) :: ptask_next*',
            'ptickdispatch.SITE = porigin', 'ptickdispatch.MARKER = ptickmarker',
            'ptickdispatch.CURSOR = 0', 'ptickdispatch.ENTRY = eps', *valid('S_next'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            '$drive(S_next[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
            'S_done.TICKCOUNT = 0', *valid('S_done'),
            'S_done.EVENTS = ' + output('T', '19', ':', str(sources.OFFSET), 'C', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
