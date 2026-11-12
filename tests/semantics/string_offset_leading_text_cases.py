"""Fixed leading-integer text Warning offsets with interned base and key."""

CASES = {
    'string-offset-leading-text-key-unset': b"<?php\nfunction string_read_leading($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';unset($GLOBALS['key']);return true;}\n$text='abc';$key='1x';$got=99;\nset_error_handler('string_read_leading',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',(int)isset($key);\n",
    'string-offset-leading-text-old-bounds': b"<?php\nfunction string_read_leading_bounds($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='WXYZ';unset($GLOBALS['key']);return true;}\n$text='abc';$key='3x';$got=99;\nset_error_handler('string_read_leading_bounds',E_WARNING);\n$got=$text[$key];\nrestore_error_handler();\necho $got,'|',$text,'|',(int)isset($key);\n",
    'string-offset-leading-text-supplied-throw': b"<?php\nfunction string_read_leading_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='WXYZ';unset($GLOBALS['key']);restore_error_handler();throw $GLOBALS['saved'];}\n$text='abc';$key='3x';$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_leading_throw',E_WARNING);\ntry {$got=$text[$key];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$text,'|',(int)isset($key);}\nrestore_error_handler();\n",
}
