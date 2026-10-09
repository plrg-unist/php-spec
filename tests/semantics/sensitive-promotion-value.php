<?php
class SensitivePromotedValue23 {
    public \Error $error;
    public function __construct(#[\SensitiveParameter] public int $secret, public int $visible) {
        $secret = 17;
        $this->error = new \Error("E");
    }
}
$object = new SensitivePromotedValue23(7, 9);
$error = $object->error;
$arguments = $error->getTrace()[0]["args"];
echo $object->secret, "|", $arguments[0]->getValue(), "|", $arguments[1], "|", $error->getTraceAsString();
