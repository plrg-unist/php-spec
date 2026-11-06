#!/usr/bin/env python3
"""Terminal typed isset never invokes its admitted paired getter."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;$answer=false;
function answer82($member,$value):bool {
    global $count;$count=$count+1;echo "B",$member,":",$value,";";
    if($count===3){unset($GLOBALS['object']);echo "U";throw new Exception("isset");}
    return $GLOBALS['answer'];
}
class TerminalBoolPair82 {
    private int $secret=7;
    public int $plain=99;
    public function __isset(string $member):bool {
        echo "I",$member,";";$GLOBALS['name']="plain";
        return answer82($member,$this->secret);
    }
    public function __get($member){echo "G";return $this->secret;}
    public function __destruct(){echo "A";}
}
$object=new TerminalBoolPair82;$name="secret";
$result=isset($object->secret);echo $result===false,":",$name,";";
$answer=true;$name="secret";$result=isset($object->$name);echo $result===true,":",$name,";";
$name="secret";$result="keep";
try{$result=isset($object->$name);}catch(Exception $error){echo "C",$result,";";}
unset($error);
$object=new TerminalBoolPair82;$name="secret";$result=isset($object->$name);echo $result===true,";";
unset($object);echo $count,"Z";
'''

SOURCE_EXPECTED = b'Isecret;Bsecret:7;1:plain;Isecret;Bsecret:7;1:plain;Isecret;Bsecret:7;UACkeep;Isecret;Bsecret:7;1;A4Z'

CASES = {'terminal-typed-isset-present-get-literal-cv-bool-drop-abort': (SOURCE, SOURCE_EXPECTED)}
CONTROLS = {}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
