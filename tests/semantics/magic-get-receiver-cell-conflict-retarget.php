<?php
class CellConflictHolder131 { public string $value = '7'; }
class CellConflictTarget131 {
    public int $ghost = 0;
    function clear() { $self = $this; unset($self->ghost); }
    function &__get($name) { global $receiver, $slot; echo 'G|'; $receiver = null; return $slot; }
    function __destruct() { global $slot, $replacement; echo 'D|', $slot === '7' ? 'kept7|' : 'bad-source|'; $slot = '8'; echo 'd|'; throw $replacement; }
}
function &cellConflictFactory131() { global $receiver; echo 'F|'; return $receiver; }
$slot = '7';
$holder = new CellConflictHolder131;
$holder->value =& $slot;
$replacement = new Exception('H');
$receiver = new CellConflictTarget131;
$receiver->clear();
$result = 42;
echo 'C:';
try { $result = cellConflictFactory131()->ghost; } // READ131
catch (Exception $error) {
    echo $error === $replacement ? 'same|' : 'bad-error|';
    $previous = $error->getPrevious();
    echo $previous instanceof TypeError ? 'typed|' : 'bad-previous|';
    echo $previous->getMessage() === 'Reference with value of type string held by property CellConflictHolder131::$value of type string is not compatible with property CellConflictTarget131::$ghost of type int' ? 'message|' : 'bad-message|';
    echo $previous->getLine() === 18 ? 'line|' : 'bad-line|', $previous->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result === 42 ? '42|' : 'bad-store|', $slot === '8' ? 'cell8|' : 'bad-source|', $receiver === null ? 'null|' : 'bad-receiver|';
}
unset($error, $previous, $result, $holder, $receiver, $replacement, $slot);
echo 'Z|';
