<?php
$failure = new Exception("handler");
class MagicGeneratorHandler125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) {
        global $failure;
        echo "B|", $name, "|"; $arguments["arguments"] = null;
        echo "U|"; unset($arguments); throw $failure;
    }
}
class MagicGeneratorHandlerPayload125 {
    public function __destruct() { echo "D|payload|"; }
}
function magicGeneratorHandler125() {
    global $receiver;
    try { echo "G|"; $receiver = null; yield "arguments" => new MagicGeneratorHandlerPayload125(); echo "N|"; }
    finally { echo "F|"; }
}
$receiver = new MagicGeneratorHandler125();
$answer = 42;
try { $answer = $receiver->MiSs(...magicGeneratorHandler125()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|", $answer, "|"; }
echo "A|";
