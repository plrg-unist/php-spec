<?php
class MagicArrayDuplicate125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) { echo "BAD|body|"; }
}
class MagicArrayDuplicatePayload125 {
    public function __destruct() { echo "D|payload|"; }
}
function magicArrayDuplicate125() {
    global $receiver; echo "P|"; $receiver = null;
    return ["arguments" => new MagicArrayDuplicatePayload125()];
}
$receiver = new MagicArrayDuplicate125();
$answer = 42;
try { $answer = $receiver->MiSs(...["arguments" => 7], ...magicArrayDuplicate125()); }
catch (Throwable $error) { echo "E|", $error->getMessage(), "|", $answer, "|"; }
echo "A|";
