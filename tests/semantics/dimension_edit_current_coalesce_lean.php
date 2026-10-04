<?php
error_reporting(0);
class DestinationEditCurrent249 {public static int $value=9;}
trait HandlerEditCurrent249 {
    private function handle($level,$message,$file,$line) {echo "H:",get_called_class(),":",$line,";";if($line===11) {$GLOBALS['kept249']=$GLOBALS['same249'];$GLOBALS['same249'][1]=13;} else {$GLOBALS['later249']=$GLOBALS['same249'];}return false;}
    public function run(&$arg) {$seed=null;$a=[1=>$seed,2=>&$arg];$GLOBALS['same249']=&$a;set_error_handler($this->handle(...),8192);
        $result=($a[
            selectedCurrent249(
                1.5
            ) +
            0.0
        ] ??= currentRhs249());
        restore_error_handler();$arg=17;echo "R:",$result===null?1:0,":",$a[1],":",$GLOBALS['kept249'][1]===null?1:0,":",$GLOBALS['later249'][2],":",$GLOBALS['kept249'][2],":",func_get_arg(0),";";
        unset($GLOBALS['same249'],$GLOBALS['kept249'],$GLOBALS['later249']);
    }
}
class OwnerEditCurrent249 {use HandlerEditCurrent249;}
class ChildEditCurrent249 extends OwnerEditCurrent249 {public function handle($level,$message,$file,$line) {echo "WRONG;";return true;}}
function selectedCurrent249($value) {echo "K;";return $value;}
function currentRhs249() {echo "S;";return 19;}
$owner249=new ChildEditCurrent249();$owner249->run(DestinationEditCurrent249::$value);echo "V:",DestinationEditCurrent249::$value,";";
