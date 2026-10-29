"""Frozen source for reached ErrorException severity comparisons."""

CASES = {
    'state-severity': br'''<?php
class TailSeverity144 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
$a = new ErrorException('same', 7, 3, 'f.php', 9); $b = new ErrorException('same', 7, 4, 'f.php', 9); $c = new ErrorException('same', 7, 3, 'f.php', 9);
echo 'B|', $a<=>$b, '|';
$sa = $a->__toString(); $sb = $b->__toString(); $c->__toString();
echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
echo 'A|', [0,$a,new TailSeverity144]<=>[0,$b,'x'], '|';
''',
}
