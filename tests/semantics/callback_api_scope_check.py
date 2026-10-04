#!/usr/bin/env python3
"""The retired selecting method retains its genuine inherited called scope."""
import json
from pathlib import Path

import shutdown_state_review as runner

rows = json.loads(Path(__file__).with_name('callback_api_review_cases.json').read_text())
source = next(row['source'] for row in rows
              if row['id'] == 'shutdown-keyword-parent-self-static-called')
runner.CASES = {
    'retired-inherited-method-called-scope': {
        'source': source,
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            '|S.SHUTDOWN.ENTRIES| = 3',
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.TARGET = API_METHOD_TARGET papiquery porigin_handler ptbytes true',
            'pshutdownentry.CAPTURE = (pmethodcapture)',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_lexical)',
            '$class_named(S.CLASSNAMES, $ptascii("d")) = (porigin_called)',
            '$effective_method(S, porigin_lexical, $ptascii("reg"), |S.CLASSES|) = (pmethoddesc)',
            '$effective_method(S, porigin_called, $ptascii("h"), |S.CLASSES|) = (pmethoddesc_other)',
            'pmethodcapture.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
            'pmethodcapture.LEXICAL_CLASS = (porigin_lexical)',
            'pmethodcapture.CALLED_CLASS = (porigin_called)',
            'pmethodcapture.CALLSITE = (porigin_call)',
            'papiquery.SCOPE = (porigin_lexical)',
            'papiquery.CALLED = (porigin_called)', 'papiquery.THIS = eps',
            'papiquery.CLASS.CALLED = porigin_called',
            '$consumer_capture_valid(S, pshutdownentry.CALL.SITE, pshutdownentry.CAPTURE)',
            '$consumer_shutdown_scope(S, papiquery, pshutdownentry)',
            '$api_carrier_valid(S, papiquery, porigin_handler, ptbytes, true)',
            '$shutdown_entry_valid(S, pshutdownentry)',
            '~$consumer_capture_valid(S, pshutdownentry.CALL.SITE, eps)',
            '~$consumer_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.CALLED_CLASS = (porigin_lexical)]))',
            '~$consumer_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.LEXICAL_CLASS = (porigin_called)]))',
            '~$consumer_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN]))',
            '~$consumer_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.CALLSITE = (pshutdownentry.CALL.SITE)]))',
            '~$consumer_shutdown_scope(S, papiquery[.CALLED = (porigin_lexical)], pshutdownentry)',
            '~$consumer_shutdown_scope(S, papiquery[.SCOPE = (porigin_called)], pshutdownentry)',
            '~$consumer_shutdown_scope(S, papiquery[.THIS = (|S.OBJECTS|)], pshutdownentry)',
            '~$shutdown_entry_valid(S, pshutdownentry[.CAPTURE = eps])',
            '$call_task_valid(S, SHUTDOWN_SEND 0 0 eps)',
            *runner.VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN',
            'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL', *runner.DONE,
            '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if runner.run([]) else 1)
