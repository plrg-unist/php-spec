<?php
$pack = [7, 8];
$saved = $pack;
class MagicArrayReference125 {
    public function __call(string $name, array $arguments) {
        global $pack;
        echo "B|", $name, "|", $arguments[0], "|", $arguments[1], "|", $arguments["tail"], "|", $pack[0], "|";
        $arguments[0] = 33; return 23;
    }
}
function &magicArrayInput125() { global $pack; echo "P|"; return $pack; }
function magicArrayReplace125() { global $pack; echo "Q|"; $pack = [99]; return ["tail" => 9]; }
$receiver = new MagicArrayReference125();
$answer = $receiver->MiSs(...magicArrayInput125(), ...magicArrayReplace125());
echo "R|", $answer, "|V|", $pack[0], "|", $saved[0], "|A|";
