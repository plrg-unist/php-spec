<?php
error_reporting(0);
class DestinationUnsetCurrent249 {public static int $value=9;}
trait HandlerUnsetCurrent249 {
    private function handle($level,$message,$file,$line) {echo "U:",get_called_class(),":",$line,";";$GLOBALS['last249']=$GLOBALS['same249'];$GLOBALS['live249']=17;return false;}
    public function run(&$arg) {$a=[2=>&$arg];$GLOBALS['same249']=&$a;$GLOBALS['live249']=&$arg;set_error_handler($this->handle(...),8192);
        unset($a[2.5]);restore_error_handler();echo "R:",isset($a[2])?1:0,":",isset($GLOBALS['last249'][2])?1:0,":",$arg,":",func_get_arg(0),";";
        unset($GLOBALS['same249'],$GLOBALS['live249'],$GLOBALS['last249']);
    }
}
class OwnerUnsetCurrent249 {use HandlerUnsetCurrent249;}
class ChildUnsetCurrent249 extends OwnerUnsetCurrent249 {public function handle($level,$message,$file,$line) {echo "WRONG;";return true;}}
$owner249=new ChildUnsetCurrent249();$owner249->run(DestinationUnsetCurrent249::$value);echo "V:",DestinationUnsetCurrent249::$value,";";
