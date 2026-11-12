"""Ordinary aliased primitive string-offset keys across cast Warning callbacks."""

CASES = {
    'string-offset-reference-key-live-alias': b"<?php\nfunction string_read_reference_key($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['alias']=2;return true;}\n$text='abc';$alias=1.5;$key=&$alias;$got=99;\nset_error_handler('string_read_reference_key',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$key,'|',$alias;\n",
    'string-offset-reference-key-supplied-throw': b"<?php\nfunction string_read_reference_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['alias']=2;throw $GLOBALS['saved'];}\n$text='abc';$alias=1.5;$key=&$alias;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_reference_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$key,'|',$alias;}\nrestore_error_handler();\n",
}
