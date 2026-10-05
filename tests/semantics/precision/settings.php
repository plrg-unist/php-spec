<?php
$value=12.3456789;
echo 'I[',ini_get('precision'),']:', $value,'|';
foreach (['3tail','0','-1','4294967296','-2','  +0004junk',"1\0tail",'',true,false,null,-1.9] as $setting) {
    $old=ini_set('precision',$setting);
    if ($old===false) echo 'F'; else echo 'O[',$old,']';
    echo ':N[',ini_get('precision'),']:',(string)$value,':';
    print $value;
    echo '|';
}
ini_restore('precision');
echo 'R[',ini_get('precision'),']:', $value,'|END';
