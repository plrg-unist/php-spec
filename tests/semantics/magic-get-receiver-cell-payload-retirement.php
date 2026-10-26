<?php
class CellCopyPayload131 { function __destruct() { global $replacementC; echo 'P|'; throw $replacementC; } }
class CellCopyTarget131 {
    public $ghost = null;
    function clear() { $self = $this; unset($self->ghost); }
    function &__get($name) { global $slot; echo 'G|'; return $slot; }
    function __destruct() { global $slot, $replacementH; echo 'D|'; $slot = null; echo 'd|'; throw $replacementH; }
}
function &cellCopyFactory131() { $receiver = new CellCopyTarget131; $receiver->clear(); echo 'F|'; return $receiver; }
$replacementH = new Exception('H');
$replacementC = new Exception('C');
$slot = new CellCopyPayload131;
$result = 42;
echo 'P:';
try { $result = cellCopyFactory131()->ghost; } // READ131
catch (Exception $error) {
    echo $error === $replacementC ? 'sameC|' : 'bad-error|';
    echo $error->getPrevious() === $replacementH ? 'previousH|' : 'bad-previous|', $replacementH->getPrevious() === null ? 'rootH|' : 'bad-root|';
    echo $result === 42 ? '42|' : 'bad-store|', $slot === null ? 'null|' : 'bad-source|';
}
unset($error, $result, $slot, $replacementH, $replacementC);
echo 'Z|';
