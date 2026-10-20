<?php
class MixedPayload118 {
    public int $value = 7;
    public function __destruct() { echo 'V', $this->value, '|'; }
}
#[AllowDynamicProperties]
class MixedCallback118 {
    public int $tag = 1;
    public function __clone(): void {
        global $source, $error;
        echo 'C|';
        $this->tag = 2;
        $source = null;
        foreach ($this as $key => $entry) {
            if ($key === 'tag') { echo 'T', $entry, '|'; }
            else { echo 'P', $entry->value, '|'; }
        }
        unset($key, $entry);
        echo 'c|';
        throw $error;
    }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
$error = new Exception('same118');
$source = new MixedCallback118();
$source->payload = new MixedPayload118();
foreach ($source as $key => $entry) {}
unset($key, $entry);
$result = 42;
echo 'X:';
try { $result = clone $source; echo 'bad|'; }
catch (Throwable $caught) {
    echo 'C|', $caught === $error ? 'same|' : 'wrong|', $result, '|';
}
unset($source, $caught, $error);
echo 'E|';
