<?php
class LeftLine { public function __toString() { $e = new Exception('left'); echo 'L:', $e->getTraceAsString(), '|'; return 'left'; } }
class RightLine { public function __toString() { $e = new Exception('right'); echo 'R:', $e->getTraceAsString(), '|'; return 'right'; } } class HolderLine { public $piece; }
$left = new LeftLine; $holder = new HolderLine; $holder->piece = new RightLine;
echo "{$left}{$holder
    ->piece}", '|END';
