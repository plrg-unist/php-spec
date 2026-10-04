<?php
error_reporting(0);
class OwnerGlobals226 {
    private function handle($level,$message,$file,$line) {
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
$left226=7;$old226=&$left226;$null226=null;
$receiver226=new ChildGlobals226();$receiver226->install();
unset($receiver226,$captured226);
$same226=$left226 === $GLOBALS['missing226'];
echo "R:",$same226?1:0,":",$old226,":",$left226===null?1:0,":",$missing226,";";
restore_error_handler();
