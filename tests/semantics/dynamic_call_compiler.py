#!/usr/bin/env python3
"""Dynamic expression-call phases, emitted INIT markers and source modes."""
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
CASES = json.loads((ROOT / 'tests/semantics/dynamic_call_compiler_cases.json').read_text())


CONTEXTS = {'dynamic-case-leading-slash': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                                '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) = '
                                '(expression_0)',
                                '$ppcall_dynamic(expression_0) = true',
                                '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                'expression_0) = (UNPACK_VAR)'],
 'dynamic-runtime-name-namespace': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 1, PCINDEX 2, PCFIELD 0]) 1) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '(CODEEXPR ([PCINDEX 1, PCFIELD 1, PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 1, PCINDEX 2, '
                                    'PCFIELD 0, PCFIELD 0])) = (expression_0)',
                                    '$ppcall_dynamic(expression_0) = true',
                                    '$ppaccess(P, [PCINDEX 1, PCFIELD 1, PCINDEX 2, PCFIELD 0, PCFIELD 0]) = '
                                    '(PPR)',
                                    '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 1, PCINDEX '
                                    '2, PCFIELD 0], expression_0) = (UNPACK_VAR)',
                                    '(CODECALL_INIT ([PCINDEX 1, PCFIELD 1, PCINDEX 4, PCFIELD 0]) 1) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '(CODEEXPR ([PCINDEX 1, PCFIELD 1, PCINDEX 4, PCFIELD 0]) 1 false) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 1, PCINDEX 4, '
                                    'PCFIELD 0, PCFIELD 0])) = (expression_1)',
                                    '$ppcall_dynamic(expression_1) = true',
                                    '$ppaccess(P, [PCINDEX 1, PCFIELD 1, PCINDEX 4, PCFIELD 0, PCFIELD 0]) = '
                                    '(PPR)',
                                    '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 1, PCINDEX '
                                    '4, PCFIELD 0], expression_1) = (UNPACK_VAR)'],
 'dynamic-runtime-name-import-ignored': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                         '$ppfunction_code(P).EXPRESSIONS',
                                         '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                         '$ppfunction_code(P).EXPRESSIONS',
                                         '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, '
                                         'PCFIELD 0])) = (expression_0)',
                                         '$ppcall_dynamic(expression_0) = true',
                                         '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                         '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                         'expression_0) = (UNPACK_VAR)'],
 'dynamic-callee-before-arguments': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0]) 1) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '(CODEEXPR ([PCINDEX 3, PCFIELD 0]) 1 false) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, PCFIELD '
                                     '0])) = (expression_0)',
                                     '$ppcall_dynamic(expression_0) = true',
                                     '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                     '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0], '
                                     'expression_0) = (UNPACK_VAR)'],
 'dynamic-missing-before-argument': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD '
                                     '0])) = (expression_0)',
                                     '$ppcall_dynamic(expression_0) = true',
                                     '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                     '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                     'expression_0) = (UNPACK_VAR)'],
 'dynamic-undefined-callee': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD 0])) = '
                              '(expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                              'expression_0) = (UNPACK_VAR)'],
 'dynamic-nonstring-callee': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) = '
                              '(expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                              'expression_0) = (UNPACK_VAR)'],
 'dynamic-reference-name': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                            '(CODEEXPR ([PCINDEX 3, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                            '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, PCFIELD 0])) = '
                            '(expression_0)',
                            '$ppcall_dynamic(expression_0) = true',
                            '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 0]) = (PPR)',
                            '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0], expression_0) '
                            '= (UNPACK_VAR)'],
 'dynamic-selected-before-name-mutation': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0]) 1) <- '
                                           '$ppfunction_code(P).EXPRESSIONS',
                                           '(CODEEXPR ([PCINDEX 3, PCFIELD 0]) 1 false) <- '
                                           '$ppfunction_code(P).EXPRESSIONS',
                                           '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, '
                                           'PCFIELD 0])) = (expression_0)',
                                           '$ppcall_dynamic(expression_0) = true',
                                           '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                           '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0], '
                                           'expression_0) = (UNPACK_VAR)'],
 'dynamic-reference-cv': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                          '(CODEEXPR ([PCINDEX 3, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                          '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, PCFIELD 0])) = '
                          '(expression_0)',
                          '$ppcall_dynamic(expression_0) = true',
                          '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 0]) = (PPR)',
                          '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0], expression_0) = '
                          '(UNPACK_VAR)'],
 'dynamic-reference-append': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 3, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, PCFIELD 0])) = '
                              '(expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0], '
                              'expression_0) = (UNPACK_VAR)'],
 'dynamic-named-and-unpack': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) = '
                              '(expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                              'expression_0) = (UNPACK_VAR)'],
 'dynamic-reference-return': ['(CODECALL_INIT ([PCINDEX 3, PCFIELD 0, PCFIELD 1]) 1) <- '
                              '$ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 3, PCFIELD 0, PCFIELD 1]) 1 false) <- '
                              '$ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 3, PCFIELD 0, PCFIELD 1, '
                              'PCFIELD 0])) = (expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 3, PCFIELD 0, PCFIELD 1, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 3, PCFIELD 0, PCFIELD 1], '
                              'expression_0) = (UNPACK_VAR)'],
 'dynamic-multiline-callee': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 5) <- $ppfunction_code(P).EXPRESSIONS',
                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 6 false) <- $ppfunction_code(P).EXPRESSIONS',
                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) = '
                              '(expression_0)',
                              '$ppcall_dynamic(expression_0) = true',
                              '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                              'expression_0) = (UNPACK_VAR)',
                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0, PCFIELD 0]) 4 false) <- '
                              '$ppfunction_code(P).EXPRESSIONS'],
 'dynamic-literal-string-reference-mode': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                           '$ppfunction_code(P).EXPRESSIONS',
                                           '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                           '$ppfunction_code(P).EXPRESSIONS',
                                           '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, '
                                           'PCFIELD 0])) = (expression_0)',
                                           '$ppcall_dynamic(expression_0) = false',
                                           '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = eps',
                                           '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                           'expression_0) = (UNPACK_VAR)',
                                           '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) '
                                           '= (PPW)'],
 'dynamic-builtin-body-dependency': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0, PCINDEX 0]) 1) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '(CODEEXPR ([PCINDEX 1, PCFIELD 0, PCINDEX 0]) 1 false) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCINDEX 0, '
                                     'PCFIELD 0])) = (expression_0)',
                                     '$ppcall_dynamic(expression_0) = true',
                                     '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCINDEX 0, PCFIELD 0]) = (PPR)',
                                     '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0, '
                                     'PCINDEX 0], expression_0) = (UNPACK_VAR)'],
 'dynamic-array-callable-dependency': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD '
                                       '0])) = (expression_0)',
                                       '$ppcall_dynamic(expression_0) = true',
                                       '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                       '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                       'expression_0) = (UNPACK_VAR)'],
 'dynamic-static-method-string-dependency': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- '
                                             '$ppfunction_code(P).EXPRESSIONS',
                                             '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                             '$ppfunction_code(P).EXPRESSIONS',
                                             '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, '
                                             'PCFIELD 0])) = (expression_0)',
                                             '$ppcall_dynamic(expression_0) = true',
                                             '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                             '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD '
                                             '0], expression_0) = (UNPACK_VAR)'],
 'dynamic-literal-string-namespace': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 1, PCINDEX 1, PCFIELD 0]) 1) <- '
                                      '$ppfunction_code(P).EXPRESSIONS',
                                      '(CODEEXPR ([PCINDEX 1, PCFIELD 1, PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                      '$ppfunction_code(P).EXPRESSIONS',
                                      '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 1, PCINDEX '
                                      '1, PCFIELD 0, PCFIELD 0])) = (expression_0)',
                                      '$ppcall_dynamic(expression_0) = false',
                                      '$ppaccess(P, [PCINDEX 1, PCFIELD 1, PCINDEX 1, PCFIELD 0, PCFIELD 0]) = '
                                      'eps',
                                      '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 1, '
                                      'PCINDEX 1, PCFIELD 0], expression_0) = (UNPACK_VAR)'],
 'dynamic-folded-string-reference-mode': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                          '$ppfunction_code(P).EXPRESSIONS',
                                          '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                          '$ppfunction_code(P).EXPRESSIONS',
                                          '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, '
                                          'PCFIELD 0])) = (expression_0)',
                                          '$ppcall_dynamic(expression_0) = false',
                                          '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = eps',
                                          '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                          'expression_0) = (UNPACK_VAR)',
                                          '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) '
                                          '= (PPW)'],
 'dynamic-later-cast-string-ref': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                   '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                   '$ppfunction_code(P).EXPRESSIONS',
                                   '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) '
                                   '= (expression_0)',
                                   '$ppcall_dynamic(expression_0) = true',
                                   '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                   '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                   'expression_0) = (UNPACK_VAR)',
                                   '$code_name($ppfunction_code(P).NAMES, [PCINDEX 2, PCFIELD 0]) = eps',
                                   '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 2, PCFIELD 0, '
                                   'PCFIELD 0]) = ((1, false))',
                                   '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = '
                                   '(PPF)'],
 'dynamic-later-concat-string-ref': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                     '$ppfunction_code(P).EXPRESSIONS',
                                     '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD '
                                     '0])) = (expression_0)',
                                     '$ppcall_dynamic(expression_0) = true',
                                     '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                     '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                     'expression_0) = (UNPACK_VAR)',
                                     '$code_name($ppfunction_code(P).NAMES, [PCINDEX 2, PCFIELD 0]) = eps',
                                     '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 2, PCFIELD 0, '
                                     'PCFIELD 0]) = ((1, false))',
                                     '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = '
                                     '(PPF)'],
 'dynamic-later-cast-named-ref': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                  '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                                  '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 0])) '
                                  '= (expression_0)',
                                  '$ppcall_dynamic(expression_0) = true',
                                  '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                  '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                  'expression_0) = (UNPACK_VAR)',
                                  '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (PPF)'],
 'dynamic-literal-multiline-send': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 3) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 3 false) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD '
                                    '0])) = (expression_0)',
                                    '$ppcall_dynamic(expression_0) = false',
                                    '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = eps',
                                    '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                    'expression_0) = (UNPACK_VAR)'],
 'dynamic-cast-multiline-send': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 3) <- $ppfunction_code(P).EXPRESSIONS',
                                 '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 3 false) <- $ppfunction_code(P).EXPRESSIONS',
                                 '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD 0])) = '
                                 '(expression_0)',
                                 '$ppcall_dynamic(expression_0) = true',
                                 '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                 '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                 'expression_0) = (UNPACK_VAR)'],
 'dynamic-literal-forward-mode': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                  '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                                  '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD 0])) '
                                  '= (expression_0)',
                                  '$ppcall_dynamic(expression_0) = false',
                                  '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = eps',
                                  '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                  'expression_0) = (UNPACK_VAR)',
                                  '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (PPF)'],
 'dynamic-later-folded-constant-ref': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD '
                                       '0])) = (expression_0)',
                                       '$ppcall_dynamic(expression_0) = true',
                                       '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                       '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                       'expression_0) = (UNPACK_VAR)',
                                       '$code_name($ppfunction_code(P).NAMES, [PCINDEX 2, PCFIELD 0]) = '
                                       '(([102,49], eps))',
                                       '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 2, PCFIELD 0, '
                                       'PCFIELD 0]) = ((1, true))',
                                       '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = '
                                       '(PPF)'],
 'dynamic-parser-numeric-concat-ref': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 1) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 1 false) <- '
                                       '$ppfunction_code(P).EXPRESSIONS',
                                       '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD '
                                       '0])) = (expression_0)',
                                       '$ppcall_dynamic(expression_0) = false',
                                       '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = eps',
                                       '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                       'expression_0) = (UNPACK_VAR)',
                                       '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = '
                                       '(PPW)'],
 'dynamic-initial-literal-missing-name': ['(CODECALL_INIT ([PCINDEX 0, PCFIELD 0]) 1) <- '
                                          '$ppfunction_code(P).EXPRESSIONS',
                                          '(CODEEXPR ([PCINDEX 0, PCFIELD 0]) 1 false) <- '
                                          '$ppfunction_code(P).EXPRESSIONS',
                                          '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 0, PCFIELD 0, '
                                          'PCFIELD 0])) = (expression_0)',
                                          '$ppcall_dynamic(expression_0) = false',
                                          '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCFIELD 0]) = eps',
                                          '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 0, PCFIELD 0], '
                                          'expression_0) = (UNPACK_VAR)'],
 'dynamic-call-boundary': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0, PCFIELD 1]) 1) <- '
                           '$ppfunction_code(P).EXPRESSIONS',
                           '(CODEEXPR ([PCINDEX 2, PCFIELD 0, PCFIELD 1]) 1 false) <- '
                           '$ppfunction_code(P).EXPRESSIONS',
                           '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD 1, PCFIELD '
                           '0])) = (expression_0)',
                           '$ppcall_dynamic(expression_0) = true',
                           '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCFIELD 0]) = (PPR)',
                           '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0, PCFIELD 1], '
                           'expression_0) = (UNPACK_VAR)'],
 'dynamic-reference-result-unpack': ['(CODECALL_INIT ([PCINDEX 4, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) 1) '
                                     '<- $ppfunction_code(P).EXPRESSIONS',
                                     '(CODEEXPR ([PCINDEX 4, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) 1 '
                                     'false) <- $ppfunction_code(P).EXPRESSIONS',
                                     '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 4, PCFIELD 0, PCFIELD 1, '
                                     'PCINDEX 0, PCFIELD 1, PCFIELD 0])) = (expression_0)',
                                     '$ppcall_dynamic(expression_0) = true',
                                     '$ppaccess(P, [PCINDEX 4, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1, '
                                     'PCFIELD 0]) = (PPR)',
                                     '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 4, PCFIELD 0, '
                                     'PCFIELD 1, PCINDEX 0, PCFIELD 1], expression_0) = (UNPACK_VAR)',
                                     '$ppunpack_class($ppfunction_code(P), P.FOLD.SOURCE, [PCINDEX 4, PCFIELD 0, '
                                     'PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (UNPACK_VAR)'],
 'dynamic-successful-multiline-callee-type': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 5) <- '
                                              '$ppfunction_code(P).EXPRESSIONS',
                                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 6 false) <- '
                                              '$ppfunction_code(P).EXPRESSIONS',
                                              '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, '
                                              'PCFIELD 0])) = (expression_0)',
                                              '$ppcall_dynamic(expression_0) = true',
                                              '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                              '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD '
                                              '0], expression_0) = (UNPACK_VAR)',
                                              '(CODEEXPR ([PCINDEX 2, PCFIELD 0, PCFIELD 0]) 4 false) <- '
                                              '$ppfunction_code(P).EXPRESSIONS'],
 'dynamic-parenthesized-literal-call-line': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 5) <- '
                                             '$ppfunction_code(P).EXPRESSIONS',
                                             '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 5 false) <- '
                                             '$ppfunction_code(P).EXPRESSIONS',
                                             '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, '
                                             'PCFIELD 0])) = (expression_0)',
                                             '$ppcall_dynamic(expression_0) = false',
                                             '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = eps',
                                             '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD '
                                             '0], expression_0) = (UNPACK_VAR)'],
 'dynamic-parenthesized-cv-call-line': ['(CODECALL_INIT ([PCINDEX 2, PCFIELD 0]) 5) <- '
                                        '$ppfunction_code(P).EXPRESSIONS',
                                        '(CODEEXPR ([PCINDEX 2, PCFIELD 0]) 6 false) <- '
                                        '$ppfunction_code(P).EXPRESSIONS',
                                        '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 2, PCFIELD 0, PCFIELD '
                                        '0])) = (expression_0)',
                                        '$ppcall_dynamic(expression_0) = true',
                                        '$ppaccess(P, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                        '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 2, PCFIELD 0], '
                                        'expression_0) = (UNPACK_VAR)'],
 'dynamic-later-constant-leading-slash-existing': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- '
                                                   '$ppfunction_code(P).EXPRESSIONS',
                                                   '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                                   '$ppfunction_code(P).EXPRESSIONS',
                                                   '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD '
                                                   '0, PCFIELD 0])) = (expression_0)',
                                                   '$ppcall_dynamic(expression_0) = true',
                                                   '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                                   '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, '
                                                   'PCFIELD 0], expression_0) = (UNPACK_VAR)',
                                                   '$code_name($ppfunction_code(P).NAMES, [PCINDEX 1, PCFIELD 0]) '
                                                   '= (([92,102,49], eps))',
                                                   '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 1, '
                                                   'PCFIELD 0, PCFIELD 0]) = ((1, true))'],
 'dynamic-later-constant-leading-slash-missing': ['(CODECALL_INIT ([PCINDEX 0, PCFIELD 0]) 1) <- '
                                                  '$ppfunction_code(P).EXPRESSIONS',
                                                  '(CODEEXPR ([PCINDEX 0, PCFIELD 0]) 1 false) <- '
                                                  '$ppfunction_code(P).EXPRESSIONS',
                                                  '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 0, PCFIELD '
                                                  '0, PCFIELD 0])) = (expression_0)',
                                                  '$ppcall_dynamic(expression_0) = true',
                                                  '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                                  '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 0, '
                                                  'PCFIELD 0], expression_0) = (UNPACK_VAR)',
                                                  '$code_name($ppfunction_code(P).NAMES, [PCINDEX 0, PCFIELD 0]) '
                                                  '= (([92,77,105,115,115,105,110,103,49], eps))',
                                                  '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 0, '
                                                  'PCFIELD 0, PCFIELD 0]) = ((1, true))'],
 'dynamic-ternary-leading-slash': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                   '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                   '$ppfunction_code(P).EXPRESSIONS',
                                   '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD 0])) '
                                   '= (expression_0)',
                                   '$ppcall_dynamic(expression_0) = true',
                                   '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                   '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                   'expression_0) = (UNPACK_VAR)',
                                   '$code_name($ppfunction_code(P).NAMES, [PCINDEX 1, PCFIELD 0]) = eps',
                                   '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 1, PCFIELD 0, '
                                   'PCFIELD 0]) = ((1, false))'],
 'dynamic-coalesce-leading-slash': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                    '$ppfunction_code(P).EXPRESSIONS',
                                    '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD '
                                    '0])) = (expression_0)',
                                    '$ppcall_dynamic(expression_0) = true',
                                    '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                    '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                    'expression_0) = (UNPACK_VAR)',
                                    '$code_name($ppfunction_code(P).NAMES, [PCINDEX 1, PCFIELD 0]) = eps',
                                    '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 1, PCFIELD 0, '
                                    'PCFIELD 0]) = ((1, false))'],
 'dynamic-suppressed-constant-leading-slash': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- '
                                               '$ppfunction_code(P).EXPRESSIONS',
                                               '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- '
                                               '$ppfunction_code(P).EXPRESSIONS',
                                               '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, '
                                               'PCFIELD 0])) = (expression_0)',
                                               '$ppcall_dynamic(expression_0) = true',
                                               '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                               '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD '
                                               '0], expression_0) = (UNPACK_VAR)',
                                               '$code_name($ppfunction_code(P).NAMES, [PCINDEX 1, PCFIELD 0]) = '
                                               '(([92,102,49], eps))',
                                               '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 1, '
                                               'PCFIELD 0, PCFIELD 0]) = ((1, true))'],
 'dynamic-cast-leading-slash': ['(CODECALL_INIT ([PCINDEX 1, PCFIELD 0]) 1) <- $ppfunction_code(P).EXPRESSIONS',
                                '(CODEEXPR ([PCINDEX 1, PCFIELD 0]) 1 false) <- $ppfunction_code(P).EXPRESSIONS',
                                '$origin_node([P.FOLD.SOURCE], PORIGIN 91 ([PCINDEX 1, PCFIELD 0, PCFIELD 0])) = '
                                '(expression_0)',
                                '$ppcall_dynamic(expression_0) = true',
                                '$ppaccess(P, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (PPR)',
                                '$ppunpack_function_class($ppfunction_code(P), [PCINDEX 1, PCFIELD 0], '
                                'expression_0) = (UNPACK_VAR)',
                                '$code_name($ppfunction_code(P).NAMES, [PCINDEX 1, PCFIELD 0]) = eps',
                                '$code_expression($ppfunction_code(P).EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD '
                                '0]) = ((1, false))']}
PENDING = {'dynamic-initial-literal-builtin-boundary': 'initial literal builtin call lowering', 'dynamic-initial-literal-builtin-write-boundary': 'initial literal builtin call lowering'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/dynamic_call_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='dynamic-call-compiler-', dir=ROOT / '.tools'))
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
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Dynamic expression-call compiler phases, initial parser category, source argument modes and separate INIT/call lines; runtime lookup and ownership are separately paired.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/dynamic-call-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
