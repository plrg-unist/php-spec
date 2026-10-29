<?php
class MagicGeneratorInvalidTemporary125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) { echo "BAD|body|"; }
}
class MagicGeneratorInvalidTemporaryPayload125 {
    public function __destruct() { echo "D|payload|"; }
}
function magicInvalidTemporary125() {
    global $receiver;
    try { echo "G|"; yield 0 => 7; echo "Y|"; $receiver = null; yield false => new MagicGeneratorInvalidTemporaryPayload125(); echo "BAD|next|"; }
    finally { echo "F|"; }
}
$receiver = new MagicGeneratorInvalidTemporary125();
$answer = 42;
try { $answer = $receiver->MiSs(...magicInvalidTemporary125()); }
catch (Throwable $error) { echo "E|", $error->getMessage(), "|", $answer, "|"; }
echo "A|";
