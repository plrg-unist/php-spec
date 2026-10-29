<?php
$failure = new Exception("producer");
class MagicGeneratorBody125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) { echo "BAD|body|"; }
}
class MagicGeneratorBodyPayload125 {
    public function __destruct() { echo "D|payload|"; }
}
function magicGeneratorBody125() {
    global $receiver, $failure;
    try { echo "G|"; yield "arguments" => new MagicGeneratorBodyPayload125(); echo "N|"; $receiver = null; throw $failure; }
    finally { echo "F|"; }
}
$receiver = new MagicGeneratorBody125();
$answer = 42;
try { $answer = $receiver->MiSs(...magicGeneratorBody125()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|", $answer, "|"; }
echo "A|";
