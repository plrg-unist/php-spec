<?php
class LiteralBacking30 {
    public int $value { get => $this->{'value'}; }
    public int $other { get => ${'this'}->other; }
}
$box = new LiteralBacking30;
$box->value = 7;
$box->other = 9;
foreach ((array) $box as $key => $value) { echo $key, "=", $value, "|"; }
