"""Independent frozen capture/Previous recurrence, used for reached-state checks.

Original SHA256 33f786bb049d1c5af9ae64eb590e1611ded1c0ed6cc748f21d4e60bc0cf1d688;
its retained native observation is reused, with no duplicate source agreement.
"""

CASES = {
    'captured-previous-active-before-prefix': br'''<?php
function outer154($x): Exception { return new Exception('A', 7); }
function bridge154(): TypeError { global $previous154; return new TypeError('B', 7, $previous154); }
$left = null; $right = null;
$a = outer154([&$left]); $b = outer154([&$right]);
$opposite = new Exception('C', 7);
$previous154 = $a; $left = bridge154(); $previous154 = $opposite; $right = bridge154();
echo 'B|'; $hold = 'hold'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } } catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int) ($e->getFile() === __FILE__), ':', (int) ($e->getLine() === $site), ':', (int) ($e->getTrace() === []), '|'; }
$right = $left; echo 'I|', $a <=> $b, ':', (int) ($a == $b), '|';
''',
}
