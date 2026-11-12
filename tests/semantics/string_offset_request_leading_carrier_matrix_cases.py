"""Non-NUL REQUEST leading bases and keys preserve selected bytes and cells."""

CASES = {
    'string-offset-leading-marked-base-key': b"<?php\nfunction string_read_marked_base_leading($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';$GLOBALS['key_alias']=2;return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$base_alias=&$text;$key='1x';$key_alias=&$key;$got=99;\nset_error_handler('string_read_marked_base_leading',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$base_alias,'|',$keeper,'|',$key,'|',$key_alias;\n",
    'string-offset-leading-request-pair': b"<?php\nfunction string_read_request_pair_leading($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';$GLOBALS['key']=2;return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$key_left='1';$key_right='x';$key=$key_left.$key_right;$got=99;\nset_error_handler('string_read_request_pair_leading',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$keeper,'|',$key;\n",
    'string-offset-leading-marked-request-pair-throw': b"<?php\nfunction string_read_marked_request_pair_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';$GLOBALS['key_alias']=2;unset($GLOBALS['text']);unset($GLOBALS['base_alias']);unset($GLOBALS['key']);unset($GLOBALS['key_alias']);throw $GLOBALS['saved'];}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$base_alias=&$text;$key_left='1';$key_right='x';$key=$key_left.$key_right;$key_alias=&$key;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_marked_request_pair_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$keeper,'|',(int)isset($text),'|',(int)isset($base_alias),'|',(int)isset($key),'|',(int)isset($key_alias);}\nrestore_error_handler();\n",
    'string-offset-leading-shared-request-cell': b"<?php\nfunction string_read_shared_request_leading($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';$GLOBALS['key_alias']=2;return true;}\n$left='1';$right='x';$text=$left.$right;$keeper=$text;$base_alias=&$text;$key=&$text;$key_alias=&$key;$got=99;\nset_error_handler('string_read_shared_request_leading',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',$base_alias,'|',$keeper,'|',$key,'|',$key_alias;\n",
}
OUTPUTS = (
    b'2|Illegal string offset "1x"|5;b|XYZ|XYZ|abc|2|2',
    b'2|Illegal string offset "1x"|5;b|XYZ|abc|2',
    b'2|Illegal string offset "1x"|5;1|1|99|abc|0|0|0|0',
    b'2|Illegal string offset "1x"|5;x|2|2|1x|2|2',
)
