"""No-table hooked-object array snapshots and their reference ownership."""

CASES = {
    'singleton-scalar-snapshot': br'''<?php
class ScalarProjection128R {
    public int $virtual {
        get { echo 'BAD|'; return 1000; }
    }
    public $plain = 2;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
}
$box = new ScalarProjection128R;
$temporary =& $box->plain;
unset($temporary);
echo 'B|';
$copy = (array)$box; // CAST
echo 'C:', $copy['plain'] === 2, ':', $copy['value'] === 7, ':', ($copy === ['plain'=>2,'value'=>7]), '|';
$copy['plain'] = 9;
echo 'R:', $box->plain === 2, ':', $copy['plain'] === 9, '|';
unset($copy, $box);
echo 'A|';
''',
    'singleton-object-snapshot-release': br'''<?php
class SnapshotVictim128R {
    public function __destruct() { echo 'D|'; }
}
class ObjectProjection128R {
    public $plain;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
}
$box = new ObjectProjection128R;
$box->plain = new SnapshotVictim128R;
$temporary =& $box->plain;
unset($temporary);
echo 'B|';
$copy = (array)$box; // CAST
echo 'C:', ($copy === ['plain'=>$copy['plain'],'value'=>7]), ':', $copy['value'] === 7, '|';
$box->plain = 0;
echo 'K:', $box->plain === 0, '|';
unset($box);
echo 'U|';
unset($copy['plain']);
echo 'A|';
unset($copy);
''',
    'shared-cell-snapshot-write': br'''<?php
class SharedProjection128R {
    public $plain = 2;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
}
$outside = 2;
$box = new SharedProjection128R;
$box->plain =& $outside;
echo 'B|';
$copy = (array)$box; // CAST
$copy['plain'] = 9;
echo 'R:', $outside === 9, ':', $box->plain === 9, ':', $copy['plain'] === 9, ':', $copy['value'] === 7, '|';
unset($copy, $box, $outside);
echo 'A|';
''',
    'cached-table-snapshot-control': br'''<?php
#[\AllowDynamicProperties]
class CachedProjection128R {
    public $plain = 2;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
}
$box = new CachedProjection128R;
$box->tag = 5;
echo 'B|';
$copy = (array)$box; // CAST
$copy['plain'] = 9;
$box->plain = 3;
echo 'R:', $box->plain === 3, ':', $copy['plain'] === 9, ':', $copy['value'] === 7, ':', $copy['tag'] === 5, ':', ($copy === ['plain'=>9,'value'=>7,'tag'=>5]), '|';
unset($copy, $box);
echo 'A|';
''',
}

EXPECTED = {
    'singleton-scalar-snapshot': b'B|C:1:1:1|R:1:1|A|',
    'singleton-object-snapshot-release': b'B|C:1:1|K:1|U|D|A|',
    'shared-cell-snapshot-write': b'B|R:1:1:1:1|A|',
    'cached-table-snapshot-control': b'B|R:1:1:1:1:1|A|',
}
