<?php
class ClonePayload113 {
    public int $value = 7;
    public function __destruct() { echo 'V', $this->value, '|'; }
}
class CachedCallback113 {
    public int $tag = 1;
    public $payload;
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
        echo 'c|';
    }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
$source = new CachedCallback113();
$source->payload = new ClonePayload113();
foreach ($source as $key => $entry) {}
unset($key, $entry);
$copy = 42;
echo 'R:';
$copy = clone $source;
echo 'A|';
echo $copy->tag, '/', $copy->payload->value, '|';
unset($copy, $source);
echo 'E|';
