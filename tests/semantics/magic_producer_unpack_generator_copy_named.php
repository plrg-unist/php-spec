<?php
$value = 7;
class MagicGeneratorCopy125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) {
        global $value;
        echo "B|", $name, "|", $arguments["arguments"], "|", $arguments["tail"], "|", $value, "|";
        $arguments["arguments"] = 33; echo "T|", $value, "|"; return 23;
    }
}
function &magicGeneratorCopy125() {
    global $value, $receiver;
    try { echo "G|"; yield "arguments" => $value; echo "N|"; $value = 9; $receiver = null; $tail = 8; yield "tail" => $tail; echo "Z|"; }
    finally { echo "F|"; }
}
$receiver = new MagicGeneratorCopy125();
$answer = $receiver->MiSs(...magicGeneratorCopy125());
echo "R|", $answer, "|V|", $value, "|A|";
