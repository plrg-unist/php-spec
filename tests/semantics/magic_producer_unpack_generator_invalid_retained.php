<?php
class MagicGeneratorInvalidRetained125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) { echo "BAD|body|"; }
}
class MagicGeneratorInvalidRetainedPayload125 {
    public function __destruct() { echo "D|payload|"; }
}
function magicInvalidRetained125() {
    global $receiver;
    try { echo "G|"; yield 0 => 7; echo "Y|"; $receiver = null; yield false => new MagicGeneratorInvalidRetainedPayload125(); echo "BAD|next|"; }
    finally { echo "F|"; }
}
$receiver = new MagicGeneratorInvalidRetained125();
$generator = magicInvalidRetained125();
$answer = 42;
try { $answer = $receiver->MiSs(...$generator); }
catch (Throwable $error) { echo "E|", $error->getMessage(), "|", $answer, "|"; }
echo "U|"; unset($generator); echo "A|";
