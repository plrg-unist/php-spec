<?php
class DiagnosticBacking {public static object $value;}
class DiagnosticString {
    function __toString() {
        global $value;
        DiagnosticBacking::$value=&$value;
        echo 'S',func_num_args(),':',E_STRICT,'|';
        return 'converted';
    }
}
class DiagnosticOwner {
    const VALUE=E_STRICT+1;
    public static function name($name=self::class) {return $name;}
    private static function handler($level,$message,$file,$line) {
        echo 'H',func_num_args(),':',$level===E_DEPRECATED?'D':'X','|';
        global $value;
        $value=new DiagnosticString;
        self::receive($value,$value);
        echo self::name(),':',$value,'|';
        try {$value='blocked';}catch(TypeError $e){echo 'R|';}
        $other=new stdClass;
        DiagnosticBacking::$value=&$other;
        $value=[];
        return 0;
    }
    public static function receive(string &$a,string &$b) {
        echo 'P',func_num_args(),':',$a,':',$b,'|';
    }
    public static function run() {
        set_error_handler([self::class,'handler'],E_DEPRECATED);
        echo self::VALUE,':',self::VALUE,'|';
        restore_error_handler();
        echo self::name();
    }
}
DiagnosticOwner::run();
