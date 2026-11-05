#!/usr/bin/env python3
"""Reach the eval import Tick using a counter primed by the parent unit."""
import argparse
import json

import fiber_state_review as review
import tick_import_review_cases as sources


def ascii_text(value):
    return '$ptascii(' + json.dumps(value) + ')'


def output(*chunks):
    return '[' + ', '.join('OUTPUT ' + ascii_text(chunk) for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'eval-import-tick-shares-counter-and-aborts-before-the-pending-class': {
        'source': sources.CASES['review-eval-namespace-import-shares-counter-and-aborts-pending-class'][0].decode(),
        'eval_sources': [(1, b'''namespace Dyn47;
interface Ready47 {}
class Trigger47 { public const VALUE=7; public function unused(){declare(ticks=2);} }
use Exception as Imported47;
class Pending47 implements Ready47 { public const VALUE=9; }
echo "BAD";''')],
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if porigin = PORIGIN n_unit pcpath -- if $(n_unit > 0) -- if $origin_node(S.SOURCES, porigin) = (NStmtUse phpType24 phpType51 metadata) -- if S.EVENTS = eps',
        'checks': [
            'porigin = PORIGIN n_unit pcpath', '$(n_unit > 0)',
            'pcpath = [PCINDEX 0, PCFIELD 1, PCINDEX 2]',
            '$eval_context_at(S.EVALCONTEXTS, n_unit) = (pevalcontext)',
            'pevalcontext.PHASE = UNIT_RUN',
            '$origin_node(S.SOURCES, pevalcontext.SITE) = (NExprEval (NScalarString phpType33 metadata_code) metadata_eval)',
            'porigin_namespace = PORIGIN n_unit ([PCINDEX 0])',
            '$tick_marker(S, porigin_namespace) = eps',
            'porigin_trigger = PORIGIN n_unit ([PCINDEX 0, PCFIELD 1, PCINDEX 1])',
            'porigin_pending = PORIGIN n_unit ([PCINDEX 0, PCFIELD 1, PCINDEX 3])',
            '$origin_node(S.SOURCES, porigin_pending) = (statement_pending)',
            'ptask_tail* = (ORIGIN_RETURN porigin_saved?) :: (AT porigin_pending (STMT statement_pending)) :: ptask_after*',
            '$class_named(S.CLASSNAMES, ' + ascii_text(r'dyn47\trigger47') + ') = (porigin_trigger)',
            '$class_named(S.CLASSNAMES, ' + ascii_text(r'dyn47\pending47') + ') = eps',
            '$class_at(S.CLASSES, porigin_pending) = (pclassdesc_pending)',
            '~pclassdesc_pending.EARLY',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 4',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 1',
            '$lookup(S.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 0)', *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
            'S_done.EVALCONTEXTS = eps', *valid('S_done'),
            '$class_named(S_done.CLASSNAMES, ' + ascii_text(r'dyn47\trigger47') + ') = (porigin_trigger)',
            '$class_named(S_done.CLASSNAMES, ' + ascii_text(r'dyn47\pending47') + ') = eps',
            'S_done.STORE[n_count] = DEFINED (PINT 1)',
            'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('T', '7', 'N', 'C', 'N', '1', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
