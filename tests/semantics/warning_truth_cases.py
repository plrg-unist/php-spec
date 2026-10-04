"""Original-null decisions across source warning callbacks; casts stay pending."""

CASES = [
    ('if-and-elseif-original-null', b'''<?php
error_reporting(0);
$seen = 0;
set_error_handler(function($severity, $message, $file, $line) use (&$seen) {
    $seen++;
    $GLOBALS['condition209'] = 7;
}, 2);
if ($condition209) { echo 'BAD'; }
elseif ($condition209) { echo 'T'; }
else { echo 'BAD'; }
unset($condition209);
if (false) { echo 'BAD'; }
elseif ($condition209) { echo 'BAD'; }
else { echo 'E'; }
echo ':', $condition209, ':', $seen;
restore_error_handler();
''', b'TE:7:2', 'normal'),
    ('while-do-for-original-null', b'''<?php
error_reporting(0);
$seen = 0;
set_error_handler(function($severity, $message, $file, $line) use (&$seen) {
    $seen++;
    $GLOBALS['while209'] = 7;
    $GLOBALS['do209'] = 7;
    $GLOBALS['for209'] = 7;
    echo func_num_args(), ';';
}, 2);
while ($while209) { echo 'BAD'; }
echo 'W:', $while209, ';';
unset($do209);
do { echo 'D'; } while ($do209);
echo ':', $do209, ';';
unset($for209);
for ($i = 0; false, $for209; $i++) { echo 'BAD'; }
echo 'F:', $for209, ':', $i, ':', $seen;
restore_error_handler();
''', b'4;W:7;D4;:7;4;F:7:0:3', 'normal'),
    ('while-back-edge-original-null', b'''<?php
error_reporting(0);
$seen = 0;
$loop209 = 1;
set_error_handler(function() use (&$seen) {
    $seen++;
    $GLOBALS['loop209'] = 7;
}, 2);
while ($loop209) {
    echo 'B';
    unset($loop209);
}
echo '|', $loop209, ':', $seen;
restore_error_handler();
''', b'B|7:1', 'normal'),
    ('boolean-short-left-and-right', b'''<?php
error_reporting(0);
$seen = 0;
$effect = 0;
set_error_handler(function() use (&$seen) {
    $seen++;
    $GLOBALS['left209'] = 7;
    $GLOBALS['right209'] = 7;
}, 2);
$r = $left209 && ($effect = 9);
echo ($r ? 'BAD' : 'F'), ':', $effect, ';';
unset($left209);
$r = $left209 || ($effect = 3);
echo ($r ? 'T' : 'BAD'), ':', $effect, ';';
unset($right209);
$gate = true;
$r = $gate && $right209;
echo ($r ? 'BAD' : 'F'), ':', $right209, ';';
unset($right209);
$gate = false;
$r = $gate || $right209;
echo ($r ? 'BAD' : 'F'), ':', $right209, ':', $seen;
restore_error_handler();
''', b'F:0;T:3;F:7;F:7:4', 'normal'),
    ('keyword-short-left-and-right', b'''<?php
error_reporting(0);
$seen = 0;
$effect = 0;
set_error_handler(function() use (&$seen) {
    $seen++;
    $GLOBALS['left209'] = 7;
    $GLOBALS['right209'] = 7;
}, 2);
$r = ($left209 and ($effect = 9));
echo ($r ? 'BAD' : 'F'), ':', $effect, ';';
unset($left209);
$r = ($left209 or ($effect = 3));
echo ($r ? 'T' : 'BAD'), ':', $effect, ';';
unset($right209);
$gate = 1;
$r = ($gate and $right209);
echo ($r ? 'BAD' : 'F'), ':', $right209, ';';
unset($right209);
$gate = 0;
$r = ($gate or $right209);
echo ($r ? 'BAD' : 'F'), ':', $right209, ':', $seen;
restore_error_handler();
''', b'F:0;T:3;F:7;F:7:4', 'normal'),
    ('ternary-condition-original-null', b'''<?php
error_reporting(0);
$seen = 0;
set_error_handler(function() use (&$seen) {
    $seen++;
    $GLOBALS['ternary209'] = 7;
}, 2);
$r = $ternary209 ? 'BAD' : 'F';
echo $r, ':', $ternary209, ';';
unset($ternary209);
$r = $ternary209 ?: 'S';
echo $r, ':', $ternary209, ':', $seen;
restore_error_handler();
''', b'F:7;S:7:2', 'normal'),
    ('throw-suppresses-truth-consumers', b'''<?php
error_reporting(0);
$seen = 0;
$r = 9;
$handler = function($severity, $message, $file, $line) use (&$seen) {
    $seen++;
    throw new Error('truth-stop');
};
set_error_handler($handler, 2);
try { if ($missing_if) { echo 'BAD'; } else { echo 'BAD'; } }
catch (Error $e) { echo 'C;'; }
try { $r = true && $missing_bool; echo 'BAD'; }
catch (Error $e) { echo 'B;'; }
try { do { echo 'D;'; } while ($missing_loop); echo 'BAD'; }
catch (Error $e) { echo 'L;'; }
try { $r = $missing_ternary ? 'BAD' : 'BAD'; echo 'BAD'; }
catch (Error $e) { echo 'E;'; }
echo $r, ':', $seen, ':', (get_error_handler() === $handler ? 1 : 0);
restore_error_handler();
''', b'C;B;D;L;E;9:4:1', 'normal'),
    ('no-handler-and-truth-mask-miss', b'''<?php
error_reporting(0);
if ($no_handler209) { echo 'BAD'; } else { echo 'F;'; }
$seen = 0;
set_error_handler(function() use (&$seen) { $seen++; }, 512);
$r = !$missing_not209;
echo ($r ? 'T' : 'BAD'), ';';
$r = $missing_short209 || false;
echo ($r ? 'BAD' : 'F'), ':', $seen;
restore_error_handler();
''', b'F;T;F:0', 'normal'),
    ('cast-warning-ingress-pending', b'''<?php
error_reporting(0);
set_error_handler(function() { echo 'H'; }, 2);
$r = (bool) $missing_cast209;
echo ($r ? 'BAD' : 'F');
restore_error_handler();
''', b'HF', 'unsupported'),
]
