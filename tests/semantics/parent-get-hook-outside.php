<?php
class ParentGetBase108 {
    public int $value { get { return 7; } }
}
class ParentGetOutside108 extends ParentGetBase108 {
    public function bad() { return parent::$value::get(); }
}
echo 'NEVER|';
