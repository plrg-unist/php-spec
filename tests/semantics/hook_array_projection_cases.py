"""Normal no-table hook projections and subsequent object comparison."""

CASES = {
    'cast-preserves-inline-undef-comparison': br'''<?php
class ProjectionOrder128 {
    public int $first;
    public int $value = 7 {
        get { global $gets; $gets=$gets+1; return $this->value+100; }
    }
}
$gets=0;
$left=new ProjectionOrder128;
$right=new ProjectionOrder128;
$right->first=5;
echo 'B|';
$copy=(array)$left; // CAST
echo 'C:',(int)($copy['value']===7),':',(int)(!isset($copy['first'])),':',(int)($gets===0),'|';
$result=$left <=> $right; // COMPARE
echo 'R:',$result,':',(int)($result===1),':',(int)($gets===0),'|A|';
''',
    'raw-nonpublic-virtual-snapshot': br'''<?php
class ProjectionShape128 {
    public int $virtual {
        get { echo 'BAD|'; return 1000; }
    }
    private int $secret=2;
    protected int $hidden=3;
    public int $value=7 {
        get { global $gets; $gets=$gets+1; return $this->value+100; }
    }
}
$gets=0;
$box=new ProjectionShape128;
echo 'B|';
$copy=(array)$box; // CAST
echo 'C:',(int)($copy["\0ProjectionShape128\0secret"]===2),':',(int)($copy["\0*\0hidden"]===3),':',(int)($copy['value']===7),':',(int)(!isset($copy['virtual'])),':',(int)($gets===0),'|';
$observed=$box->value;
echo 'G:',(int)($observed===107),':',(int)($gets===1),'|A|';
''',
}

EXPECTED = {
    'cast-preserves-inline-undef-comparison': b'B|C:1:1:1|R:1:1:1|A|',
    'raw-nonpublic-virtual-snapshot': b'B|C:1:1:1:1:1|G:1:1|A|',
}
