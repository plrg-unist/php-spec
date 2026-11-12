"""A surviving alias retains the original REQUEST cell after selected-name unset."""

CASES = {
    'string-offset-reference-alias-keeper-unset-name': b"<?php\nfunction string_read_reference_alias_keeper($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';unset($GLOBALS['text']);$GLOBALS['key']=2;return true;}\n$left='a';$right='bc';$text=$left.$right;$base_alias=&$text;$key=1.5;$got=99;\nset_error_handler('string_read_reference_alias_keeper',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',(int)isset($text),'|',$base_alias,'|',$key;\n",
    'string-offset-reference-alias-keeper-supplied-throw': b"<?php\nfunction string_read_reference_alias_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';unset($GLOBALS['text']);$GLOBALS['key']=2;throw $GLOBALS['saved'];}\n$left='a';$right='bc';$text=$left.$right;$base_alias=&$text;$key=1.5;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_reference_alias_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',(int)isset($text),'|',$base_alias,'|',$key;}\nrestore_error_handler();\n",
}

OUTPUTS = (b'2|String offset cast occurred|5;c|0|abc|2',
           b'2|String offset cast occurred|5;1|1|99|0|abc|2')
