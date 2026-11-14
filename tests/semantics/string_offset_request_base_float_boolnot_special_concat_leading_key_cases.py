"""Runtime quiet float NOT/CONCAT keys keep real temporary string carriers."""
import json
from pathlib import Path

WATCHED = tuple(json.loads((Path(__file__).resolve().parents[2] / 'spec/semantics/modules.json').read_bytes()))

CASES = {
    'string-offset-request-base-float-boolnot-zero-leading-key': b"<?php\nfunction string_read_request_base_literal_key($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$got=99;\nset_error_handler('string_read_request_base_literal_key',E_WARNING);ini_set('precision','17');\n$got=$text[(('' . (!0.0)) . 'x')];\nrestore_error_handler();\necho $got,'|',$text,'|',$keeper;\n",
    'string-offset-request-base-float-boolnot-signed-zero-negative-leading-key': b"<?php\nfunction string_read_request_base_literal_key($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['text']='XYZ';return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$got=99;\nset_error_handler('string_read_request_base_literal_key',E_WARNING);ini_set('precision','17');\n$got=$text[(('-' . (!(-0.0))) . 'x')];\nrestore_error_handler();\necho $got,'|',$text,'|',$keeper;\n",
    'string-offset-marked-request-base-float-boolnot-infinity-zero-key-throw': b"<?php\nfunction string_read_marked_request_literal_key_throw($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';$GLOBALS['base_alias']='XYZ';unset($GLOBALS['text']);unset($GLOBALS['base_alias']);throw $GLOBALS['saved'];}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$base_alias=&$text;$got=99;$saved=new Exception('saved');\nset_error_handler('string_read_marked_request_literal_key_throw',E_WARNING);ini_set('precision','17');\ntry {$got=$text[(('0' . (!INF)) . 'x')];} catch (Exception $caught) {echo (int)($caught===$saved),'|',(int)($caught->getPrevious()===null),'|',$got,'|',$keeper,'|',(int)isset($text),'|',(int)isset($base_alias);}\nrestore_error_handler();\n",
    'string-offset-request-base-float-boolnot-arithmetic-negative-key-bounds': b"<?php\nfunction string_read_request_literal_key_bounds($n,$m,$f,$l) {echo $n,'|',$m,'|',$l,';';if($m==='Uninitialized string offset -4'){unset($GLOBALS['text']);unset($GLOBALS['keeper']);return true;}$GLOBALS['text']='XYZ';return true;}\n$left='a';$right='bc';$text=$left.$right;$keeper=$text;$got=99;\nset_error_handler('string_read_request_literal_key_bounds',E_WARNING);ini_set('precision','17');\n$got=$text[(('-4' . (!(1.0 + 2.0))) . 'x')];\nrestore_error_handler();\necho $got,'|',(int)isset($text),'|',(int)isset($keeper);\n",
}

OUTPUTS = dict(zip(CASES, (
    b'2|Illegal string offset "1x"|5;b|XYZ|abc',
    b'2|Illegal string offset "-1x"|5;c|XYZ|abc',
    b'2|Illegal string offset "0x"|5;1|1|99|abc|0|0',
    b'2|Illegal string offset "-4x"|5;2|Uninitialized string offset -4|5;|0|0',
)))
