<?php
class OwnedConflictParent128 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return conflictReferenceFactory128()->ghost; // READ128
    }
}
class OwnedConflictChild128 extends OwnedConflictParent128 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() {
        global $slot, $replacement;
        echo 'D|';
        echo $slot === '7' ? 'kept7|' : 'bad-source|';
        $slot = '8';
        throw $replacement;
    }
}
class OwnedConflictHolder128 { public string $value = '7'; }
function conflictReferenceFactory128() {
    $receiver = new OwnedConflictChild128();
    $receiver->clear();
    return $receiver;
}
$holder = new OwnedConflictHolder128();
$slot =& $holder->value;
$replacement = new Exception('replacement');
$result = 42;
echo 'C:';
try { $result = OwnedConflictParent128::readOwned(); echo 'bad|'; }
catch (Exception $caught) {
    echo $caught === $replacement ? 'same|' : 'bad-identity|';
    $previous = $caught->getPrevious();
    if ($previous instanceof TypeError) {
        echo 'typed|';
        echo $previous->getMessage() === 'Reference with value of type string held by property OwnedConflictHolder128::$value of type string is not compatible with property OwnedConflictParent128::$ghost of type int' ? 'message|' : 'bad-message|';
        echo $previous->getLine() === 6 ? 'line|' : 'bad-line|';
        echo $previous->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    } else { echo 'bad-type|'; }
    echo $result, '|';
    echo $holder->value === '8' ? 'held8|' : 'bad|';
}
unset($result, $slot, $holder, $caught, $previous, $replacement);
echo 'E|';
