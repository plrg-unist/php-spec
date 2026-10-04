#!/usr/bin/env python3
"""The retired selecting method retains its genuine inherited called scope."""

import shutdown_state_review as runner

source = '<?php class C{static function reg(){register_shutdown_function(["self","h"]);}private static function h(){}}class D extends C{static function other(){}}error_reporting(0);D::reg();'
runner.CASES = {
    'retired-inherited-method-called-scope': {
        'source': source,
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            '|S.SHUTDOWN.ENTRIES| = 1',
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.TARGET = API_METHOD_TARGET papiquery porigin_handler ptbytes true',
            'pshutdownentry.CAPTURE = (pmethodcapture)',
            'pshutdownentry.PRODUCER = (pshutdownproducer)',
            '~pshutdownproducer.INTERNAL',
            'pshutdownproducer.SCOPE = eps /\\ pshutdownproducer.BINDING = eps',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_lexical)',
            '$class_named(S.CLASSNAMES, $ptascii("d")) = (porigin_called)',
            '$effective_method(S, porigin_lexical, $ptascii("reg"), |S.CLASSES|) = (pmethoddesc)',
            '$effective_method(S, porigin_called, $ptascii("other"), |S.CLASSES|) = (pmethoddesc_other)',
            'pmethodcapture.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
            '$target_function(S, pshutdownproducer.TARGET) = (pmethoddesc.FUNCTION)',
            '$target_called_class(S, pshutdownproducer.TARGET) = (porigin_called)',
            'pmethodcapture.LEXICAL_CLASS = (porigin_lexical)',
            'pmethodcapture.CALLED_CLASS = (porigin_called)',
            'pmethodcapture.CALLSITE = (porigin_call)',
            'pshutdownproducer.SITE = (porigin_call)',
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
            '~$shutdown_entry_valid(S, pshutdownentry[.PRODUCER = eps])',
            '~$shutdown_entry_valid(S, pshutdownentry[.PRODUCER = (pshutdownproducer[.INTERNAL = true])])',
            '~$shutdown_entry_valid(S, pshutdownentry[.PRODUCER = (pshutdownproducer[.SITE = eps])])',
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
