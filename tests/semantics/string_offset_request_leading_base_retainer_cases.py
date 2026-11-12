"""REQUEST leading-read bases survive through a real current keeper CV."""

CASES = {
    'string-offset-request-leading-base-retained-header': b"<?php\nfunction string_read_request_base_leading($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';$GLOBALS['key']=2;return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$key='1x';$got=99;\nset_error_handler('string_read_request_base_leading',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$keeper,'|',$key;\n",
    'string-offset-request-leading-base-supplied-throw': b"<?php\nfunction string_read_request_base_leading_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';unset($GLOBALS['key']);throw $GLOBALS['saved'];}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$key='1x';$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_request_base_leading_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',$keeper,'|',(int)isset($key);}\nrestore_error_handler();\n",
}

OUTPUTS = (b'2|Illegal string offset "1x"|5;b|XYZ|abc|2',
           b'2|Illegal string offset "1x"|5;1|1|99|XYZ|abc|0')
