#!/usr/bin/env python3
"""Arrow compiler phases, ordered implicit bindings, real expression returns and emitted lines."""
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
CASES = json.loads((ROOT / 'tests/semantics/arrow_compiler_cases.json').read_text())


CONTEXTS = {'arrow-order-parameter-shadow': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 2,PCFIELD 0,PCFIELD '
                                  '1])) = (pfunction_0)',
                                  'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                  'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                  'pfunction_0.BODY = ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                  '~pfunction_0.EARLY',
                                  '$pparrow_template(pfunction_0)',
                                  '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([98])]',
                                  '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT '
                                  '([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([98]) 1)]',
                                  '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 2,PCFIELD '
                                  '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                  '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                  '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-nested-parameter-discovery': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1])) = (pfunction_0)',
                                      'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                      'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                      'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                      '~pfunction_0.EARLY',
                                      '$pparrow_template(pfunction_0)',
                                      '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([120])]',
                                      '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT '
                                      '([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([120]) 1)]',
                                      '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                      '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1,PCFIELD 5])) = (pfunction_1)',
                                      'pfunction_1.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58, 123, '
                                      '99, 108, 111, 115, 117, 114, 101, 58]) ++ SOURCE_FILE_BYTES ++ ([58, '
                                      '49, 125, 58, 49, 125])',
                                      'pfunction_1.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5,PCFIELD '
                                      '5])',
                                      '~pfunction_1.EARLY',
                                      '$pparrow_template(pfunction_1)',
                                      '$fixture_implicit_names(pfunction_1.CODE.EXPRESSIONS) = []',
                                      '$fixture_implicits(pfunction_1.CODE.EXPRESSIONS) = []',
                                      '$fixture_arrows(pfunction_1.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1,PCFIELD 5,PCFIELD 5]), 1)]',
                                      '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                      '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-nested-explicit-use': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD 0,PCFIELD '
                               '1])) = (pfunction_0)',
                               'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                               'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                               'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                               '~pfunction_0.EARLY',
                               '$pparrow_template(pfunction_0)',
                               '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([120])]',
                               '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT ([PCINDEX '
                               '1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([120]) 1)]',
                               '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                               '0,PCFIELD 1,PCFIELD 5]), 1)]',
                               '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                               '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-folded-variable-name': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD 0,PCFIELD '
                                '1])) = (pfunction_0)',
                                'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                '~pfunction_0.EARLY',
                                '$pparrow_template(pfunction_0)',
                                '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([120,121])]',
                                '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT ([PCINDEX '
                                '1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([120,121]) 1)]',
                                '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                                '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-computed-variable-discovery': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 2,PCFIELD '
                                       '0,PCFIELD 1])) = (pfunction_0)',
                                       'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                       'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                       'pfunction_0.BODY = ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                       '~pfunction_0.EARLY',
                                       '$pparrow_template(pfunction_0)',
                                       '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([110])]',
                                       '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT '
                                       '([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([110]) 1)]',
                                       '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX '
                                       '2,PCFIELD 0,PCFIELD 1,PCFIELD 5]), 1)]',
                                       '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                       '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-autoglobal-discovery': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 2,PCFIELD 0,PCFIELD '
                                '1])) = (pfunction_0)',
                                'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                'pfunction_0.BODY = ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                '~pfunction_0.EARLY',
                                '$pparrow_template(pfunction_0)',
                                '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 2,PCFIELD '
                                '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-static-magic-nested': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 1,PCINDEX '
                               '0,PCFIELD 5,PCINDEX 0,PCFIELD 0])) = (pfunction_0)',
                               'pfunction_0.NAME = '
                               '[123,99,108,111,115,117,114,101,58,78,92,109,97,107,101,40,41,58,49,125]',
                               'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 5,PCINDEX '
                               '0,PCFIELD 0,PCFIELD 5])',
                               '~pfunction_0.EARLY',
                               '$pparrow_template(pfunction_0)',
                               '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                               '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                               '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                               '1,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 5]), 1)]',
                               '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 1,PCINDEX '
                               '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 5,PCFIELD 0,PCINDEX 2,PCFIELD '
                               '1,PCFIELD 0])) = (pfunction_1)',
                               'pfunction_1.NAME = '
                               '[123,99,108,111,115,117,114,101,58,123,99,108,111,115,117,114,101,58,78,92,109,97,107,101,40,41,58,49,125,58,49,125]',
                               'pfunction_1.BODY = ([PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 5,PCINDEX '
                               '0,PCFIELD 0,PCFIELD 5,PCFIELD 0,PCINDEX 2,PCFIELD 1,PCFIELD 0,PCFIELD 5])',
                               '~pfunction_1.EARLY',
                               '$pparrow_template(pfunction_1)',
                               '$fixture_implicit_names(pfunction_1.CODE.EXPRESSIONS) = []',
                               '$fixture_implicits(pfunction_1.CODE.EXPRESSIONS) = []',
                               '$fixture_arrows(pfunction_1.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                               '1,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 5,PCFIELD 0,PCINDEX '
                               '2,PCFIELD 1,PCFIELD 0,PCFIELD 5]), 1)]',
                               '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                               '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-named-default-types': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD 0,PCFIELD '
                               '1])) = (pfunction_0)',
                               'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                               'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                               'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                               '~pfunction_0.EARLY',
                               '$pparrow_template(pfunction_0)',
                               '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([122])]',
                               '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT ([PCINDEX '
                               '1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([122]) 1)]',
                               '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                               '0,PCFIELD 1,PCFIELD 5]), 1)]',
                               '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                               '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-unpack-reference-signature': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                      '0,PCFIELD 1])) = (pfunction_0)',
                                      'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                      'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                      'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                      '~pfunction_0.EARLY',
                                      '$pparrow_template(pfunction_0)',
                                      '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                      '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                      '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                                      '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                      '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                      '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-never-fallthrough': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD 1])) '
                             '= (pfunction_0)',
                             'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                             'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                             'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                             '~pfunction_0.EARLY',
                             '$pparrow_template(pfunction_0)',
                             '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                             '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                             '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 0,PCFIELD 0,PCFIELD '
                             '1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5]) 1 '
                             'true)]',
                             '$ppaccess(P, ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = (PPR)',
                             '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                             '0,PCFIELD 1,PCFIELD 5]), 1)]',
                             '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                             '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-never-expression-error': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                  '1])) = (pfunction_0)',
                                  'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                  'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                  'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                  '~pfunction_0.EARLY',
                                  '$pparrow_template(pfunction_0)',
                                  '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                  '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                  '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                                  '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                  '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                  '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-multiline-parameter-type': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                    '0,PCFIELD 1])) = (pfunction_0)',
                                    'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                    'SOURCE_FILE_BYTES ++ ([58, 50, 125])',
                                    'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                    '~pfunction_0.EARLY',
                                    '$pparrow_template(pfunction_0)',
                                    '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                    '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                    '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                                    '0,PCFIELD 1,PCFIELD 5]), 5)]',
                                    '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                    '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-multiline-return-type': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                 '1])) = (pfunction_0)',
                                 'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                 'SOURCE_FILE_BYTES ++ ([58, 50, 125])',
                                 'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                 '~pfunction_0.EARLY',
                                 '$pparrow_template(pfunction_0)',
                                 '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                 '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                 '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                 '1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5]) 3 '
                                 'true)]',
                                 '$ppaccess(P, ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = (PPR)',
                                 '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 0,PCFIELD '
                                 '0,PCFIELD 1,PCFIELD 5]), 3)]',
                                 '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                 '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-array-discovery-order': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 2,PCFIELD 0,PCFIELD '
                                 '1])) = (pfunction_0)',
                                 'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                 'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                 'pfunction_0.BODY = ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                 '~pfunction_0.EARLY',
                                 '$pparrow_template(pfunction_0)',
                                 '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([118]),([107])]',
                                 '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT '
                                 '([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([118]) 1),(CODEIMPLICIT '
                                 '([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([107]) 1)]',
                                 '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 2,PCFIELD 0,PCFIELD '
                                 '1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5]) 1 '
                                 'false)]',
                                 '$ppaccess(P, ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = (PPR)',
                                 '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 2,PCFIELD '
                                 '0,PCFIELD 1,PCFIELD 5]), 1)]',
                                 '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                 '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-multiline-captured-return': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1])) = (pfunction_0)',
                                     'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                     'SOURCE_FILE_BYTES ++ ([58, 51, 125])',
                                     'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                     '~pfunction_0.EARLY',
                                     '$pparrow_template(pfunction_0)',
                                     '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = [([118])]',
                                     '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = [(CODEIMPLICIT '
                                     '([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) ([118]) 4)]',
                                     '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 1,PCFIELD 0,PCFIELD '
                                     '1,PCFIELD 5]) 6 false)]',
                                     '$ppaccess(P, ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = (PPR)',
                                     '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1,PCFIELD 5]), 6)]',
                                     '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                     '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-never-discarded-reference-call': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                          '0,PCFIELD 1])) = (pfunction_0)',
                                          'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) '
                                          '++ SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                          'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                          '~pfunction_0.EARLY',
                                          '$pparrow_template(pfunction_0)',
                                          '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                          '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                          '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 1,PCFIELD '
                                          '0,PCFIELD 1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 1,PCFIELD '
                                          '0,PCFIELD 1,PCFIELD 5]) 1 false)]',
                                          '$ppaccess(P, ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = (PPR)',
                                          '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX '
                                          '1,PCFIELD 0,PCFIELD 1,PCFIELD 5]), 1)]',
                                          '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                          '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-reference-return-local-lifetime': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                           '0,PCFIELD 1])) = (pfunction_0)',
                                           'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) '
                                           '++ SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                           'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                           '~pfunction_0.EARLY',
                                           '$pparrow_template(pfunction_0)',
                                           '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = '
                                           '[([120])]',
                                           'pfunction_0.SIGNATURE.BYREF',
                                           '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = '
                                           '[(CODEIMPLICIT ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5]) '
                                           '([120]) 1)]',
                                           '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 1,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 1,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5]) 1 false)]',
                                           '$ppaccess(P, ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = '
                                           '(PPW)',
                                           '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX '
                                           '1,PCFIELD 0,PCFIELD 1,PCFIELD 5]), 1)]',
                                           '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                           '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps'],
 'arrow-reference-return-value-and-call': ['$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 2,PCFIELD '
                                           '0,PCFIELD 1])) = (pfunction_0)',
                                           'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) '
                                           '++ SOURCE_FILE_BYTES ++ ([58, 51, 125])',
                                           'pfunction_0.BODY = ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                           '~pfunction_0.EARLY',
                                           '$pparrow_template(pfunction_0)',
                                           '$fixture_implicit_names(pfunction_0.CODE.EXPRESSIONS) = []',
                                           'pfunction_0.SIGNATURE.BYREF',
                                           '$fixture_implicits(pfunction_0.CODE.EXPRESSIONS) = []',
                                           '$fixture_body(pfunction_0.CODE.EXPRESSIONS, ([PCINDEX 2,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 2,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5]) 3 true)]',
                                           '$ppaccess(P, ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = '
                                           '(PPR)',
                                           '$fixture_arrows(pfunction_0.CODE.EXPRESSIONS) = [(([PCINDEX '
                                           '2,PCFIELD 0,PCFIELD 1,PCFIELD 5]), 3)]',
                                           '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 3,PCFIELD '
                                           '0,PCFIELD 1])) = (pfunction_1)',
                                           'pfunction_1.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) '
                                           '++ SOURCE_FILE_BYTES ++ ([58, 52, 125])',
                                           'pfunction_1.BODY = ([PCINDEX 3,PCFIELD 0,PCFIELD 1,PCFIELD 5])',
                                           '~pfunction_1.EARLY',
                                           '$pparrow_template(pfunction_1)',
                                           '$fixture_implicit_names(pfunction_1.CODE.EXPRESSIONS) = []',
                                           'pfunction_1.SIGNATURE.BYREF',
                                           '$fixture_implicits(pfunction_1.CODE.EXPRESSIONS) = []',
                                           '$fixture_body(pfunction_1.CODE.EXPRESSIONS, ([PCINDEX 3,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5])) = [(CODEEXPR ([PCINDEX 3,PCFIELD '
                                           '0,PCFIELD 1,PCFIELD 5]) 4 false)]',
                                           '$ppaccess(P, ([PCINDEX 3,PCFIELD 0,PCFIELD 1,PCFIELD 5])) = '
                                           '(PPR)',
                                           '$fixture_arrows(pfunction_1.CODE.EXPRESSIONS) = [(([PCINDEX '
                                           '3,PCFIELD 0,PCFIELD 1,PCFIELD 5]), 4)]',
                                           '$fixture_implicits($ppfunction_code(P).EXPRESSIONS) = eps',
                                           '$fixture_arrows($ppfunction_code(P).EXPRESSIONS) = eps']}

PENDING = {}

EXTRA = 'dec $fixture_implicit_entry(pcodeexpr) : ptbytes*\ndef $fixture_implicit_entry(CODEIMPLICIT pcpath ptbytes z) = [ptbytes]\ndef $fixture_implicit_entry(pcodeexpr) = eps -- otherwise\ndec $fixture_implicit_names(pcodeexpr*) : ptbytes*\ndef $fixture_implicit_names(eps) = eps\ndef $fixture_implicit_names(pcodeexpr :: pcodeexpr_tail*) = $fixture_implicit_entry(pcodeexpr) ++ $fixture_implicit_names(pcodeexpr_tail*)\ndec $fixture_arrows_entry(pcodeexpr) : (pcpath, int)*\ndef $fixture_arrows_entry(CODEARROW pcpath z) = [(pcpath, z)]\ndef $fixture_arrows_entry(pcodeexpr) = eps -- otherwise\ndec $fixture_arrows(pcodeexpr*) : (pcpath, int)*\ndef $fixture_arrows(eps) = eps\ndef $fixture_arrows(pcodeexpr :: pcodeexpr_tail*) = $fixture_arrows_entry(pcodeexpr) ++ $fixture_arrows(pcodeexpr_tail*)\ndec $fixture_implicits(pcodeexpr*) : pcodeexpr*\ndef $fixture_implicits(eps) = eps\ndec $fixture_implicit_code(pcodeexpr) : pcodeexpr*\ndef $fixture_implicit_code(CODEIMPLICIT pcpath ptbytes z) = [CODEIMPLICIT pcpath ptbytes z]\ndef $fixture_implicit_code(pcodeexpr) = eps -- otherwise\ndef $fixture_implicits(pcodeexpr :: pcodeexpr_tail*) = $fixture_implicit_code(pcodeexpr) ++ $fixture_implicits(pcodeexpr_tail*)\ndec $fixture_body(pcodeexpr*, pcpath) : pcodeexpr*\ndef $fixture_body(eps, pcpath) = eps\ndec $fixture_body_entry(pcodeexpr, pcpath) : pcodeexpr*\ndef $fixture_body_entry(CODEEXPR pcpath z b, pcpath) = [CODEEXPR pcpath z b]\ndef $fixture_body_entry(pcodeexpr, pcpath) = eps -- otherwise\ndef $fixture_body(pcodeexpr :: pcodeexpr_tail*, pcpath) = $fixture_body_entry(pcodeexpr, pcpath) ++ $fixture_body(pcodeexpr_tail*, pcpath)\n'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/arrow_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='arrow-compiler-', dir=ROOT / '.tools'))
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
                body += ''.join('  -- if '+condition+'\n' for raw_condition in CONTEXTS.get(name, []) for condition in [raw_condition.replace('SOURCE_FILE_BYTES', types.byte_expr(str(file)))])
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
    report = {'scope': 'Arrow compiler phases, ordered source-derived implicit bindings, distinct template kind, own-scope markers, signature priorities, magic names and separate return/body metadata; implicit undefined values and runtime ownership are separately paired.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/arrow-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
