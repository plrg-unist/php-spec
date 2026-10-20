<?php
class ClonePayload113 {
    public int $value = 7;
    public function __destruct() { echo 'V', $this->value, '|'; }
}
class CachedCallback113 {
    public int $tag = 1;
    public $payload;
    public function __clone(): void {
        global $source, $error;
        echo 'C|';
        $this->tag = 2;
        foreach ($this as $key => $entry) {
            if ($key === 'tag') { echo 'T', $entry, '|'; }
            else { echo 'P', $entry->value, '|'; }
        }
        unset($key, $entry);
        $source = null;
        echo 'c|';
        throw $error;
    }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
$error = new Exception('same113');
$source = new CachedCallback113();
$source->payload = new ClonePayload113();
foreach ($source as $key => $entry) {}
unset($key, $entry);
$result = 42;
echo 'X:';
try { $result = clone $source; echo 'A|'; }
catch (Exception $caught) { if ($caught === $error) { echo 'C|'; } echo $result, '|'; }
echo 'F|';
unset($source, $caught, $error);
echo 'E|';
