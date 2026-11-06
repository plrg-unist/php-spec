#!/usr/bin/env python3
"""Normal Array/Object conversion during the null-C FINAL drain."""
from pathlib import Path
import output_result_cleanup_sources as runner
ROOT = runner.ROOT
CASES = {'final-array-warning-null-c': (b"<?php echo 'P';$phase=0;set_error_handler(function($n,$m,$f,$l){retu"
                                b"rn $n===2&&$m==='Array to string conversion'&&$f==='Unknown'&&$l===0"
                                b"&&$GLOBALS['phase']===9;});function h($b,$p){$GLOBALS['phase']=$p;re"
                                b"turn [];}ob_start('h');echo 'A';",
                                b'PArray'),
 'final-object-cast-release': (b"<?php echo 'P';$phase=0;class T{function __toString(){global $phase;"
                               b"$f=ob_get_status()['flags'];$b=ob_get_contents();echo 'S';return"
                               b' "H$phase:$f:$b";}function __destruct(){echo \'D\';}}function h($b,$p)'
                               b"{$GLOBALS['phase']=$p;return new T;}ob_start('h');echo 'A';",
                               b'PH9:113:A')}
STDERR = {}
CONTROLS = {
    'pending-final-object': b"<?php echo 'P';class T{function __toString(){throw new Exception('E');}}function h($b,$p){return new T;}ob_start('h');echo 'A';",
}
CONTROL_REASONS = {'pending-final-object': 'pending FINAL Array/Object return conversion'}
_original_fingerprint = runner.fingerprint

def fingerprint():
    inputs = _original_fingerprint()
    inputs['tests/semantics/output_final_conversion_sources.py'] = runner.common.sha(Path(__file__))
    return inputs

if __name__ == '__main__':
    runner.CASES = CASES
    runner.STDERR = STDERR
    runner.CONTROLS = CONTROLS
    runner.CONTROL_REASONS = CONTROL_REASONS
    runner.fingerprint = fingerprint
    runner.main()
