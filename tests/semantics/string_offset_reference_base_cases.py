"""Referenced interned string headers survive cast Warning alias writes."""

CASES = {
    'string-offset-reference-base-replacement': b"<?php\nfunction string_read_reference_base($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';$GLOBALS['key']=2;return true;}\n$text='abc';$base_alias=&$text;$key=1.5;$got=99;\nset_error_handler('string_read_reference_base',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$base_alias,'|',$key;\n",
    'string-offset-reference-base-supplied-throw': b"<?php\nfunction string_read_reference_base_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';$GLOBALS['key']=2;throw $GLOBALS['saved'];}\n$text='abc';$base_alias=&$text;$key=1.5;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_reference_base_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',$base_alias,'|',$key;}\nrestore_error_handler();\n",
}
