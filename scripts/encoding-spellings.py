#!/usr/bin/env python3
"""Record and verify every pinned libmbfl name/MIME/alias spelling."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PHP = str(ROOT / '.tools/php/bin/php')
# mb_internal_encoding resolves names independently through the public mbstring
# API. Its state changes occur only in this trusted, isolated inventory process.
query = r'''set_error_handler(fn()=>true); $codecs=[]; $spellings=[];
foreach(mb_list_encodings() as $name) {
    $mime=mb_preferred_mime_name($name); $aliases=mb_encoding_aliases($name);
    $codecs[$name]=['mime'=>$mime ?: null,'aliases'=>$aliases];
    foreach(array_merge([$name], $mime ? [$mime] : [], $aliases) as $spelling) {
        if (!mb_internal_encoding($spelling)) throw new RuntimeException('Unresolved spelling');
        $canonical=mb_internal_encoding();
        $spellings[$spelling]=['name'=>$spelling,'canonical'=>$canonical,
            'source_b64'=>base64_encode(mb_convert_encoding('<?php /* name */ echo 1;', $canonical,'UTF-8'))];
    }
}
echo json_encode(['codecs'=>$codecs,'spellings'=>array_values($spellings)]);'''
data = json.loads(subprocess.check_output([PHP, '-n', '-r', query], text=True))
definitions = {}
for path in sorted((ROOT / 'vendor/php-src/ext/mbstring/libmbfl').rglob('*.c')):
    text = path.read_text()
    for match in re.finditer(r'const mbfl_encoding \w+\s*=\s*\{(.*?)\};', text, re.S):
        fields = match.group(1).split(',')
        name = re.fullmatch(r'\s*"([^"]+)"\s*', fields[1])
        if name:
            definitions[name[1]] = {'file': str(path.relative_to(ROOT)), 'line': text[:match.start()].count('\n') + 1}
    for match in re.finditer(r'^DEF_SB(?:_TBL)?\([^,]+,\s*"([^"]+)"', text, re.M):
        definitions[match[1]] = {'file': str(path.relative_to(ROOT)), 'line': text[:match.start()].count('\n') + 1}
for name, codec in data['codecs'].items():
    codec['definition'] = definitions[name]
data['spellings'].sort(key=lambda item: item['name'])
data = {'authority': 'vendor/php-src/ext/mbstring/libmbfl/mbfl/mbfl_encoding.c:307',
        'precedence': ['canonical name', 'first MIME name in registry order', 'first alias in registry order'],
        'declaration_lookup': 'C string: ASCII case-insensitive, terminated by the first NUL; INI lists separately use the native length-aware list parser.',
        **data}
assert len(data['codecs']) == 79 and len(data['spellings']) == 214
path = ROOT / 'coverage/encoding-spellings.json'
path.write_text(json.dumps(data, indent=2) + '\n')
check = r'''$data=json_decode(file_get_contents($argv[1]),true,512,JSON_THROW_ON_ERROR); $count=0;
foreach($data['spellings'] as $item) {
    foreach(array_unique([$item['name'],strtolower($item['name']),strtoupper($item['name']),$item['name']."\0ignored"]) as $name) {
        if (php_spec_encoding_name($name)!==$item['canonical']) throw new RuntimeException('Lookup mismatch for '.bin2hex($name));
        ++$count;
    }
}
foreach(['','pass','none','raw','not-an-encoding',' UTF-8','UTF-8 ',"\0UTF-8"] as $name) {
    if (php_spec_encoding_name($name)!==null) throw new RuntimeException('Invalid encoding accepted: '.bin2hex($name));
    ++$count;
}
echo json_encode(['spellings'=>count($data['spellings']),'lookup_checks'=>$count]);'''
result = subprocess.check_output([PHP, '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), '-r', check, str(path)], text=True)
print(result)
