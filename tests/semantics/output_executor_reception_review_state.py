#!/usr/bin/env python3
"""Independent received-argument and diagnostic checkpoints after deactivation."""
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
BASE = '''<?php
class LateProbeOB09 {
    public function __destruct() {
        echo "D1|";
        echo ob_start(...["flags" => -1, "chunk_size" => true]) ? "T|" : "F|";
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateProbeOB09);
    return "F" . $bytes;
});
echo "X|";
'''
HANDLED = BASE.replace('<?php\n', '<?php\nset_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });\n').replace(
    'ob_start(...["flags" => -1, "chunk_size" => true])',
    'ob_start(chunk_size: null, flags: 1.5)')
NONNULL = BASE.replace('ob_start(...["flags" => -1, "chunk_size" => true])',
                       'ob_start(42)')
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]
DONE = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.EVENTS = S.EVENTS /\\ S_zero.OUTPUTBUFFERS = eps /\\ S_zero.OUTPUTSEQ = 1',
    'S_done = $drive_steps(S, 1000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
    '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
]

review.CASES = {
    'omitted-callback-unpacked-receipt': {
        'source': BASE,
        'request_env': ENV,
        'stage': 'S.TODO = (OB_PARSE pconfigcall 3 pvalue_values*) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pvalue_values* = [PNULL, PINT 1, PINT $(-1)]',
            'pconfigcall.INDEX = 1 /\\ pconfigcall.NAMED',
            'pconfigcall.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN (PBOOL true)), NAMED_SENT (KNOWN (PINT $(-1)))]',
            'pconfigcall.PACKS = [pconfigpack]',
            'pconfigpack.INDEX = 0 /\\ pconfigpack.LINE = 5',
            '$config_invoke_valid(S, pconfigcall)',
            '$executor_default_start_valid(S, pconfigcall)',
            '$ob_parse_valid(S, pconfigcall, 3, pvalue_values*)',
            '$executor_boundary(S) = eps /\\ $output_guard(S) = S',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '~$config_invoke_valid(S, pconfigcall[.PACKS = eps])',
            '~$config_invoke_valid(S, pconfigcall[.PACKS = [pconfigpack[.INDEX = 1]]])',
            '~$config_invoke_valid(S, pconfigcall[.NAMED = false])',
            '~$config_invoke_valid(S, pconfigcall[.INDEX = 0])',
            '~$executor_default_start_valid(S, pconfigcall[.SENT = [NAMED_SENT (KNOWN (PINT 42)), NAMED_SENT (KNOWN (PBOOL true)), NAMED_SENT (KNOWN (PINT $(-1)))]])',
            '~$ob_parse_valid(S, pconfigcall, 3, [PNULL, PINT 0, PINT $(-1)])',
            '$call_descriptors_valid(S) /\\ $output_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'deprecations-before-selected-notice': {
        'source': HANDLED,
        'request_env': ENV,
        'stage': 'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = 6',
            'pobnotice.CALL.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN (PFLOAT 4609434218613702656))]',
            'pobnotice.CALL.NAMED /\\ pobnotice.CALL.PACKS = eps',
            '$ob_conversion(S, pobnotice.CALL, 1) = OB_DEPRECATED (PINT 0) n_message_chunk*',
            '$ob_conversion(S, pobnotice.CALL, 2) = OB_DEPRECATED (PINT 1) n_message_flags*',
            'pobnotice.VALUE = PBOOL false /\\ ~pobnotice.SECOND /\\ ~pobnotice.WRAPPER /\\ pobnotice.LEVEL = eps',
            '$executor_default_start_valid(S, pobnotice.CALL)',
            '$ob_notice_valid(S, pobnotice)',
            '~$ob_notice_valid(S, pobnotice[.OWNER = $(pobnotice.OWNER + 1)])',
            '~$ob_notice_valid(S, pobnotice[.VALUE = PBOOL true])',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.LINE = 5]])',
            '~$ob_notice_valid(S[.OUTPUTBLOCKED = true], pobnotice)',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $output_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'nonnull-callback-stops-after-reception': {
        'source': NONNULL,
        'request_env': ENV,
        'stage': 'S.TODO = (OB_PARSE pconfigcall 2 pvalue_values*) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pvalue_values* = [PINT 42, PINT 0]',
            '$ob_parse_valid(S, pconfigcall, 2, pvalue_values*)',
            '$executor_boundary(S) = eps',
            'PhpStep: S ~> S_parsed',
            'pvalue_done* = [PINT 42, PINT 0, PINT 112]',
            'S_parsed.TODO = (OB_PARSE pconfigcall 3 pvalue_done*) :: ptask_tail*',
            'S_parsed.COMPLETION = NORMAL',
            '$ob_parse_valid(S_parsed, pconfigcall, 3, pvalue_done*)',
            '$executor_boundary(S_parsed) = ("output-handler start after output deactivation")',
            'S_guarded = $output_guard(S_parsed)',
            'S_guarded.COMPLETION = UNSUPPORTED "output-handler start after output deactivation"',
            'S_guarded.TODO = S_parsed.TODO',
            'S_guarded.OUTPUTBUFFERS = eps /\\ S_guarded.OUTPUTSEQ = 1',
            'S_guarded.EVENTS = S.EVENTS',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=120) else 1)
