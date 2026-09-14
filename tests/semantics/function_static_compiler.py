#!/usr/bin/env python3
"""Named-function static declaration phases, stored mode, CV scope and emitted lines."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/function_static_compiler_cases.json').read_text())


CONTEXTS = {'static-counter': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX '
                    '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                    '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                    '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) '
                    '=/= eps',
                    '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                    '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX 0,PCFIELD '
                    '5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]'],
 'static-null-cached': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 1,PCFIELD 5,PCINDEX '
                        '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                        '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                        '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                        '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                        '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]'],
 'static-comma-order': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 1,PCFIELD 5,PCINDEX '
                        '0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 false,PPCSTATIC ([PCINDEX 1,PCFIELD 5,PCINDEX '
                        '0,PCFIELD 0,PCINDEX 1]) ([98]) 1 1 false]',
                        '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                        '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 1,PCFIELD 0]) = eps',
                        '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                        '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                        '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 false,CODESTATIC ([PCINDEX '
                        '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 1]) ([98]) 1 1 false]'],
 'static-parameter-prior-value': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD '
                                  '5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                  '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                                  '0]) = eps',
                                  '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                                  '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                  '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]'],
 'static-local-prior-value': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD '
                              '5,PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                              '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = '
                              'eps',
                              '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                              '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                              '0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]'],
 'static-unset-local': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX '
                        '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                        '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                        '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                        '1]) =/= eps',
                        '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                        '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                        '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]'],
 'static-rebind-local': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX '
                         '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                         '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                         '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                         '1]) =/= eps',
                         '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                         '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                         '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]'],
 'static-multiline-undefined-constant': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                         '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 3 4 false]',
                                         '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                         '0,PCFIELD 0]) = eps',
                                         '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                         '(pfunction_0)',
                                         '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                         '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 3 4 '
                                         'false]'],
 'static-namespace-constant': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD '
                               '1,PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                               '$ppaccess(P, [PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD '
                               '0,PCINDEX 0,PCFIELD 0]) = eps',
                               '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0,PCFIELD 1,PCINDEX 1])) = '
                               '(pfunction_0)',
                               '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                               '0,PCFIELD 1,PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                               'false]'],
 'static-skipped-then-entered': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 1,PCFIELD '
                                 '5,PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                 '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD '
                                 '0,PCINDEX 0,PCFIELD 0]) = eps',
                                 '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                                 '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                                 '1,PCFIELD 5,PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 '
                                 '1 false]'],
 'static-folded-conditional-skips-invalid': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                             '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 0]) = eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                             '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                             '(pfunction_0)',
                                             '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0]) ([120]) 1 1 true]'],
 'static-folded-conditional-effect-once': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                           '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                           '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 0]) = eps',
                                           '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = '
                                           '(pfunction_0)',
                                           '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                           '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 '
                                           '1 false]',
                                           '(CODEREDIRECT ([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 1]) ([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 1,PCFIELD 1]) false) <- pfunction_0.CODE.REDIRECTS',
                                           '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 1,PCFIELD 2]) = eps'],
 'static-suppressed-literal-initializer': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                           '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                           '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 0]) = eps',
                                           '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                           '(pfunction_0)',
                                           '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                           '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 '
                                           '1 false]',
                                           '$code_expression(pfunction_0.CODE.EXPRESSIONS, [PCINDEX '
                                           '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = ((1, '
                                           'true))'],
 'static-nested-function-name-isolation': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                           '0,PCFIELD 5,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) '
                                           '([120]) 1 1 true,PPCSTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX '
                                           '1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                           '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 5,PCINDEX '
                                           '0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                                           '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                           '5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                           '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX '
                                           '0,PCFIELD 0]) = eps',
                                           '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD '
                                           '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                           '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                           '5,PCINDEX 0])) = (pfunction_0)',
                                           '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                           '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                           '0,PCINDEX 0]) ([120]) 1 1 true]',
                                           '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                           '(pfunction_1)',
                                           '$fixture_static_code(pfunction_1.CODE.EXPRESSIONS) = [CODESTATIC '
                                           '([PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([120]) 1 '
                                           '1 true]'],
 'static-bare-null-returned-alias': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                     '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                     '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                     '0,PCFIELD 0]) = eps',
                                     '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                     '0,PCFIELD 1]) = eps',
                                     '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                                     '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                     '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                                     'true]'],
 'static-reentry-inner-wins': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 0,PCFIELD '
                               '5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                               '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) '
                               '= eps',
                               '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                               '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC ([PCINDEX '
                               '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]'],
 'static-reentry-array-shared-alias': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                       '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 0]) = eps',
                                       '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                                       '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                       '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                                       'false]'],
 'static-binding-releases-prior-reference': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                             '0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 0]) = eps',
                                             '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                             '(pfunction_0)',
                                             '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX '
                                             '0]) ([120]) 1 1 false]'],
 'static-autoglobal-hidden-local-cv': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                       '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([95,71,69,84]) 2 2 '
                                       'true]',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 0]) = eps',
                                       '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD '
                                       '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                       '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                                       '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                       '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) '
                                       '([95,71,69,84]) 2 2 true]',
                                       'pfunction_0.CVS = [([95,71,69,84]),([110])]'],
 'static-globals-hidden-local-cv': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX 1,PCFIELD '
                                    '5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([71,76,79,66,65,76,83]) 2 2 true]',
                                    '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                                    '0]) = eps',
                                    '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                    '0,PCFIELD 1]) =/= eps',
                                    '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                                    '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                    '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) '
                                    '([71,76,79,66,65,76,83]) 2 2 true]',
                                    'pfunction_0.CVS = [([71,76,79,66,65,76,83]),([110])]'],
 'static-stored-array-null-distinct-cells': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                             '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 '
                                             'true,PPCSTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 1]) ([110]) 1 1 true,PPCSTATIC ([PCINDEX 1,PCFIELD '
                                             '5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 true]',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 0]) = eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '1,PCFIELD 0]) = eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 1,PCFIELD 1]) =/= eps',
                                             '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 0]) = eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                             '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = '
                                             '(pfunction_0)',
                                             '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0]) ([97]) 1 1 true,CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX '
                                             '0,PCFIELD 0,PCINDEX 1]) ([110]) 1 1 true]',
                                             '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = '
                                             '(pfunction_1)',
                                             '$fixture_static_code(pfunction_1.CODE.EXPRESSIONS) = '
                                             '[CODESTATIC ([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0]) ([97]) 1 1 true]'],
 'static-dynamic-array-element-once': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                       '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 false]',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 0]) = eps',
                                       '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 1])) = (pfunction_0)',
                                       '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                       '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([97]) 1 1 '
                                       'false]'],
 'static-bare-cv-current-parameter': ['$fixture_static_records(P.EXPRESSIONS) = [PPCSTATIC ([PCINDEX '
                                      '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                      '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                      '0,PCFIELD 0]) = eps',
                                      '$function_at(P.FUNCTIONS, PORIGIN 91 ([PCINDEX 0])) = (pfunction_0)',
                                      '$fixture_static_code(pfunction_0.CODE.EXPRESSIONS) = [CODESTATIC '
                                      '([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                                      'false]',
                                      '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                      '0,PCFIELD 1]) = (PPR)',
                                      '$code_expression(pfunction_0.CODE.EXPRESSIONS, [PCINDEX 0,PCFIELD '
                                      '5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = ((1, false))',
                                      'pfunction_0.CVS = [([120])]',
                                      '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                      '0,PCINDEX 0,PCFIELD 1]) = eps']}
PENDING = {"static-undefined-initializer-retry-dependency": "ordinary statement compilation"}
EXTRA = '\ndec $fixture_static_record(ppexprdone) : bool\ndef $fixture_static_record(PPCSTATIC pcpath ptbytes n_begin n_bind b) = true\ndef $fixture_static_record(ppexprdone) = false -- otherwise\ndec $fixture_static_records(ppexprdone*) : ppexprdone*\ndef $fixture_static_records(eps) = eps\ndef $fixture_static_records((PPCSTATIC pcpath ptbytes n_begin n_bind b) :: ppexprdone*) = (PPCSTATIC pcpath ptbytes n_begin n_bind b) :: $fixture_static_records(ppexprdone*)\ndef $fixture_static_records(ppexprdone :: ppexprdone_tail*) = $fixture_static_records(ppexprdone_tail*)\n  -- if ~$fixture_static_record(ppexprdone)\ndec $fixture_static_code_record(pcodeexpr) : bool\ndef $fixture_static_code_record(CODESTATIC pcpath ptbytes z_begin z_bind b) = true\ndef $fixture_static_code_record(pcodeexpr) = false -- otherwise\ndec $fixture_static_code(pcodeexpr*) : pcodeexpr*\ndef $fixture_static_code(eps) = eps\ndef $fixture_static_code((CODESTATIC pcpath ptbytes z_begin z_bind b) :: pcodeexpr*) = (CODESTATIC pcpath ptbytes z_begin z_bind b) :: $fixture_static_code(pcodeexpr*)\ndef $fixture_static_code(pcodeexpr :: pcodeexpr_tail*) = $fixture_static_code(pcodeexpr_tail*)\n  -- if ~$fixture_static_code_record(pcodeexpr)\n'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/function_static_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='function-static-compiler-', dir=ROOT / '.tools'))
    print(out, flush=True)

    def run(command, label):
        (out / (label + '.command.json')).write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=60)
        except subprocess.TimeoutExpired as error:
            (out / (label + '.stdout')).write_bytes(error.stdout or b'')
            (out / (label + '.stderr')).write_bytes(error.stderr or b'')
            (out / (label + '.status.json')).write_text(json.dumps({'status': 'timeout'}))
            raise
        (out / (label + '.stdout')).write_bytes(result.stdout)
        (out / (label + '.stderr')).write_bytes(result.stderr)
        (out / (label + '.status.json')).write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        return result

    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(adapter_path), str(ROOT)], out / 'adapter-wire')
    records, assertions = [], []
    try:
        for index, (name, source) in enumerate(CASES.items()):
            file = out / (name + '.php')
            file.write_bytes(source.encode())
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            native = run([str(types.PHP), '-n', *types.FLAGS, '-l', str(file)], name)
            assert native.returncode in (0, 255), native
            events = context.events(native)
            record = {'name': name, 'source_base64': base64.b64encode(source.encode()).decode(),
                      'checked': checked, 'lint_exit': native.returncode, 'events': events}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            body = f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            if name not in PENDING:
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name in PENDING:
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')\n'
            elif native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n'
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
            assertions.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n' + body)
            (out / (name + '.state.watsup')).write_text(f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + EXTRA + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Named-function statics compiler phases, pre-evaluation stored mode, source declaration/CV scope and separate initializer/bind lines; runtime persistent-cell ownership is separately paired.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/function-static-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
