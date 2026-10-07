#!/usr/bin/env python3
"""Source-reached receive generations and effectful parameter-alias cuts."""
import argparse,json,tempfile
from pathlib import Path
import parameter_callable_alias_protocol as donor

global_protocol=donor.global_protocol
base=donor.base
ROOT=donor.ROOT
premises=donor.premises
FILES={}

SOURCES={'parameter-namespace-warning-prefix': '<?php\n'
                                       'namespace {\n'
                                       '    const ParameterNoticeSeed = static function () { '
                                       "return 'global'; };\n"
                                       '    trait ParameterNoticeTrait { public static function '
                                       "target() { return 'trait'; } }\n"
                                       '}\n'
                                       'namespace ParameterNotice {\n'
                                       '    function take($a = [ParameterNoticeSeed, '
                                       '\\ParameterNoticeTrait::target(...), '
                                       'ParameterNoticeSeed]) { return $a; }\n'
                                       '    $seen = 0;\n'
                                       '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                       '        ++$seen;\n'
                                       "        echo 'H|';\n"
                                       "        eval('namespace ParameterNotice; const "
                                       'ParameterNoticeSeed = static function () { return '
                                       '"local"; };\');\n'
                                       '        return true;\n'
                                       '    });\n'
                                       '    $a = take();\n'
                                       '    $b = take();\n'
                                       "    echo $a[0] === \\ParameterNoticeSeed ? 'old:' : "
                                       "'wrong:';\n"
                                       "    echo $a[2] === ParameterNoticeSeed ? 'new:' : "
                                       "'wrong:';\n"
                                       "    echo $b[0] === ParameterNoticeSeed ? 'local:' : "
                                       "'wrong:';\n"
                                       "    echo $a[1] !== $b[1] ? 'fresh:' : 'same:';\n"
                                       "    echo $seen, ':';\n"
                                       '    $old = $a[0];\n'
                                       '    $new = $a[2];\n'
                                       "    echo $old(), ':', $new();\n"
                                       '}\n',
 'parameter-namespace-warning-retry': '<?php\n'
                                      'namespace {\n'
                                      '    const ParameterRetrySeed = static function () { return '
                                      "'global'; };\n"
                                      '    trait ParameterRetryTrait { public static function '
                                      "target() { return 'trait'; } }\n"
                                      '}\n'
                                      'namespace ParameterRetry {\n'
                                      '    function take($a = [ParameterRetrySeed, '
                                      '\\ParameterRetryTrait::target(...), ParameterRetrySeed]) { '
                                      'return $a; }\n'
                                      '    $seen = 0;\n'
                                      '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                      '        ++$seen;\n'
                                      "        echo 'H', $seen, '|';\n"
                                      '        if ($seen === 1) {\n'
                                      "            eval('namespace ParameterRetry; const "
                                      'ParameterRetrySeed = static function () { return "local"; '
                                      "};');\n"
                                      "            throw new \\Exception('stop');\n"
                                      '        }\n'
                                      '        return true;\n'
                                      '    });\n'
                                      '    try { take(); } catch (\\Exception $e) { echo '
                                      "$e->getMessage(), '|'; }\n"
                                      '    $a = take();\n'
                                      '    $first = $a[0];\n'
                                      '    $last = $a[2];\n'
                                      "    echo $first(), ':', $last(), ':', $seen;\n"
                                      '}\n',
 'parameter-trailing-real-warning': '<?php\n'
                                    'namespace {\n'
                                    '    const ParameterNoticeSeed = static function () { return '
                                    "'global'; };\n"
                                    '    trait ParameterNoticeTrait { public static function '
                                    "target() { return 'trait'; } }\n"
                                    '}\n'
                                    'namespace ParameterNotice {\n'
                                    '    function take($a = [ParameterNoticeSeed, '
                                    '\\ParameterNoticeTrait::target(...), ParameterNoticeSeed, '
                                    "static function () { return 'after'; }]) { return $a; }\n"
                                    '    $seen = 0;\n'
                                    '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                    '        ++$seen;\n'
                                    "        echo 'H|';\n"
                                    "        eval('namespace ParameterNotice; const "
                                    'ParameterNoticeSeed = static function () { return "local"; '
                                    "};');\n"
                                    '        return true;\n'
                                    '    });\n'
                                    '    $a = take();\n'
                                    '    $b = take();\n'
                                    "    echo $a[0] === \\ParameterNoticeSeed ? 'old:' : "
                                    "'wrong:';\n"
                                    "    echo $a[2] === ParameterNoticeSeed ? 'new:' : 'wrong:';\n"
                                    "    echo $b[0] === ParameterNoticeSeed ? 'local:' : "
                                    "'wrong:';\n"
                                    "    echo $a[1] !== $b[1] ? 'fresh:' : 'same:';\n"
                                    "    echo $seen, ':';\n"
                                    '    $old = $a[0];\n'
                                    '    $new = $a[2];\n'
                                    "    echo $old(), ':', $new();\n"
                                    '}\n',
 'parameter-generation-same-site-retry': '<?php\n'
                                         'namespace {\n'
                                         '    const ParameterGenerationRetrySeed = static '
                                         "function () { return 'global'; };\n"
                                         '    trait ParameterGenerationRetryTrait { public static '
                                         "function target() { return 'trait'; } }\n"
                                         '}\n'
                                         'namespace ParameterGenerationRetry {\n'
                                         '    function take($a = [ParameterGenerationRetrySeed, '
                                         '\\ParameterGenerationRetryTrait::target(...), '
                                         'ParameterGenerationRetrySeed]) { return $a; }\n'
                                         '    function driver() { return take(); }\n'
                                         '    $seen = 0;\n'
                                         '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                         '        ++$seen;\n'
                                         "        echo 'H', $seen, '|';\n"
                                         '        if ($seen === 1) {\n'
                                         "            eval('namespace ParameterGenerationRetry; "
                                         'const ParameterGenerationRetrySeed = static function () '
                                         '{ return "local"; };\');\n'
                                         "            throw new \\Exception('stop');\n"
                                         '        }\n'
                                         '        return true;\n'
                                         '    });\n'
                                         '    try { driver(); } catch (\\Exception $e) { echo '
                                         "$e->getMessage(), '|'; }\n"
                                         '    $a = driver();\n'
                                         '    $first = $a[0];\n'
                                         '    $last = $a[2];\n'
                                         "    echo $first(), ':', $last(), ':', $seen;\n"
                                         '}\n',
 'parameter-generation-same-parent-loop': '<?php\n'
                                          'namespace {\n'
                                          '    const ParameterGenerationLoopSeed = static '
                                          "function () { return 'global'; };\n"
                                          '    trait ParameterGenerationLoopTrait { public static '
                                          "function target() { return 'trait'; } }\n"
                                          '}\n'
                                          'namespace ParameterGenerationLoop {\n'
                                          '    function take($a = [ParameterGenerationLoopSeed, '
                                          '\\ParameterGenerationLoopTrait::target(...), '
                                          'ParameterGenerationLoopSeed]) { return $a; }\n'
                                          '    function driver() {\n'
                                          '        $last = [];\n'
                                          '        for ($i = 0; $i < 2; ++$i) {\n'
                                          '            try { $last = take(); } catch (\\Exception '
                                          "$e) { echo $e->getMessage(), '|'; }\n"
                                          '        }\n'
                                          '        return $last;\n'
                                          '    }\n'
                                          '    $seen = 0;\n'
                                          '    set_error_handler(function ($n, $m) use (&$seen) '
                                          '{\n'
                                          '        ++$seen;\n'
                                          "        echo 'H', $seen, '|';\n"
                                          '        if ($seen === 1) {\n'
                                          "            eval('namespace ParameterGenerationLoop; "
                                          'const ParameterGenerationLoopSeed = static function () '
                                          '{ return "local"; };\');\n'
                                          "            throw new \\Exception('stop');\n"
                                          '        }\n'
                                          '        return true;\n'
                                          '    });\n'
                                          '    $a = driver();\n'
                                          '    $first = $a[0];\n'
                                          '    $last = $a[2];\n'
                                          "    echo $first(), ':', $last(), ':', $seen;\n"
                                          '}\n',
 'parameter-generation-foreign-birth-loop': '<?php\n'
                                            'namespace {\n'
                                            '    const ParameterGenerationForeignSeed = static '
                                            "function () { return 'global'; };\n"
                                            '    trait ParameterGenerationForeignTrait { public '
                                            "static function target() { return 'trait'; } }\n"
                                            '}\n'
                                            'namespace ParameterGenerationForeign {\n'
                                            '    function take($a = '
                                            '[ParameterGenerationForeignSeed, '
                                            '\\ParameterGenerationForeignTrait::target(...), '
                                            'ParameterGenerationForeignSeed]) { return $a; }\n'
                                            '    function other($a = '
                                            'ParameterGenerationForeignSeed) { return $a; }\n'
                                            '    function driver() {\n'
                                            '        $foreign = other();\n'
                                            "        echo 'F:', $foreign(), '|';\n"
                                            '        $last = [];\n'
                                            '        for ($i = 0; $i < 2; ++$i) {\n'
                                            '            try { $last = take(); } catch '
                                            "(\\Exception $e) { echo $e->getMessage(), '|'; }\n"
                                            '        }\n'
                                            '        return $last;\n'
                                            '    }\n'
                                            '    $seen = 0;\n'
                                            '    set_error_handler(function ($n, $m) use (&$seen) '
                                            '{\n'
                                            '        ++$seen;\n'
                                            "        echo 'H', $seen, '|';\n"
                                            '        if ($seen === 1) {\n'
                                            "            eval('namespace "
                                            'ParameterGenerationForeign; const '
                                            'ParameterGenerationForeignSeed = static function () '
                                            '{ return "local"; };\');\n'
                                            "            throw new \\Exception('stop');\n"
                                            '        }\n'
                                            '        return true;\n'
                                            '    });\n'
                                            '    $a = driver();\n'
                                            '    $first = $a[0];\n'
                                            '    $last = $a[2];\n'
                                            "    echo $first(), ':', $last(), ':', $seen;\n"
                                            '}\n',
 'parameter-generation-named-hole-retry': '<?php\n'
                                          'namespace {\n'
                                          "    const Seed = static function () { return 'global'; "
                                          '};\n'
                                          '}\n'
                                          'namespace ParameterGenerationNamed {\n'
                                          '    trait RawTrait {\n'
                                          '        public static function make() { return '
                                          "'fresh'; }\n"
                                          '    }\n'
                                          '    function take($a = [Seed, RawTrait::make(...), '
                                          "Seed], $tag = 'default') {\n"
                                          '        return [$a, $tag];\n'
                                          '    }\n'
                                          "    function driver() { return take(tag: 'named'); }\n"
                                          '    $phase = 0;\n'
                                          '    set_error_handler(function ($level, $message) use '
                                          '(&$phase) {\n'
                                          '        ++$phase;\n'
                                          "        echo 'H', $phase, '|';\n"
                                          '        if ($phase === 1) {\n'
                                          "            eval('namespace ParameterGenerationNamed; "
                                          'const Seed = static function () { return "local"; '
                                          "};');\n"
                                          "            throw new \\Exception('stop');\n"
                                          '        }\n'
                                          '        return true;\n'
                                          '    });\n'
                                          '    try { driver(); } catch (\\Exception $e) { echo '
                                          "'stop|'; }\n"
                                          '    $x = driver();\n'
                                          "    echo $x[0][0](), ':', $x[0][2](), ':', $x[0][1](), "
                                          "':', $x[1], ':',\n"
                                          "        ($x[0][0] === $x[0][2] ? 'same' : "
                                          "'different'), ':', $phase;\n"
                                          '}\n',
 'parameter-generation-nested-reentry': '<?php\n'
                                        'namespace {\n'
                                        '    const ParameterGenerationReentrySeed = static '
                                        "function () { return 'global'; };\n"
                                        '    trait ParameterGenerationReentryTrait { public '
                                        "static function target() { return 'trait'; } }\n"
                                        '}\n'
                                        'namespace ParameterGenerationReentry {\n'
                                        '    function take($a = [ParameterGenerationReentrySeed, '
                                        '\\ParameterGenerationReentryTrait::target(...), '
                                        'ParameterGenerationReentrySeed]) { return $a; }\n'
                                        '    function driver() { return take(); }\n'
                                        '    $seen = 0;\n'
                                        '    $inner = [];\n'
                                        '    set_error_handler(function ($n, $m) use (&$seen, '
                                        '&$inner) {\n'
                                        '        ++$seen;\n'
                                        "        echo 'H', $seen, '|';\n"
                                        "        eval('namespace ParameterGenerationReentry; "
                                        'const ParameterGenerationReentrySeed = static function '
                                        '() { return "local"; };\');\n'
                                        '        set_error_handler(function ($n, $m) use (&$seen) '
                                        '{\n'
                                        '            ++$seen;\n'
                                        "            echo 'H', $seen, '|';\n"
                                        '            return true;\n'
                                        '        });\n'
                                        '        $inner = driver();\n'
                                        '        $first = $inner[0];\n'
                                        '        $last = $inner[2];\n'
                                        "        echo 'I:', $first(), ':', $last(), '|';\n"
                                        '        return true;\n'
                                        '    });\n'
                                        '    $outer = driver();\n'
                                        "    echo 'O:';\n"
                                        '    echo $outer[0] === \\ParameterGenerationReentrySeed '
                                        "? 'old:' : 'wrong:';\n"
                                        '    echo $outer[2] === ParameterGenerationReentrySeed ? '
                                        "'new:' : 'wrong:';\n"
                                        "    echo $outer[1] !== $inner[1] ? 'fresh:' : 'same:';\n"
                                        '    $first = $outer[0];\n'
                                        '    $last = $outer[2];\n'
                                        "    echo $first(), ':', $last(), ':', $seen;\n"
                                        '}\n',
 'parameter-generation-deprecated-value-capture': '<?php\n'
                                                  'namespace {\n'
                                                  '    const ParameterGenerationDeprecatedSeed = '
                                                  "static function () { return 'global'; };\n"
                                                  '}\n'
                                                  'namespace ParameterGenerationDeprecated {\n'
                                                  '    function take($a = '
                                                  '[ParameterGenerationDeprecatedSeed, E_STRICT, '
                                                  'ParameterGenerationDeprecatedSeed]) { return '
                                                  '$a; }\n'
                                                  '    set_error_handler(function ($n, $m) {\n'
                                                  "        echo 'H|';\n"
                                                  "        eval('namespace "
                                                  'ParameterGenerationDeprecated; const '
                                                  'ParameterGenerationDeprecatedSeed = static '
                                                  'function () { return "local"; }; const '
                                                  "E_STRICT = 17;');\n"
                                                  '        return true;\n'
                                                  '    });\n'
                                                  '    $a = take();\n'
                                                  '    echo $a[0] === '
                                                  "\\ParameterGenerationDeprecatedSeed ? 'old:' : "
                                                  "'wrong:';\n"
                                                  '    echo $a[2] === '
                                                  "ParameterGenerationDeprecatedSeed ? 'new:' : "
                                                  "'wrong:';\n"
                                                  "    echo $a[1], ':';\n"
                                                  '    $old = $a[0];\n'
                                                  '    $new = $a[2];\n'
                                                  "    echo $old(), ':', $new();\n"
                                                  "    echo '|', E_STRICT;\n"
                                                  '}\n',
 'parameter-generation-deprecated-two-receives': '<?php\n'
                                                 'namespace {\n'
                                                 '    const ParameterGenerationTwiceSeed = static '
                                                 "function () { return 'global'; };\n"
                                                 '}\n'
                                                 'namespace ParameterGenerationDeprecatedTwice {\n'
                                                 '    function take($a = '
                                                 '[ParameterGenerationTwiceSeed, E_STRICT, '
                                                 'ParameterGenerationTwiceSeed]) {\n'
                                                 '        return $a;\n'
                                                 '    }\n'
                                                 '    function driver() { return take(); }\n'
                                                 '    set_error_handler(function ($level, '
                                                 '$message) {\n'
                                                 "        echo 'H|';\n"
                                                 "        eval('namespace "
                                                 'ParameterGenerationDeprecatedTwice; const '
                                                 'ParameterGenerationTwiceSeed = static function '
                                                 '() { return "local"; }; const E_STRICT = '
                                                 "17;');\n"
                                                 '        return true;\n'
                                                 '    });\n'
                                                 '    $first = driver();\n'
                                                 "    echo ($first[0] === $first[2] ? 'same' : "
                                                 "'old:new'), ':', $first[1], ':',\n"
                                                 "        $first[0](), ':', $first[2](), '|';\n"
                                                 '    $second = driver();\n'
                                                 "    echo ($second[0] === $second[2] ? 'same' : "
                                                 "'different'), ':', $second[1], ':',\n"
                                                 "        $second[0](), ':', $second[2]();\n"
                                                 '}\n',
 'parameter-generation-two-frontiers': '<?php\n'
                                       'namespace {\n'
                                       '    const ParameterGenerationMultiFirst = static function '
                                       "() { return 'g1'; };\n"
                                       '    const ParameterGenerationMultiSecond = static '
                                       "function () { return 'g2'; };\n"
                                       '    trait ParameterGenerationMultiTrait {\n'
                                       "        public static function first() { return 'first'; "
                                       '}\n'
                                       '        public static function second() { return '
                                       "'second'; }\n"
                                       '    }\n'
                                       '}\n'
                                       'namespace ParameterGenerationMulti {\n'
                                       '    function take($a = [ParameterGenerationMultiFirst, '
                                       '\\ParameterGenerationMultiTrait::first(...), '
                                       'ParameterGenerationMultiFirst, '
                                       'ParameterGenerationMultiSecond, '
                                       '\\ParameterGenerationMultiTrait::second(...), '
                                       'ParameterGenerationMultiSecond]) { return $a; }\n'
                                       '    $seen = 0;\n'
                                       '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                       '        ++$seen;\n'
                                       "        echo 'H', $seen, '|';\n"
                                       '        if ($seen === 1) {\n'
                                       "            eval('namespace ParameterGenerationMulti; "
                                       'const ParameterGenerationMultiFirst = static function () '
                                       '{ return "l1"; };\');\n'
                                       '        } else {\n'
                                       "            eval('namespace ParameterGenerationMulti; "
                                       'const ParameterGenerationMultiSecond = static function () '
                                       '{ return "l2"; };\');\n'
                                       '        }\n'
                                       '        return true;\n'
                                       '    });\n'
                                       '    $a = take();\n'
                                       '    echo $a[0] === \\ParameterGenerationMultiFirst ? '
                                       "'old1:' : 'wrong:';\n"
                                       '    echo $a[2] === ParameterGenerationMultiFirst ? '
                                       "'new1:' : 'wrong:';\n"
                                       '    echo $a[3] === \\ParameterGenerationMultiSecond ? '
                                       "'old2:' : 'wrong:';\n"
                                       '    echo $a[5] === ParameterGenerationMultiSecond ? '
                                       "'new2:' : 'wrong:';\n"
                                       '    $v0 = $a[0]; $v2 = $a[2]; $v3 = $a[3]; $v5 = $a[5];\n'
                                       "    echo $v0(), ':', $v2(), ':', $v3(), ':', $v5();\n"
                                       '}\n',
 'parameter-generation-parked-fiber': '<?php\n'
                                      'namespace {\n'
                                      '    const ParameterGenerationFiberSeed = static function '
                                      "() { return 'global'; };\n"
                                      '    trait ParameterGenerationFiberTrait { public static '
                                      "function target() { return 'trait'; } }\n"
                                      '}\n'
                                      'namespace ParameterGenerationFiber {\n'
                                      '    function take($a = [ParameterGenerationFiberSeed, '
                                      '\\ParameterGenerationFiberTrait::target(...), '
                                      'ParameterGenerationFiberSeed]) { return $a; }\n'
                                      '    set_error_handler(static function ($n, $m) {\n'
                                      "        echo 'H|';\n"
                                      "        \\Fiber::suspend('paused');\n"
                                      '        return true;\n'
                                      '    });\n'
                                      '    $fiber = new \\Fiber(static function () {\n'
                                      '        $a = take();\n'
                                      '        echo $a[0] === \\ParameterGenerationFiberSeed ? '
                                      "'old:' : 'wrong:';\n"
                                      '        echo $a[2] === ParameterGenerationFiberSeed ? '
                                      "'new:' : 'wrong:';\n"
                                      '        $first = $a[0];\n'
                                      '        $last = $a[2];\n'
                                      "        echo $first(), ':', $last();\n"
                                      '    });\n'
                                      "    echo $fiber->start(), '|';\n"
                                      "    eval('namespace ParameterGenerationFiber; const "
                                      'ParameterGenerationFiberSeed = static function () { return '
                                      '"local"; };\');\n'
                                      "    echo 'P|';\n"
                                      '    $fiber->resume();\n'
                                      '}\n',
 'parameter-object-context-warning': '<?php\n'
                                     'namespace {\n'
                                     '    const ParameterNoticeSeed = static function () { return '
                                     "'global'; };\n"
                                     '    class ParameterNoticeObject {}\n'
                                     '    const ParameterNoticeObjectSeed = new '
                                     'ParameterNoticeObject;\n'
                                     '    trait ParameterNoticeTrait { public static function '
                                     "target() { return 'trait'; } }\n"
                                     '}\n'
                                     'namespace ParameterNotice {\n'
                                     '    function take($a = [\\ParameterNoticeObjectSeed, '
                                     'ParameterNoticeSeed, \\ParameterNoticeTrait::target(...), '
                                     'ParameterNoticeSeed]) { return $a; }\n'
                                     '    $seen = 0;\n'
                                     '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                     '        ++$seen;\n'
                                     "        echo 'H|';\n"
                                     "        eval('namespace ParameterNotice; const "
                                     'ParameterNoticeSeed = static function () { return "local"; '
                                     "};');\n"
                                     '        return true;\n'
                                     '    });\n'
                                     '    $a = take();\n'
                                     '    $b = take();\n'
                                     "    echo $a[0] === \\ParameterNoticeObjectSeed ? 'object:' "
                                     ": 'wrong:';\n"
                                     "    echo $a[1] === \\ParameterNoticeSeed ? 'old:' : "
                                     "'wrong:';\n"
                                     "    echo $a[3] === ParameterNoticeSeed ? 'new:' : "
                                     "'wrong:';\n"
                                     "    echo $b[1] === ParameterNoticeSeed ? 'local:' : "
                                     "'wrong:';\n"
                                     "    echo $a[2] !== $b[2] ? 'fresh:' : 'same:';\n"
                                     "    echo $seen, ':';\n"
                                     '    $old = $a[1];\n'
                                     '    $new = $a[3];\n'
                                     "    echo $old(), ':', $new();\n"
                                     '}\n',
 'parameter-null-key-warning': '<?php\n'
                               'const ParameterBooleanNullSeed = static function () { return '
                               "'donor'; };\n"
                               'function takeBooleanNullKeys($a = [false => '
                               'ParameterBooleanNullSeed, null => [true, false, null], true => '
                               "static function () { return 'fresh'; }]) { return $a; }\n"
                               '$a = takeBooleanNullKeys();\n'
                               '$b = takeBooleanNullKeys();\n'
                               "echo $a[0] === ParameterBooleanNullSeed ? 'same:' : 'wrong:';\n"
                               "echo $a[''] === [true, false, null] ? 'values:' : 'wrong:';\n"
                               "echo $a[1] !== $b[1] ? 'fresh:' : 'same:';\n"
                               '$f = $a[0];\n'
                               '$g = $a[1];\n'
                               "echo $f(), ':', $g();\n"}

OUTPUTS={'parameter-namespace-warning-prefix': 'H|old:new:local:fresh:1:global:local',
 'parameter-namespace-warning-retry': 'H1|stop|H2|local:local:2',
 'parameter-trailing-real-warning': 'H|old:new:local:fresh:1:global:local',
 'parameter-generation-same-site-retry': 'H1|stop|H2|local:local:2',
 'parameter-generation-same-parent-loop': 'H1|stop|H2|local:local:2',
 'parameter-generation-foreign-birth-loop': 'F:global|H1|stop|H2|local:local:2',
 'parameter-generation-named-hole-retry': 'H1|stop|H2|local:local:fresh:named:same:2',
 'parameter-generation-nested-reentry': 'H1|H2|I:local:local|O:old:new:fresh:global:local:2',
 'parameter-generation-deprecated-value-capture': 'H|old:new:2048:global:local|17',
 'parameter-generation-deprecated-two-receives': 'H|old:new:2048:global:local|same:17:local:local'}

EVALS={'parameter-namespace-warning-prefix': ['namespace ParameterNotice; const ParameterNoticeSeed = '
                                        'static function () { return "local"; };'],
 'parameter-namespace-warning-retry': ['namespace ParameterRetry; const ParameterRetrySeed = '
                                       'static function () { return "local"; };'],
 'parameter-trailing-real-warning': ['namespace ParameterNotice; const ParameterNoticeSeed = '
                                     'static function () { return "local"; };'],
 'parameter-generation-same-site-retry': ['namespace ParameterGenerationRetry; const '
                                          'ParameterGenerationRetrySeed = static function () { '
                                          'return "local"; };'],
 'parameter-generation-same-parent-loop': ['namespace ParameterGenerationLoop; const '
                                           'ParameterGenerationLoopSeed = static function () { '
                                           'return "local"; };'],
 'parameter-generation-foreign-birth-loop': ['namespace ParameterGenerationForeign; const '
                                             'ParameterGenerationForeignSeed = static function () '
                                             '{ return "local"; };'],
 'parameter-generation-named-hole-retry': ['namespace ParameterGenerationNamed; const Seed = '
                                           'static function () { return "local"; };'],
 'parameter-generation-nested-reentry': ['namespace ParameterGenerationReentry; const '
                                         'ParameterGenerationReentrySeed = static function () { '
                                         'return "local"; };'],
 'parameter-generation-deprecated-value-capture': ['namespace ParameterGenerationDeprecated; '
                                                   'const ParameterGenerationDeprecatedSeed = '
                                                   'static function () { return "local"; }; const '
                                                   'E_STRICT = 17;'],
 'parameter-generation-deprecated-two-receives': ['namespace ParameterGenerationDeprecatedTwice; '
                                                  'const ParameterGenerationTwiceSeed = static '
                                                  'function () { return "local"; }; const '
                                                  'E_STRICT = 17;'],
 'parameter-generation-two-frontiers': ['namespace ParameterGenerationMulti; const '
                                        'ParameterGenerationMultiFirst = static function () { '
                                        'return "l1"; };',
                                        'namespace ParameterGenerationMulti; const '
                                        'ParameterGenerationMultiSecond = static function () { '
                                        'return "l2"; };'],
 'parameter-generation-parked-fiber': ['namespace ParameterGenerationFiber; const '
                                       'ParameterGenerationFiberSeed = static function () { '
                                       'return "local"; };'],
 'parameter-object-context-warning': ['namespace ParameterNotice; const ParameterNoticeSeed = '
                                      'static function () { return "local"; };']}

PREFIX=donor.PREFIX+r'''
dec $causal_test_saved(pframe*, nat) : (pframe, pframe*)?
def $causal_test_saved(pframe :: pframe_tail*, n_owner) = ((pframe, pframe_tail*))
  -- if $parameter_receive_owner(pframe.CONTEXT) = (n_owner)
def $causal_test_saved(pframe :: pframe_tail*, n_owner) = $causal_test_saved(pframe_tail*, n_owner)
  -- if $parameter_receive_owner(pframe.CONTEXT) =/= (n_owner)
def $causal_test_saved(eps, n_owner) = eps
dec $causal_test_stage(pstate, ptbytes, nat, nat) : bool
def $causal_test_stage(S, ptbytes_name, n_stage, n_owner) = true
  -- if S.COMPLETION = NORMAL
  -- if n_stage = 0 \/ n_stage = 1
  -- if $donor_test_stage(S, ptbytes_name, n_stage)
  -- if $parameter_receive_owner(S.CURRENT) = (n_owner)
def $causal_test_stage(S, ptbytes_name, 2, n_owner) = true
  -- if S.COMPLETION = NORMAL
  -- if $donor_test_function(S, ptbytes_name)
  -- if $parameter_receive_owner(S.CURRENT) = (n_owner)
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if $parameter_receive_frontier(perrorcall.RESUME) =/= eps
def $causal_test_stage(S, ptbytes_name, 4, n_owner) = true
  -- if $causal_test_saved(S.FRAMES, n_owner) = ((pframe, pframe_tail*))
  -- if $parameter_receive_birth(S, n_owner) = (preceivebirth)
  -- if $(|S.USERCONSTANTS| > preceivebirth.PREFIX)
def $causal_test_stage(S, ptbytes_name, 5, n_owner) = true
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.TODO = (EVAL_AWAIT n_unit) :: ptask_tail*
  -- if $causal_test_saved(S.FRAMES, n_owner) =/= eps
def $causal_test_stage(S, ptbytes_name, n_stage, n_owner) = false -- otherwise
dec $causal_test_next(pstate, nat) : pstate
def $causal_test_next(S, 5) = $global_test_resume($drive_steps(S, 1))
  -- if S.COMPLETION = NORMAL
def $causal_test_next(S, 5) = $global_test_service(S)
  -- if S.COMPLETION = SOURCE_PENDING
def $causal_test_next(S, n_stage) = $global_test_next(S)
  -- if n_stage =/= 5
dec $causal_test_seek(pstate, ptbytes, nat, nat, nat) : pstate
def $causal_test_seek(S, ptbytes_name, n_stage, n_owner, n_limit) = S
  -- if $causal_test_stage(S, ptbytes_name, n_stage, n_owner)
def $causal_test_seek(S, ptbytes_name, n_stage, n_owner, n_limit) = $causal_test_seek($causal_test_next(S, n_stage), ptbytes_name, n_stage, n_owner, $nabs($(n_limit - 1)))
  -- if ~$causal_test_stage(S, ptbytes_name, n_stage, n_owner)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = SOURCE_PENDING
dec $causal_test_closed(preceivebirth*) : bool
def $causal_test_closed(eps) = true
def $causal_test_closed(preceivebirth :: preceivebirth_tail*) = (~preceivebirth.ACTIVE /\ $causal_test_closed(preceivebirth_tail*))
'''

CHECKS={}

def function_name(namespace):
    return '$ptascii('+json.dumps(namespace)+') ++ [92] ++ $ptascii("take")'

# Every condition below is reached through the actual driver and checked source.
# Helpers only locate the real receive/bind; they never mint a proof in fixtures.
def finish_checks(output,total,start='S'):
    return premises(f'''
S.COMPLETION = NORMAL
S_bound = $donor_test_step({start})
S_bound.COMPLETION = NORMAL
$parameter_receive_owner(S_bound.CURRENT) = eps
S_done = $global_test_finish(S_bound, 18000)
S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii({json.dumps(output)})
S_done.PARAMETERSEQ = {total} /\\ |S_done.PARAMETERRECEIVES| = {total}
$causal_test_closed(S_done.PARAMETERRECEIVES)
$parameter_receive_state_valid(S_done) /\\ $call_descriptors_valid(S_done)
S_done.DEFAULTCACHE = eps
''')

# Start with the accepted donor source assertions, changing only actual causal
# admission and its observable normal completion on this new source cut.
for case in ('parameter-namespace-warning-prefix','parameter-trailing-real-warning'):
    prior=donor.CHECKS[case]
    stop=prior.index('S.COMPLETION = NORMAL')
    checks=prior[:stop]
    needle='~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)'
    checks[checks.index(needle)]=needle[1:]
    CHECKS[case]=checks
FIRST_CUT=premises(r'''
S.CURRENT = (pcallcontext)
pcallcontext.DEFAULTRECEIVE = (preceiveowner)
preceiveowner.ID = 1 /\ preceiveowner.PREFIX = 1
$parameter_receive_birth(S, 1) = (preceivebirth)
preceivebirth.ACTIVE /\ preceivebirth.PARENT = eps
preceivebirth.PREFIX = 1 /\ preceivebirth.ORIGIN = pconstantcontext.ORIGIN
S.PARAMETERSEQ = 1 /\ |S.PARAMETERRECEIVES| = 1
$parameter_receive_state_valid(S)
porigin_effect = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
$parameter_receive_order(S, preceivebirth, pdefault.ORIGIN, eps, eps) = (preceiveorder)
preceiveorder.EFFECTS = [porigin_effect]
$parameter_receive_cut_at(puserconstant_local.RECEIVES, 1) = (preceivecut)
$parameter_receive_cut_valid(S, preceivebirth, porigin_effect, puserconstant_local, preceivecut)
puserconstant_local.ORIGIN = PORIGIN n_eval pcpath_declaration
S.EVALBINDINGS = [pevalbinding]
pevalbinding.UNIT = n_eval /\ pevalbinding.USERPREFIX = 1
$parameter_receive_cut_at(pevalbinding.RECEIVES, 1) = (preceivecut_ingress)
preceivecut_ingress.CAUSE.UNIT = 0 /\ preceivecut.CAUSE.UNIT = n_eval
preceivecut_ingress.CAUSE.CALLS = preceivecut.CAUSE.CALLS
$parameter_receive_ingress_valid(S, pevalbinding)
$parameter_receive_ingress_prefix(S.EVALBINDINGS, 1, |S.USERCONSTANTS|) = 1
$parameter_receive_registrations_valid(S, preceivebirth, 1, porigin_effect, S.USERCONSTANTS, 0)
$parameter_receive_cut_at([preceivecut, preceivecut, preceivecut], 1) = eps
S_duplicate = S[.USERCONSTANTS = [puserconstant_old, puserconstant_local[.RECEIVES = [preceivecut, preceivecut, preceivecut]]]]
$heap_valid($heap_graph(S_duplicate))
~$parameter_default_transfer_valid(S_duplicate, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_no_cut = S[.USERCONSTANTS = [puserconstant_old, puserconstant_local[.RECEIVES = eps]]]
~$parameter_receive_registrations_valid(S_no_cut, preceivebirth, 1, porigin_effect, S_no_cut.USERCONSTANTS, 0)
~$parameter_default_transfer_valid(S_no_cut, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_no_ingress = S[.EVALBINDINGS = [pevalbinding[.RECEIVES = eps]]]
~$parameter_default_transfer_valid(S_no_ingress, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_forward_bound = S_forward[.PARAMETERRECEIVES = [preceivebirth[.PREFIX = 2]]][.CURRENT = (pcallcontext[.DEFAULTRECEIVE = (preceiveowner[.PREFIX = 2])])]
$constant_value_class_valid(S_forward_bound, PARRAY n_array, pvalueclass_forward)
$heap_valid($heap_graph(S_forward_bound))
~$parameter_receive_ingress_valid(S_forward_bound, pevalbinding)
~$parameter_default_transfer_valid(S_forward_bound, pfunction, 0, PARRAY n_array, pvalueclass_forward)
S_forward_erased = S_forward_bound[.USERCONSTANTS = [puserconstant_old, puserconstant_local[.RECEIVES = eps]]]
~$parameter_receive_registrations_valid(S_forward_erased, preceivebirth[.PREFIX = 2], 1, porigin_effect, S_forward_erased.USERCONSTANTS, 0)
~$parameter_default_transfer_valid(S_forward_erased, pfunction, 0, PARRAY n_array, pvalueclass_forward)
S_fully_erased = S_forward_erased[.EVALBINDINGS = [pevalbinding[.RECEIVES = eps]]]
$constant_value_class_valid(S_fully_erased, PARRAY n_array, pvalueclass_forward)
$heap_valid($heap_graph(S_fully_erased))
$default_context_valid(S_fully_erased, pconstantcontext_forward)
~$parameter_receive_donor_source(S_fully_erased, puserconstant_local[.RECEIVES = eps])
~$parameter_default_transfer_valid(S_fully_erased, pfunction, 0, PARRAY n_array, pvalueclass_forward)
S_erased_birth = S[.PARAMETERRECEIVES = eps]
~$parameter_receive_state_valid(S_erased_birth)
~$parameter_default_transfer_valid(S_erased_birth, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
''')
for case in ('parameter-namespace-warning-prefix','parameter-trailing-real-warning'):
    CHECKS[case]+=FIRST_CUT+finish_checks(OUTPUTS[case],2)

# The retry sources differ in parent invocation, fixed-parent repetition, foreign
# closed receives and named preflight; each locates its own real entry twice.
def retry_checks(namespace,seed,first,second,named=False,foreign=False):
    stage=1 if named else 0
    checks=premises(f'''
ptbytes_function = {function_name(namespace)}
ptbytes_local = $ptascii({json.dumps(namespace)}) ++ [92] ++ $ptascii({json.dumps(seed)})
S_first = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, {first}, 8000)
S_first.CURRENT = (pcallcontext_first)
pcallcontext_first.DEFAULTRECEIVE = (preceiveowner_first)
preceiveowner_first.ID = {first} /\\ preceiveowner_first.PREFIX = 1
$parameter_receive_birth(S_first, {first}) = (preceivebirth_first)
preceivebirth_first.ACTIVE /\\ preceivebirth_first.PARENT = eps
S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_first*
S_first.CONSTCONTEXT = (pconstantcontext_first)
pconstantcontext_first.FACTS = [pconstantfact_first]
pconstantfact_first.LOOKUP = (pconstantlookup_first)
pconstantlookup_first.PREFIX = 1
$parameter_receive_state_valid(S_first) /\\ $call_descriptors_valid(S_first)
S_ingress = $causal_test_seek(S_first, ptbytes_function, 5, {first}, 5000)
S_ingress.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*
pevalcontext.USERPREFIX = 1
$parameter_receive_cut_at(pevalcontext.RECEIVES, {first}) = (preceivecut_ingress)
$eval_state_valid(S_ingress)
S_second = $causal_test_seek(S_ingress, ptbytes_function, 2, {second}, 14000)
$parameter_receive_birth(S_second, {first}) = (preceivebirth_failed)
~preceivebirth_failed.ACTIVE
S_second.CURRENT = (pcallcontext_second)
pcallcontext_second.DEFAULTRECEIVE = (preceiveowner_second)
preceiveowner_second.ID = {second} /\\ preceiveowner_second.PREFIX = 2
$parameter_receive_birth(S_second, {second}) = (preceivebirth_second)
preceivebirth_second.ACTIVE /\\ preceivebirth_second.PARENT = eps
preceivebirth_first.ORIGIN = preceivebirth_second.ORIGIN
$parameter_receive_state_valid(S_second) /\\ $call_descriptors_valid(S_second)
S = $causal_test_seek(S_second, ptbytes_function, {stage}, {second}, 5000)
S.TODO = ({'NAMED_DEFAULT_BIND' if named else 'DEFAULT_BIND'} porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
$user_constant_at(S.USERCONSTANTS, $ptascii({json.dumps(seed)})) = (puserconstant_old)
$user_constant_at(S.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_local)
puserconstant_old.VALUE = POBJECT n_old
puserconstant_local.VALUE = POBJECT n_local
n_old =/= n_local
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_state_valid(S) /\\ $call_descriptors_valid(S)
S.CURRENT = (pcallcontext)
pcallcontext.DEFAULTRECEIVE = (preceiveowner)
$parameter_receive_birth(S, {second}) = (preceivebirth)
porigin_early = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 0, PCFIELD 1])
porigin_late = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 2, PCFIELD 1])
porigin_effect = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_early) = (pconstantfact_early)
$constant_fact_at(pconstantcontext.FACTS, porigin_late) = (pconstantfact_late)
pconstantfact_early.LOOKUP = (pconstantlookup_early)
pconstantfact_late.LOOKUP = (pconstantlookup_late)
pconstantlookup_early.PREFIX = 2 /\\ pconstantlookup_late.PREFIX = 2
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_local.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS)])
$parameter_receive_cut_at(puserconstant_local.RECEIVES, {first}) = (preceivecut_first)
$parameter_receive_cut_at(puserconstant_local.RECEIVES, {second}) = eps
S.EVALBINDINGS = [pevalbinding]
$parameter_receive_cut_at(pevalbinding.RECEIVES, {first}) = (preceivecut_ingress)
$parameter_receive_cut_at(pevalbinding.RECEIVES, {second}) = eps
pconstantfact_rewind = pconstantfact_early[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_early[.PREFIX = 1][.DECL = puserconstant_old.ORIGIN])]
pvalueclass_rewind = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS)])
pconstantcontext_rewind = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_rewind), pconstantfact_root[.CLASS = pvalueclass_rewind])]
S_rewind = S[.CONSTCONTEXT = (pconstantcontext_rewind)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]]
$constant_value_class_valid(S_rewind, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_rewind))
$global_constant_lookup_valid(S_rewind, pconstantcontext.ORIGIN, pconstantfact_rewind, S.USERCONSTANTS)
~$parameter_default_transfer_valid(S_rewind, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
preceivebirth_transplanted = preceivebirth[.PREFIX = 1]
S_transplanted = S_rewind[.PARAMETERRECEIVES = S.PARAMETERRECEIVES[0:{second-1}] ++ [preceivebirth_transplanted]][.CURRENT = (pcallcontext[.DEFAULTRECEIVE = (preceiveowner[.PREFIX = 1])])][.USERCONSTANTS = [puserconstant_old, puserconstant_local[.RECEIVES = [preceivecut_first[.OWNER = {second}]]]]]
$constant_value_class_valid(S_transplanted, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_transplanted))
~$parameter_receive_registrations_valid(S_transplanted, preceivebirth_transplanted, {second}, porigin_effect, S_transplanted.USERCONSTANTS, 0)
~$parameter_default_transfer_valid(S_transplanted, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
S_reopened = S_rewind[.PARAMETERRECEIVES = S.PARAMETERRECEIVES[0:{first-1}] ++ [preceivebirth_failed[.ACTIVE = true]] ++ S.PARAMETERRECEIVES[{first}:$nabs($(|S.PARAMETERRECEIVES| - {first}))]][.CURRENT = (pcallcontext[.DEFAULTRECEIVE = (preceiveowner_first)])]
~$parameter_receive_state_valid(S_reopened)
~$parameter_default_transfer_valid(S_reopened, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
S_closed_tail = S_reopened[.PARAMETERRECEIVES = S_reopened.PARAMETERRECEIVES[0:{second-1}] ++ [preceivebirth[.ACTIVE = false]]]
$constant_value_class_valid(S_closed_tail, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_closed_tail))
$parameter_receive_latest(S_closed_tail.PARAMETERRECEIVES, eps, 1, eps) = ({second})
~$parameter_receive_context_valid(S_closed_tail, S_closed_tail.CURRENT)
~$parameter_receive_state_valid(S_closed_tail)
~$parameter_default_transfer_valid(S_closed_tail, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
S_erased_tail = S_reopened[.PARAMETERRECEIVES = S_reopened.PARAMETERRECEIVES[0:{second-1}]]
~$parameter_receive_state_valid(S_erased_tail)
~$parameter_default_transfer_valid(S_erased_tail, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
''')
    if namespace != 'ParameterRetry':
        checks+=premises('preceivebirth_first.CALLSITE = preceivebirth_second.CALLSITE')
    if named:
        checks+=premises(r'''
pcallcontext.HOLES = [0]
pcallcontext.NAMED = eps
$lookup(S.ENV, $ptascii("tag")) = (n_tag)
S.STORE[n_tag] = DEFINED (PSTRING ($ptascii("named")))
''')
    if foreign:
        checks+=premises(r'''
$parameter_receive_birth(S, 1) = (preceivebirth_foreign)
~preceivebirth_foreign.ACTIVE
preceivebirth_foreign.FUNCTION =/= preceivebirth.FUNCTION
$parameter_receive_named_entry(S, preceivebirth_foreign)
preceivebirth_tail = preceivebirth[.ORIGIN = preceivebirth_foreign.ORIGIN][.FUNCTION = preceivebirth_foreign.FUNCTION][.CALLSITE = preceivebirth_foreign.CALLSITE][.CAUSE = preceivebirth_foreign.CAUSE][.PARENT = (2)][.PARENTINDEX = (1)][.PARENTEDGE = eps][.ACTIVE = false]
S_parent_tail = S_rewind[.PARAMETERRECEIVES = [preceivebirth_foreign, preceivebirth_failed[.ACTIVE = true], preceivebirth_tail]][.CURRENT = (pcallcontext[.DEFAULTRECEIVE = (preceiveowner_first)])]
$parameter_receive_latest(S_parent_tail.PARAMETERRECEIVES, eps, 1, eps) = (2)
$parameter_receive_named_entry(S_parent_tail, preceivebirth_tail)
~$parameter_receive_source_valid(S_parent_tail, preceivebirth_tail)
~$parameter_receive_state_valid(S_parent_tail)
~$call_descriptors_valid(S_parent_tail)
~$parameter_default_transfer_valid(S_parent_tail, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
''')
    return checks

for case,namespace,seed,first,second,named,foreign in (
('parameter-namespace-warning-retry','ParameterRetry','ParameterRetrySeed',1,2,False,False),
('parameter-generation-same-site-retry','ParameterGenerationRetry','ParameterGenerationRetrySeed',1,2,False,False),
('parameter-generation-same-parent-loop','ParameterGenerationLoop','ParameterGenerationLoopSeed',1,2,False,False),
('parameter-generation-foreign-birth-loop','ParameterGenerationForeign','ParameterGenerationForeignSeed',2,3,False,True),
('parameter-generation-named-hole-retry','ParameterGenerationNamed','Seed',1,2,True,False),
):
    CHECKS[case]=retry_checks(namespace,seed,first,second,named,foreign)+finish_checks(OUTPUTS[case],second)

def deprecated_checks(namespace,seed,twice=False):
    checks=premises(f'''
ptbytes_function = {function_name(namespace)}
ptbytes_local = $ptascii({json.dumps(namespace)}) ++ [92] ++ $ptascii({json.dumps(seed)})
S_warning = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 1, 7000)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant
pdeprecatedconstant.PREFIX = 1
$parameter_receive_birth(S_warning, 1) = (preceivebirth_warning)
$parameter_receive_frontier_valid(S_warning, preceivebirth_warning, eps, RECEIVE_DEPRECATED pdeprecatedconstant)
$parameter_receive_state_valid(S_warning) /\\ $call_descriptors_valid(S_warning)
S_ingress = $causal_test_seek(S_warning, ptbytes_function, 5, 1, 5000)
S_ingress.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*
pevalcontext.USERPREFIX = 1
$parameter_receive_cut_at(pevalcontext.RECEIVES, 1) = (preceivecut_ingress)
preceivecut_ingress.FRONTIER = RECEIVE_DEPRECATED pdeprecatedconstant
$eval_state_valid(S_ingress)
S_bad_ingress = S_ingress[.EVALCONTEXTS = pevalcontext[.RECEIVES = eps] :: pevalcontext_tail*]
~$eval_state_valid(S_bad_ingress)
S = $causal_test_seek(S_ingress, ptbytes_function, 0, 1, 9000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 2048)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
$user_constant_at(S.USERCONSTANTS, $ptascii({json.dumps(seed)})) = (puserconstant_old)
$user_constant_at(S.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_local)
puserconstant_old.VALUE = POBJECT n_old /\\ puserconstant_local.VALUE = POBJECT n_local
|S.USERCONSTANTS| = 3 /\\ n_old =/= n_local
S.CONSTCONTEXT = (pconstantcontext)
S.CURRENT = (pcallcontext)
pcallcontext.DEFAULTRECEIVE = (preceiveowner)
preceiveowner.ID = 1 /\\ preceiveowner.PREFIX = 1
$parameter_receive_birth(S, 1) = (preceivebirth)
porigin_effect = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_effect) = (pconstantfact_scalar)
pconstantfact_scalar.VALUE = (PINT 2048) /\\ pconstantfact_scalar.CLASS = PVSCALAR /\\ pconstantfact_scalar.LOOKUP = eps
$global_constant_alias(S, S.USERCONSTANTS, porigin_effect) = (puserconstant_scalar)
puserconstant_scalar.VALUE = PINT 17
$deprecated_constant_source(S, porigin_effect, preceivebirth.PREFIX) = (pdeprecatedconstant.LINE)
$deprecated_constant_source(S, porigin_effect, |S.USERCONSTANTS|) = eps
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$parameter_receive_payload(S, pdefault.ORIGIN, PARRAY n_array, porigin_effect, eps) = (PINT 2048)
$parameter_receive_effect_value(S, preceivebirth, porigin_effect)
$parameter_receive_cut_at(puserconstant_local.RECEIVES, 1) = (preceivecut)
preceivecut.FRONTIER = RECEIVE_DEPRECATED pdeprecatedconstant
$parameter_receive_cut_valid(S, preceivebirth, porigin_effect, puserconstant_local, preceivecut)
$parameter_receive_cut_valid(S, preceivebirth, porigin_effect, puserconstant_scalar, preceivecut)
$parameter_receive_registrations_valid(S, preceivebirth, 1, porigin_effect, S.USERCONSTANTS, 0)
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_state_valid(S) /\\ $call_descriptors_valid(S)
S_payload = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]]
$constant_value_class_valid(S_payload, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_payload))
~$parameter_receive_effect_value(S_payload, preceivebirth, porigin_effect)
~$parameter_default_transfer_valid(S_payload, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
pconstantcontext_scalar = pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS, pconstantfact_scalar[.VALUE = (PINT 17)])]
S_scalar = S_payload[.CONSTCONTEXT = (pconstantcontext_scalar)]
$constant_fact_value_valid(pconstantfact_scalar[.VALUE = (PINT 17)])
$default_context_valid(S_scalar, pconstantcontext_scalar)
$constant_value_class_valid(S_scalar, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_scalar))
~$parameter_receive_effect_value(S_scalar, preceivebirth, porigin_effect)
~$parameter_default_transfer_valid(S_scalar, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_wrong_frontier = S[.USERCONSTANTS = [puserconstant_old, puserconstant_local[.RECEIVES = [preceivecut[.FRONTIER = RECEIVE_DEPRECATED (pdeprecatedconstant[.PREFIX = 3])]]], puserconstant_scalar]]
~$parameter_default_transfer_valid(S_wrong_frontier, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
''')
    if twice:
        checks+=premises(r'''
S_bound_first = $donor_test_step(S)
S_bound_first.COMPLETION = NORMAL
$parameter_receive_birth(S_bound_first, 1) = (preceivebirth_closed)
~preceivebirth_closed.ACTIVE
S_again = $causal_test_seek(S_bound_first, ptbytes_function, 0, 2, 16000)
$parameter_receive_birth(S_again, 2) = (preceivebirth_again)
preceivebirth_again.PREFIX = 3 /\ preceivebirth_again.ACTIVE
S_again.RESULT = KNOWN (PARRAY n_again)
S_again.ARRAYS[n_again].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
$global_test_output(S_again.EVENTS) = $ptascii("H|old:new:2048:global:local|")
$deprecated_constant_source(S_again, porigin_effect, preceivebirth_again.PREFIX) = eps
$deprecated_constant_source(S_again, porigin_effect, 0) =/= eps
S_again.CONSTCONTEXT = (pconstantcontext_again)
$constant_fact_at(pconstantcontext_again.FACTS, porigin_effect) = (pconstantfact_again)
pconstantfact_again.VALUE = (PINT 17)
$constant_fact_at(pconstantcontext_again.FACTS, pdefault.ORIGIN) = (pconstantfact_root_again)
$parameter_receive_effect_value(S_again, preceivebirth_again, porigin_effect)
$parameter_default_transfer_valid(S_again, pfunction, 0, PARRAY n_again, pconstantfact_root_again.CLASS)
$parameter_receive_state_valid(S_again) /\ $call_descriptors_valid(S_again)
S_again_payload = S_again[.ARRAYS[n_again].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (PINT 2048)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]]
~$parameter_receive_effect_value(S_again_payload, preceivebirth_again, porigin_effect)
~$parameter_default_transfer_valid(S_again_payload, pfunction, 0, PARRAY n_again, pconstantfact_root_again.CLASS)
''')
    return checks

CHECKS['parameter-generation-deprecated-value-capture']=deprecated_checks('ParameterGenerationDeprecated','ParameterGenerationDeprecatedSeed')+finish_checks(OUTPUTS['parameter-generation-deprecated-value-capture'],1)
CHECKS['parameter-generation-deprecated-two-receives']=deprecated_checks('ParameterGenerationDeprecatedTwice','ParameterGenerationTwiceSeed',True)+finish_checks(OUTPUTS['parameter-generation-deprecated-two-receives'],2,'S_again')

CHECKS['parameter-generation-nested-reentry']=premises(r'''
ptbytes_function = $ptascii("ParameterGenerationReentry") ++ [92] ++ $ptascii("take")
S_first = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 1, 8000)
$parameter_receive_birth(S_first, 1) = (preceivebirth_first)
preceivebirth_first.PARENT = eps /\ preceivebirth_first.ACTIVE
S_inner_warning = $causal_test_seek(S_first, ptbytes_function, 2, 2, 14000)
$parameter_receive_birth(S_inner_warning, 2) = (preceivebirth_inner)
preceivebirth_inner.PARENT = (1) /\ preceivebirth_inner.PREFIX = 2
preceivebirth_inner.PARENTINDEX = (3)
preceivebirth_inner.PARENTEDGE = (preceiveedge)
$parameter_receive_source_valid(S_inner_warning, preceivebirth_inner)
$parameter_receive_state_valid(S_inner_warning) /\ $call_descriptors_valid(S_inner_warning)
$causal_test_saved(S_inner_warning.FRAMES, 1) = ((pframe_outer, pframe_outer_tail*))
pframe_outer.TODO = (ERROR_HANDLER_RESULT perrorcall_outer) :: ptask_outer*
$parameter_receive_frontier(perrorcall_outer.RESUME) = (preceiveedge.FRONTIER)
$parameter_receive_ids_valid(S_inner_warning, [2, 1])
~$parameter_receive_ids_valid(S_inner_warning, [2, 2, 1])
S_inner = $causal_test_seek(S_inner_warning, ptbytes_function, 0, 2, 7000)
S_inner.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_inner*
$function_at($all_functions(S_inner), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S_inner.RESULT = KNOWN (PARRAY n_inner)
S_inner.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_method_inner)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
S_inner.CONSTCONTEXT = (pconstantcontext_inner)
$constant_fact_at(pconstantcontext_inner.FACTS, pdefault.ORIGIN) = (pconstantfact_inner_root)
$parameter_default_transfer_valid(S_inner, pfunction, 0, PARRAY n_inner, pconstantfact_inner_root.CLASS)
$parameter_receive_state_valid(S_inner) /\ $call_descriptors_valid(S_inner)
S_no_parent = S_inner[.PARAMETERRECEIVES = [preceivebirth_first, preceivebirth_inner[.PARENT = eps][.PARENTINDEX = eps][.PARENTEDGE = eps]]]
~$parameter_receive_state_valid(S_no_parent)
~$parameter_default_transfer_valid(S_no_parent, pfunction, 0, PARRAY n_inner, pconstantfact_inner_root.CLASS)
S_inner.CURRENT = (pcallcontext_inner)
S_wrong_edge = S_inner[.PARAMETERRECEIVES = [preceivebirth_first, preceivebirth_inner[.PARENTEDGE = (preceiveedge[.HANDLER = pcallcontext_inner.FUNCTION])]]]
~$parameter_receive_source_valid(S_wrong_edge, preceivebirth_inner[.PARENTEDGE = (preceiveedge[.HANDLER = pcallcontext_inner.FUNCTION])])
~$parameter_default_transfer_valid(S_wrong_edge, pfunction, 0, PARRAY n_inner, pconstantfact_inner_root.CLASS)
S_inner_bound = $donor_test_step(S_inner)
S_inner_bound.COMPLETION = NORMAL
$parameter_receive_birth(S_inner_bound, 2) = (preceivebirth_inner_closed)
~preceivebirth_inner_closed.ACTIVE
$parameter_receive_birth(S_inner_bound, 1) = (preceivebirth_outer_live)
preceivebirth_outer_live.ACTIVE
S = $causal_test_seek(S_inner_bound, ptbytes_function, 0, 1, 14000)
S.PARAMETERSEQ = 2 /\ |S.PARAMETERRECEIVES| = 2
S.RESULT = KNOWN (PARRAY n_outer)
S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method_outer)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
n_outer =/= n_inner /\ n_method_inner =/= n_method_outer /\ n_old =/= n_local
$global_test_output(S.EVENTS) = $ptascii("H1|H2|I:local:local|")
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_outer, pconstantfact_root.CLASS)
$parameter_receive_state_valid(S) /\ $call_descriptors_valid(S)
''')+finish_checks(OUTPUTS['parameter-generation-nested-reentry'],2)

CHECKS['parameter-object-context-warning']=donor.CHECKS['parameter-object-context-warning'][:]
stop=CHECKS['parameter-object-context-warning'].index('S.COMPLETION = NORMAL')
CHECKS['parameter-object-context-warning'][stop:stop]=premises(r'''
$parameter_receive_birth(S, 1) = (preceivebirth)
$parameter_receive_order(S, preceivebirth, pdefault.ORIGIN, eps, eps) = (preceiveorder)
|preceiveorder.EFFECTS| = 1
$parameter_receive_state_valid(S)
''')

CHECKS['parameter-generation-two-frontiers']=premises(r'''
ptbytes_function = $ptascii("ParameterGenerationMulti") ++ [92] ++ $ptascii("take")
S = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 0, 1, 16000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_birth(S, 1) = (preceivebirth)
$parameter_receive_order(S, preceivebirth, pdefault.ORIGIN, eps, eps) = (preceiveorder)
preceiveorder.EFFECTS = [porigin_first, porigin_second]
porigin_first =/= porigin_second
$global_test_output(S.EVENTS) = $ptascii("H1|H2|")
$parameter_receive_state_valid(S) /\ $call_descriptors_valid(S)
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_transition = $donor_test_step(S)
S_transition.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transition, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H1|H2|")
S_stop.DEFAULTCACHE = eps
''')

CHECKS['parameter-null-key-warning']=premises(r'''
S = $causal_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeBooleanNullKeys"), 0, 1, 7000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
$parameter_receive_birth(S, 1) = (preceivebirth)
S.RESULT = KNOWN (PARRAY n_array)
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_order(S, preceivebirth, pdefault.ORIGIN, eps, eps) = eps
~$parameter_callable_quiet_key_value((PNULL))
$parameter_receive_state_valid(S)
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_transition = $donor_test_step(S)
S_transition.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transition, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop.DEFAULTCACHE = eps
''')

PREFIX=PREFIX.replace('def $causal_test_stage(S, ptbytes_name, n_stage, n_owner) = false -- otherwise',r'''
def $causal_test_stage(S, ptbytes_name, 6, n_owner) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND
  -- if $causal_test_saved(S.FRAMES, n_owner) =/= eps
def $causal_test_stage(S, ptbytes_name, n_stage, n_owner) = false -- otherwise
''')
CHECKS['parameter-generation-parked-fiber']=premises(r'''
S = $causal_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii(""), 6, 1, 14000)
S.ACTIVEFIBER = (n_fiber)
S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND
$causal_test_saved(S.FRAMES, 1) = ((pframe, pframe_tail*))
pframe.CONSTCONTEXT = (pconstantcontext)
$parameter_receive_birth(S, 1) = (preceivebirth)
preceivebirth.ACTIVE
pconstantcontext.ORIGIN = preceivebirth.ORIGIN
$parameter_receive_state_valid(S) /\ $call_descriptors_valid(S)
~$fiber_transfer_domain(S)
$global_test_output(S.EVENTS) = $ptascii("H|")
S_transition = $donor_test_step(S)
S_transition.COMPLETION = UNSUPPORTED "Fiber switch during an initializer, source loader or Generator continuation"
S_stop = $drive_steps(S_transition, 40)
S_stop.COMPLETION = UNSUPPORTED "Fiber switch during an initializer, source loader or Generator continuation"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
''')

# Keep publication/callable boundary controls separate from normal source credit.

SOURCES["parameter-generation-outside-eval-donor"]='<?php\nnamespace {\n    const ParameterGenerationOutsideBase = static function () { return \'global\'; };\n    trait ParameterGenerationOutsideTrait {\n        public static function target() { return \'fresh\'; }\n    }\n}\nnamespace ParameterGenerationOutside {\n    eval(\'namespace { const ParameterGenerationOutsideSeed = \\\\ParameterGenerationOutsideBase; }\');\n    function take($a = [ParameterGenerationOutsideSeed, \\ParameterGenerationOutsideTrait::target(...), ParameterGenerationOutsideSeed]) {\n        return $a;\n    }\n    set_error_handler(function ($level, $message) {\n        echo \'H|\';\n        eval(\'namespace ParameterGenerationOutside; const ParameterGenerationOutsideSeed = static function () { return "local"; };\');\n        return true;\n    });\n    $a = take();\n    echo ($a[0] === \\ParameterGenerationOutsideBase ? \'borrowed\' : \'wrong\'), \':\',\n        $a[0](), \':\', $a[2](), \':\', $a[1]();\n}\n'
EVALS["parameter-generation-outside-eval-donor"]=['namespace { const ParameterGenerationOutsideSeed = \\ParameterGenerationOutsideBase; }', 'namespace ParameterGenerationOutside; const ParameterGenerationOutsideSeed = static function () { return "local"; };']
CHECKS['parameter-generation-outside-eval-donor']=premises(r'''
ptbytes_function = $ptascii("ParameterGenerationOutside") ++ [92] ++ $ptascii("take")
S = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 0, 1, 14000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterGenerationOutsideSeed")) = (puserconstant_outside)
puserconstant_outside.ORIGIN = PORIGIN 1 pcpath_outside
puserconstant_outside.CLASS = PVCLOSURE n_maker (PORIGIN 0 pcpath_maker)
puserconstant_outside.RECEIVES = eps
$eval_binding_at(S.EVALBINDINGS, 1) = (pevalbinding_outside)
pevalbinding_outside.RECEIVES = eps
$parameter_receive_ingress_valid(S, pevalbinding_outside)
~$parameter_receive_donor_source(S, puserconstant_outside)
$parameter_receive_birth(S, 1) = (preceivebirth)
preceivebirth.PREFIX = 2
$parameter_receive_order(S, preceivebirth, pdefault.ORIGIN, eps, eps) = (preceiveorder)
|preceiveorder.EFFECTS| = 1
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_state_valid(S) /\ $call_descriptors_valid(S)
$global_test_output(S.EVENTS) = $ptascii("H|")
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_transition = $donor_test_step(S)
S_transition.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transition, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
S_stop.DEFAULTCACHE = eps
''')

NORMAL_CASES=tuple(OUTPUTS)
BOUNDARY_CASES=tuple(case for case in SOURCES if case not in OUTPUTS)
assert set(CHECKS)==set(SOURCES)

def prepare(out):
    names=('SOURCES','FILES','EVALS','PREFIX','CHECKS')
    saved={name:getattr(global_protocol,name) for name in names}
    try:
        for name in names:setattr(global_protocol,name,globals()[name])
        return global_protocol.prepare(out)
    finally:
        for name,value in saved.items():setattr(global_protocol,name,value)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only');parser.add_argument('--output')
    arguments=parser.parse_args()
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='parameter-alias-causality-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        original=base.prepare;original_flags=base.RUNNER_FLAGS
        try:
            base.prepare=lambda path:[row for row in prepare(path) if row['id']!='parameter-generation-two-frontiers']
            base.RUNNER_FLAGS={name:['--sl'] for name in SOURCES}
            base.run(out)
        finally:
            base.prepare=original;base.RUNNER_FLAGS=original_flags
        report=json.loads((out/'report.json').read_text())
        report.update(superseded_multiple_frontier_case='parameter-generation-two-frontiers',
                      replacement_protocol='tests/semantics/parameter_multiple_frontier_protocol.py')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out)

if __name__=='__main__':main()
