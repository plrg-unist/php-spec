<?php
class MixedPayload118 {
    public int $value = 7;
    public function __destruct() { echo 'V', $this->value, '|'; }
}
#[AllowDynamicProperties]
class MixedCallback118 {
    public int $tag = 1;
    public function __clone(): void {
        global $source;
        echo 'C|';
        $this->tag = 2;
        $source = null;
        foreach ($this as $key => $entry) {
            if ($key === 'tag') { echo 'T', $entry, '|'; }
            else { echo 'P', $entry->value, '|'; }
        }
        unset($key, $entry);
        unset($this->payload);
        echo 'c|';
    }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
$source = new MixedCallback118();
$source->payload = new MixedPayload118();
foreach ($source as $key => $entry) {}
unset($key, $entry);
$result = 42;
echo 'R:';
$result = clone $source;
echo 'A|', $result->tag, '|';
unset($result, $source);
echo 'E|';
