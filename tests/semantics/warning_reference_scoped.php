<?php
declare(strict_types=1);
error_reporting(0);
class TypedScoped220 { public static int $slot=9; }
class OwnerScoped220 {
    private function handle($level,$message,$file,$line) {
        echo "H",func_num_args(),":",__CLASS__,"/",static::class;
        $older=new Error("older");
        $pending=new Error("handler",0,$older);
        $GLOBALS['pendingScoped220']=$pending;
        $GLOBALS['olderScoped220']=$older;
        throw $pending;
    }
    public function run(&$dst) {
        $handler=new ChildScoped220;
        set_error_handler([$handler,"handle"],2);
        $handler=null;
        try {
            $dst =
                $missingScoped220;
            echo "BAD";
        } catch(TypeError $error) {
            $previous=$error->getPrevious();
            echo "|C:",$dst,":",func_get_arg(0),":",$error->getLine(),":",$error->getFile()===__FILE__?1:0;
            echo ":",$previous===$GLOBALS['pendingScoped220']?1:0,":",$previous->getPrevious()===$GLOBALS['olderScoped220']?1:0;
            $trace=$error->getTrace();
            $frames=0; foreach($trace as $frame) {$frames=$frames+1;}
            echo "|T:",$frames,":",$trace[0]['class'],"/",$trace[0]['function'],":",$trace[0]['args'][0];
            $trace=$previous->getTrace();
            $frames=0; foreach($trace as $frame) {$frames=$frames+1;}
            echo "|P:",$frames,":",$trace[0]['class'],"/",$trace[0]['function'],":",$trace[0]['args'][0];
            echo ":",$trace[1]['class'],"/",$trace[1]['function'],":",$trace[1]['args'][0];
            $GLOBALS['pendingScoped220']=null;
            $GLOBALS['olderScoped220']=null;
            echo "|L:",$previous->getMessage(),":",$previous->getPrevious()->getMessage();
        }
        restore_error_handler();
    }
}
class ChildScoped220 extends OwnerScoped220 {
    public function handle($level,$message,$file,$line) {echo "BAD-Child";}
}
$dstScoped220 =& TypedScoped220::$slot;
(new ChildScoped220)->run($dstScoped220);
echo "|",$dstScoped220,"\n";
