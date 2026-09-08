"""Deterministic bounded operator and lexical interaction inputs (no execution)."""
import base64
import hashlib
import json
import subprocess
from corpus import ROOT


def generated():
    binary = ["+", "-", "*", "/", "%", "**", ".", "<<", ">>", "&", "|", "^",
              "&&", "||", "and", "or", "xor", "==", "!=", "===", "!==", "<", "<=",
              ">", ">=", "<=>", "??", "|>"]
    serial = 0

    def item(source, family):
        nonlocal serial
        serial += 1
        encoded = source.encode("latin1") if isinstance(source, str) else source
        return {"id": "generated/" + family + "/" + str(serial), "origin": "generated",
                "status": "source", "ini": {}, "sha256": hashlib.sha256(encoded).hexdigest(),
                "bytes": len(encoded), "source_b64": base64.b64encode(encoded).decode(), "expected": "accept"}

    for left in binary:
        for right in binary:
            yield item("<?php $r = (($a " + left + " $b) " + right + " $c);", "binary-left")
            yield item("<?php $r = ($a " + left + " ($b " + right + " $c));", "binary-right")
    for unary in ["+", "-", "!", "~", "@", "(int)", "(string)", "clone "]:
        for operator in binary:
            yield item("<?php $r = " + unary + "($a " + operator + " $b);", "unary-binary")
            yield item("<?php $r = (" + unary + "$a) " + operator + " $b;", "binary-unary")
    for separator in [" ", "\t", "\r\n", "/*comment*/", "//comment\n", "#comment\n"]:
        for word in ["yield", "new", "clone", "throw", "print", "include"]:
            yield item("<?php function f() { " + word + separator + "$x; }", "keyword-comment")
    for byte in [0, 9, 10, 13, 34, 36, 39, 92, 127, 128, 255]:
        payload = bytes([byte])
        yield item(b"\xff<?php $x='" + payload.replace(b"\\", b"\\\\").replace(b"'", b"\\'") + b"'; ?>\x00\xff", "literal-inline-bytes")

    # Width-changing source filters revisit the entire buffer at every declare.
    # Some combinations are parser-invalid; preserve their raw classification.
    for initial, payload in [('SJIS', b'\x81\x5c'), ('ISO-8859-1', b'\xe9'), ('UTF-8', b'\xe3\x81\x82')]:
        for final in ['SJIS', 'ISO-8859-1', 'UTF-8']:
            for count in [1, 2, 4, 8, 16]:
                for form in ['comment', 'identifier', 'literal']:
                    data = payload * count
                    body = b'/*' + data + b'*/ echo 1;' if form == 'comment' else b'$' + data + b'=1;' if form == 'identifier' else b'echo "' + data + b'";'
                    source = b'<?php declare(encoding="' + initial.encode() + b'"){' + body + b'} declare(encoding="' + final.encode() + b'");echo 1;'
                    result = item(source, 'encoding-transitions')
                    result.pop('expected')
                    result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'}
                    yield result

    for initial in ['', 'SJIS', 'ISO-8859-1', 'UTF-8']:
        for declared in ['SJIS', 'ISO-8859-1', 'UTF-8']:
            for prefix in [b'', b'\xff', b'\xe9', b'\x82\xa0', b'\xe3\x81\x82', b'\xc3\xa9']:
                source = b'<?php /*' + prefix + b'*/ declare(encoding="' + declared.encode() + b'");echo "\\u{1f600}";'
                result = item(source, 'encoding-prefix-profiles')
                result.pop('expected')
                result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'}
                if initial:
                    result['ini']['zend.script_encoding'] = initial
                yield result

    for candidates in ['UTF-8,SJIS', 'SJIS,UTF-8', 'UTF-8,ISO-8859-1', 'ISO-8859-1,UTF-8', 'UTF-8,SJIS,ISO-8859-1']:
        for declaration in [b'', b'declare(encoding="SJIS"); ']:
            for payload in [b'', b'\xff', b'\xe9', b'\x82\xa0', b'\xe3\x81\x82', b'\xc3\xa9']:
                result = item(b'<?php ' + declaration + b'echo "' + payload + b'";', 'encoding-candidate-profiles')
                result.pop('expected')
                result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8', 'zend.script_encoding': candidates}
                yield result

    for encoding, codec, bom in [('UTF-16LE', 'utf-16-le', b'\xff\xfe'), ('UTF-16BE', 'utf-16-be', b'\xfe\xff'), ('UTF-32LE', 'utf-32-le', b'\xff\xfe\0\0'), ('UTF-32BE', 'utf-32-be', b'\0\0\xfe\xff'), ('UTF-8', 'utf8', b'\xef\xbb\xbf')]:
        for prefix in ['', '#!/usr/bin/php\n', '#!/usr/bin/php\r\n']:
            result = item(bom + (prefix + '<?php echo 1;').encode(codec), 'encoding-bom-preambles')
            result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'}
            yield result
    for encoding, codec in [('SJIS', 'shift_jis'), ('UTF-16LE', 'utf-16-le'), ('ISO-8859-1', 'latin1')]:
        for internal in ['UTF-8', encoding]:
            result = item(('<?php /* lead */ declare(encoding="' + encoding + '"); echo "\\u{1F600}";').encode(codec), 'encoding-internal-profiles')
            result.pop('expected')
            result['ini'] = {'zend.multibyte': '1', 'internal_encoding': internal}
            yield result

    for substitute in ['none', 'long', 'entity', '63', '65533', '0', '128512']:
        for placement in ['literal', 'identifier', 'comment']:
            body = b'echo "\xff";' if placement == 'literal' else b'$\xff=1;' if placement == 'identifier' else b'/*\xff*/echo 1;'
            result = item(b'<?php declare(encoding="SJIS");' + body, 'encoding-substitution')
            result.pop('expected')
            result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8', 'mbstring.substitute_character': substitute}
            yield result

    for language in ['neutral', 'Japanese', 'Korean', 'Russian', 'Chinese Simplified', 'Chinese Traditional']:
        for payload in [b'\x82\xa0', b'\xe3\x81\x82', b'\xff']:
            result = item(b'<?php echo "' + payload + b'";', 'encoding-language-auto')
            result.pop('expected')
            result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8', 'zend.script_encoding': 'auto', 'mbstring.language': language}
            yield result

    for profile in [
        {'default_charset': 'ISO-8859-1'},
        {'default_charset': 'SJIS', 'internal_encoding': 'UTF-8'},
        {'default_charset': 'UTF-8', 'internal_encoding': 'ISO-8859-1', 'mbstring.internal_encoding': 'SJIS'},
        {'internal_encoding': '', 'default_charset': ''},
        {'zend.detect_unicode': '0', 'internal_encoding': 'UTF-8'},
    ]:
        result = item(b'<?php declare(encoding="SJIS");echo "\x82\xa0";', 'encoding-setting-precedence')
        result['ini'] = {'zend.multibyte': '1', **profile}
        yield result

    # Exercise every codec actually registered by the pinned engine. The helper
    # converts trusted fixture fragments only; generated PHP is never executed.
    code = "set_error_handler(fn()=>true); $out=[]; foreach(mb_list_encodings() as $encoding){$out[$encoding]=array_map(fn($s)=>base64_encode(mb_convert_encoding($s,$encoding,'UTF-8')),['<?php /*','*/ echo 1;','<?php /* text */ echo 1;']);} echo json_encode($out);"
    encodings = json.loads(subprocess.check_output([str(ROOT / '.tools/php/bin/php'), '-n', '-r', code]))
    for encoding, parts in encodings.items():
        prefix, suffix, plain = map(base64.b64decode, parts)
        for substitute in ['65533', '128512']:
            for source in [plain] + [prefix + bad + suffix for bad in [b'\xff', b'\x80', b'\xc0\xaf', b'\xed\xa0\x80', b'\x00\xd8', b'\xd8\x00']]:
                result = item(source, 'encoding-all-codecs')
                result.pop('expected')
                result['ini'] = {'zend.multibyte': '1', 'internal_encoding': 'UTF-8', 'zend.script_encoding': encoding, 'mbstring.substitute_character': substitute}
                yield result
