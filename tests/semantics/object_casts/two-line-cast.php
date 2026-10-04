<?php
class LeftLine { public function __toString() { $e = new Exception('left'); echo 'L:', $e->getTraceAsString(), '|'; return 'left'; } }
class RightLine { public function __toString() { $e = new Exception('right'); echo 'R:', $e->getTraceAsString(), '|'; return 'right'; } }
$left = new LeftLine; $holder = (object) ['piece' => new RightLine];
echo "{$left}{$holder
    ->piece}", '|END';
