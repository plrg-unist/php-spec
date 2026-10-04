<?php
error_reporting(0);
class OwnerGlobals226 {
    private function handle($level,$message,$file,$line) {
        $saved226=$GLOBALS['pending226'];
        unset($GLOBALS['pending226'],$GLOBALS['older226']);
        echo "X:",self::class,"/",get_called_class(),";";
        throw $saved226;
    }
    public function install() {
        $GLOBALS['captured226']=$this->handle(...);
        set_error_handler($GLOBALS['captured226'],2);
    }
}
class ChildGlobals226 extends OwnerGlobals226 {
    public function handle($level,$message,$file,$line) {echo "BAD;";return true;}
}
class DestinationGlobals226 {public static int $slot=9;}
$receiver226=new ChildGlobals226();$receiver226->install();
unset($receiver226,$captured226);
$dst226 =& DestinationGlobals226::$slot;
$older226=new Error('older');$pending226=new Error('handler',0,$older226);
$expected226=$pending226;$previous226=$older226;
try {$dst226=$GLOBALS['throwMissing226'];} catch(Error $e) {
    echo "T:",$dst226,":",$e===$expected226?1:0,":",$e->getPrevious()===$previous226?1:0,";";
    unset($expected226,$previous226);
    echo "L:",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";
}
restore_error_handler();
