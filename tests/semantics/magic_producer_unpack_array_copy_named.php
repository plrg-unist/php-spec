<?php
$value = 7;
$alias =& $value;
$pack = ["arguments" => &$alias];
$saved = $pack;
class MagicArrayCopyBase125 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) {
        global $value;
        echo "B|", __CLASS__, "|", static::class, "|", $name, "|", $arguments["arguments"], "|", $arguments["tail"], "|", $value, "|";
        $arguments["arguments"] = 33;
        echo "T|", $arguments["arguments"], "|", $value, "|"; return 23;
    }
}
class MagicArrayCopyChild125 extends MagicArrayCopyBase125 {}
function magicArrayTail125() {
    global $value, $receiver;
    echo "P|"; $value = 9; $receiver = null; return ["tail" => 8];
}
$receiver = new MagicArrayCopyChild125();
$answer = $receiver->MiSs(...$pack, ...magicArrayTail125());
echo "R|", $answer, "|V|", $pack["arguments"], "|", $saved["arguments"], "|A|";
