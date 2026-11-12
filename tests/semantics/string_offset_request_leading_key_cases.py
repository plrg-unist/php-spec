"""Initially ordinary REQUEST text keys retain the pre-Warning integer offset."""

CASES = {
    'string-offset-request-leading-key-fixed-index': b"<?php\nfunction string_read_request_leading_key($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';$GLOBALS['key']=2;return true;}\n$text='abc';$left='1';$right='x';$key=$left.$right;$got=99;\nset_error_handler('string_read_request_leading_key',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$key;\n",
    'string-offset-request-leading-key-supplied-throw': b"<?php\nfunction string_read_request_leading_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';unset($GLOBALS['key']);throw $GLOBALS['saved'];}\n$text='abc';$left='1';$right='x';$key=$left.$right;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_request_leading_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',(int)isset($key);}\nrestore_error_handler();\n",
}

OUTPUTS = (b'2|Illegal string offset "1x"|5;b|XYZ|2',
           b'2|Illegal string offset "1x"|5;1|1|99|XYZ|0')
