"""Initially marked interned text keys retain the pre-Warning integer offset."""

CASES = {
    'string-offset-reference-leading-key-fixed-index': b"<?php\nfunction string_read_reference_leading_key($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';$GLOBALS['key_alias']=2;return true;}\n$text='abc';$key='1x';$key_alias=&$key;$got=99;\nset_error_handler('string_read_reference_leading_key',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$key,'|',$key_alias;\n",
    'string-offset-reference-leading-key-supplied-throw': b"<?php\nfunction string_read_reference_leading_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';unset($GLOBALS['key']);unset($GLOBALS['key_alias']);throw $GLOBALS['saved'];}\n$text='abc';$key='1x';$key_alias=&$key;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_reference_leading_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',(int)isset($key),'|',(int)isset($key_alias);}\nrestore_error_handler();\n",
}

OUTPUTS = (b'2|Illegal string offset "1x"|5;b|XYZ|2|2',
           b'2|Illegal string offset "1x"|5;1|1|99|XYZ|0|0')
