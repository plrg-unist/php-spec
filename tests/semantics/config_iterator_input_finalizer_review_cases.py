"""A sole temporary Iterator finalizes before its copied prefix on key throw."""

NAME = 'config-input-finalizer-peer-saved-key-prefix'
CASES = {NAME: br'''<?php
class PeerPayload70 {
    public function __destruct() {
        echo 'P:', (int)($GLOBALS['iteratorWatch']->get() === null), ';';
    }
}
class PeerTempIterator70 implements Iterator {
    public int $i = 0;
    public function rewind(): void { echo 'W;'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, ';'; return $this->i < 2; }
    public function current(): mixed {
        echo 'C', $this->i, ';';
        if ($this->i === 0) {
            $payload = new PeerPayload70;
            $GLOBALS['payloadWatch'] = WeakReference::create($payload);
            return $payload;
        }
        return 'unused';
    }
    public function key(): mixed {
        echo 'K', $this->i, ';';
        if ($this->i === 1) { throw $GLOBALS['saved']; }
        return $this->i;
    }
    public function next(): void { echo 'N', $this->i, ';'; ++$this->i; }
    public function __destruct() {
        echo 'D:', (int)($GLOBALS['payloadWatch']->get() !== null), ';';
    }
}
function makePeerTempIterator70() {
    echo 'M;';
    $iterator = new PeerTempIterator70;
    $GLOBALS['iteratorWatch'] = WeakReference::create($iterator);
    return $iterator;
}
$iteratorWatch = null; $payloadWatch = null;
$saved = new Exception('peer-temp-input70'); $result = 99;
echo 'B;';
try { $result = ini_set(...makePeerTempIterator70()); echo 'BAD;'; }
catch (Exception $e) {
    echo 'E:', (int)($e === $saved), ':', (int)($e->getPrevious() === null),
         ':', (int)($iteratorWatch->get() === null),
         ':', (int)($payloadWatch->get() === null), ':', $result, ';';
}
'''}

# Frozen by inspection before invoking PHP: the copied payload survives INPUT
# destruction, then prefix release destroys it before the saved-key catch.
EXPECTED = {NAME:
    b'B;M;W;V0;C0;K0;N0;V1;C1;K1;D:1;P:1;E:1:1:1:1:99;'}
