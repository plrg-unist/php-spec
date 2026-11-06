#!/usr/bin/env python3
"""Normal FINAL casts use the real null-C caller, without a registration frame."""
import output_object_conversion_review_sources as runner

ROOT = runner.ROOT
CASES = {
    'normal-final-cast-null-c-trace-no-extra-frame': (
        b'<?php echo "P";\nclass T{function __toString(){$t=(new Exception)->getTrace();$a=$t[0];return "H:".$a["function"].":".(isset($a["file"])?"F":"I").":".(isset($a["line"])?$a["line"]:-1).":".(isset($t[1])?"more":"1");}}\nfunction h($b,$p){return new T;}\nob_start("h");echo "A";\n',
        b'PH:__toString:I:-1:1'),
}
_original_fingerprint = runner.fingerprint


def fingerprint():
    inputs = _original_fingerprint()
    name = 'tests/semantics/output_final_conversion_review_sources.py'
    inputs[name] = runner.common.sha(ROOT / name)
    return inputs


if __name__ == '__main__':
    runner.CASES = CASES
    runner.SLOW_CASES = set()
    runner.fingerprint = fingerprint
    runner.main()
