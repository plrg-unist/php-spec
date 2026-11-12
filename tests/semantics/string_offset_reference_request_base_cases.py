"""Authenticated REQUEST headers retained in a selected ordinary reference CV."""

CASES = {
    'string-offset-reference-request-base-live-header': b"<?php\nfunction string_read_reference_request_base($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['key']=2;return true;}\n$left='a';$right='bc';$text=$left.$right;$base_alias=&$text;$key=1.5;$got=99;\nset_error_handler('string_read_reference_request_base',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$base_alias,'|',$key;\n",
    'string-offset-reference-request-base-supplied-throw': b"<?php\nfunction string_read_reference_request_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['key']=2;throw $GLOBALS['saved'];}\n$left='a';$right='bc';$text=$left.$right;$base_alias=&$text;$key=1.5;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_reference_request_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',$base_alias,'|',$key;}\nrestore_error_handler();\n",
}
