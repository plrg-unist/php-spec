<?php
class ThisConflictHolder129 { public string $value = '7'; }
class ThisConflictParent129 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readThis() {
        global $owner;
        $owner = null;
        echo 'r|';
        $value = $this->ghost; // READ129
        echo 'bad-read|';
        return $value;
    }
}
class ThisConflictChild129 extends ThisConflictParent129 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() { global $slot, $replacement; echo 'D|', $slot === '7' ? 'kept7|' : 'bad-write|'; $slot = '8'; throw $replacement; }
}
$holder = new ThisConflictHolder129();
$slot =& $holder->value;
$replacement = new Exception('replace');
$owner = new ThisConflictChild129();
$owner->clear();
$result = 42;
echo 'C:';
try { $result = $owner->readThis(); }
catch (Throwable $caught) {
    $previous = $caught->getPrevious();
    echo $caught === $replacement ? 'same|' : 'bad-identity|', $previous instanceof TypeError ? 'typed|' : 'bad-previous|';
    echo $previous->getMessage() === 'Reference with value of type string held by property ThisConflictHolder129::$value of type string is not compatible with property ThisConflictParent129::$ghost of type int' ? 'message|' : 'bad-message|';
    echo $previous->getLine() === 10 ? 'line|' : 'bad-line|', $previous->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result === 42 ? '42|' : 'bad-result|', $holder->value === '8' ? 'held8|' : 'bad-source|', $owner === null ? 'null|' : 'bad-owner|';
}
unset($owner, $caught, $previous, $holder, $slot, $replacement, $result);
echo 'E|';
