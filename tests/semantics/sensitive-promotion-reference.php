<?php
class SensitivePromotedReference23 {
    public \Error $error;
    public function __construct(#[\SensitiveParameter] public int &$secret) {
        $this->secret = 17;
        $this->error = new \Error("E");
    }
}
$secret = 7;
$object = new SensitivePromotedReference23($secret);
$error = $object->error;
$wrapper = $error->getTrace()[0]["args"][0];
echo $secret, "|", $object->secret, "|", $wrapper->getValue(), "|";
$secret = 23;
echo $secret, "|", $object->secret, "|", $wrapper->getValue(), "|", $error->getTraceAsString();
