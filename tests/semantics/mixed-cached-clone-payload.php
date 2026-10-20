<?php
class MixedPayloadValue116 {
    public int $value = 7;
    public function __destruct() { echo 'V', $this->value, '|'; }
}
#[AllowDynamicProperties]
class MixedPayload116 {
    public int $tag = 1;
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
echo 'P:';
$source = new MixedPayload116();
$source->payload = new MixedPayloadValue116();
foreach ($source as $key => $value) {}
unset($key, $value);
$copy = clone $source;
$copy->tag = 2;
unset($source);
echo 'A|', $copy->payload->value, '|';
unset($copy);
echo 'B|';
