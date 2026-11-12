"""An outside ordinary CV retains the selected REQUEST string during Warning."""

CASES = {
    'string-offset-retained-request-carrier': b"<?php\nfunction string_read_retained($n,$m,$f,$l) {$GLOBALS['text']='XYZ';$GLOBALS['key']=2;echo 'H;';return true;}\n$prefix='a';$text=$prefix.'bc';$keeper=$text;$key=1.5;$got=99;\nset_error_handler('string_read_retained',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$keeper,'|',$key;\n",
    'string-offset-retained-request-carrier-throw': b"<?php\nfunction string_read_retained_throw($n,$m,$f,$l) {$GLOBALS['text']='XYZ';$GLOBALS['key']=2;echo 'H;';throw $GLOBALS['saved'];}\n$prefix='a';$text=$prefix.'bc';$keeper=$text;$key=1.5;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_retained_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',$keeper,'|',$key;}\nrestore_error_handler();\n",
}
