#!/usr/bin/env python3
"""FINAL match errors read the current quiet private scalar CV."""
from pathlib import Path
import function_scope as scope
import output_final_match_error_sources as prior

SCAN = prior.MISSING.replace(b"        return match (1) { 2 => 'H' };",
                            b"        $s = 3;\n        return match ($s) { 2 => 'H' };")
TABLE = SCAN.replace(b"$s = 3", b"$s = 'bad'").replace(b"2 => 'H'", b"1 => 'H', 2 => 'I'")
BOOL = SCAN.replace(b"$s = 3", b"$s = false")
NULL = SCAN.replace(b"$s = 3", b"$s = null")
FLOAT = SCAN.replace(b"$s = 3", b"$s = 1.5")
MUTATE = SCAN.replace(b"2 => 'H'", b"($s = 4) + 1 => 'H'")
NORMAL = SCAN.replace(b"$s = 3", b"$s = 2")
REFERENCE = SCAN.replace(b"$s = 3;", b"$r = 3; $s = &$r;")
UNDEFINED = SCAN.replace(b"        $s = 3;\n", b"")
CATCH = SCAN.replace(b"        return match ($s) { 2 => 'H' };",
                     b"        try { return match ($s) { 2 => 'H' }; } catch (UnhandledMatchError) { return 'H'; }")
OVERRIDE = SCAN.replace(b"        return match ($s) { 2 => 'H' };",
                        b"        try { return match ($s) { 2 => 'H' }; } finally { return 'H'; }")
CASES = {'native-cv-match-scan': SCAN, 'native-cv-match-table-string': TABLE,
         'native-cv-match-bool': BOOL, 'native-cv-match-null': NULL,
         'native-cv-match-float': FLOAT, 'native-cv-match-mutated': MUTATE,
         'native-cv-match-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-cv-match-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
