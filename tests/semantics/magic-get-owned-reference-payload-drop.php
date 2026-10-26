<?php
class OwnedPayloadParent128 {
    private $ghost = null;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return payloadReferenceFactory128()->ghost; // READ128
    }
}
class OwnedPayloadChild128 extends OwnedPayloadParent128 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() {
        global $slot, $replacement;
        echo 'D|';
        $slot = null;
        echo 'd|';
        throw $replacement;
    }
}
class OwnedReferencePayload128 {
    public function __destruct() { global $cleanup; echo 'P|'; throw $cleanup; }
}
function payloadReferenceFactory128() {
    $receiver = new OwnedPayloadChild128();
    $receiver->clear();
    return $receiver;
}
$replacement = new Exception('receiver');
$cleanup = new Exception('payload');
$slot = new OwnedReferencePayload128();
$result = 42;
echo 'P:';
try { $result = OwnedPayloadParent128::readOwned(); echo 'bad|'; }
catch (Exception $caught) {
    echo $caught === $cleanup ? 'sameC|' : 'bad-identity|';
    echo $caught->getPrevious() === $replacement ? 'previousH|' : 'bad-previous|';
    echo $replacement->getPrevious() === null ? 'rootH|' : 'bad-root|';
    echo $result, '|';
    echo $slot === null ? 'null|' : 'bad|';
}
unset($result, $slot, $caught, $replacement, $cleanup);
echo 'E|';
