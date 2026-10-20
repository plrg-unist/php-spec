<?php
class CachedPayload110 {
    public int $value = 5;
    public function __destruct() { echo 'P', $this->value, '|'; }
}
class CachedOwner110 {
    public int $tag = 1;
    public $payload = null;
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
$source = new CachedOwner110();
$source->payload = new CachedPayload110();
foreach ($source as $value) {}
unset($value);
echo 'P:';
$copy = clone $source;
$copy->tag = 2;
$copy->payload->value = 7;
echo $source->payload === $copy->payload ? 'S|' : 'bad|';
unset($source);
echo 'A|';
unset($copy);
echo 'E|';
