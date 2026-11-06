#!/usr/bin/env python3
"""Indirect magic GET keeps its notice pin after clearing the recursion guard."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function notice84($level,$message,$file,$line){
    global $count;$count=$count+1;echo "N",$level,":",$message,";";
    $current=$GLOBALS['object'];echo $current->secret,";";unset($current);
    unset($GLOBALS['object']);echo "U";
    if($count===2){throw new Exception("notice");}
    return true;
}
class IndirectMagic84 {
    private int $secret=7;
    public function __get($member) {echo "G",$member,";";return $this->secret;}
    public function __destruct(){echo "A",$this->secret,";";}
}
set_error_handler("notice84");
$object=new IndirectMagic84;$keep="keep";
try{$keep=$object->secret[]=1;}catch(Error $error){echo "E",$error->getMessage(),":",$keep,";";}
unset($error);
$object=new IndirectMagic84;
try{$keep=$object->secret[]=1;}catch(Exception $error){echo "C",$keep,";";}
unset($error);
$object=new IndirectMagic84;
try{$keep=$object->secret[]=1;}catch(Error $error){echo "R",$error->getMessage(),":",$keep,";";}
unset($error);echo $count,"Z";
'''

SOURCE_EXPECTED = b'Gsecret;N8:Indirect modification of overloaded property IndirectMagic84::$secret has no effect;Gsecret;7;UA7;ECannot use a scalar value as an array:keep;Gsecret;N8:Indirect modification of overloaded property IndirectMagic84::$secret has no effect;Gsecret;7;UA7;Ckeep;Gsecret;N8:Indirect modification of overloaded property IndirectMagic84::$secret has no effect;Gsecret;7;UA7;RCannot use a scalar value as an array:keep;3Z'

CASES = {'indirect-append-notice-reentry-release-throw-retry': (SOURCE, SOURCE_EXPECTED)}
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
