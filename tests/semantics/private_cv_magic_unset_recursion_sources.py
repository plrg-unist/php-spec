#!/usr/bin/env python3
"""Private recursive CV unset suppresses the callback but keeps visibility errors."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function recurse86($member){
    global $count;$count=$count+1;
    $current=$GLOBALS['object'];unset($GLOBALS['object']);echo "U";
    try{unset($current->$member);}catch(Error $error){echo "E",$error->getMessage(),";";}
    unset($error);unset($current);throw new Exception("outer");
}
class PrivateCVUnset86 {
    private int $secret=7;
    public int $plain=99;
    public function __unset(string $member):void {
        echo "M",$member,";";$GLOBALS['name']="plain";
        $this->secret=8;recurse86($member);
    }
    public function __destruct(){echo "A",$this->secret,";";}
}
$object=new PrivateCVUnset86;$name="secret";$keep="keep";
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "C",$keep,";";}
unset($error);
$object=new PrivateCVUnset86;$name="secret";
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "F",$keep,";";}
unset($error);echo $count,"Z";
'''

SOURCE_EXPECTED = b'Msecret;UECannot access private property PrivateCVUnset86::$secret;A8;Ckeep;Msecret;UECannot access private property PrivateCVUnset86::$secret;A8;Fkeep;2Z'

CASES = {'private-cv-recursive-unset-visibility-error': (SOURCE, SOURCE_EXPECTED)}
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
