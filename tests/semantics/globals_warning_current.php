<?php
error_reporting(0);
class OwnerGlobals226 {
    private function handle($level,$message,$file,$line) {
        if($GLOBALS['throw226']) {
            $saved226=$GLOBALS['pending226'];
            unset($GLOBALS['pending226'],$GLOBALS['older226']);
            echo "X:",self::class,"/",get_called_class(),";";
            throw $saved226;
        }
        $GLOBALS['left226'] =& $GLOBALS['null226'];
        $GLOBALS['missing226']=13;
        echo "H:",self::class,"/",get_called_class(),":",$message==='Undefined global variable $missing226'?1:0,";";
        return true;
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
$left226=7;$old226=&$left226;$null226=null;$throw226=false;
$receiver226=new ChildGlobals226();$receiver226->install();
unset($receiver226,$captured226);
$same226=$left226 === $GLOBALS['missing226'];
echo "R:",$same226?1:0,":",$old226,":",$left226===null?1:0,":",$missing226,";";
$dst226 =& DestinationGlobals226::$slot;
$older226=new Error('older');$pending226=new Error('handler',0,$older226);
$expected226=$pending226;$previous226=$older226;$throw226=true;
try {$dst226=$GLOBALS['throwMissing226'];} catch(Error $e) {
    echo "T:",$dst226,":",$e===$expected226?1:0,":",$e->getPrevious()===$previous226?1:0,";";
    unset($expected226,$previous226);
    echo "L:",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";
}
restore_error_handler();
