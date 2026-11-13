<?php
namespace Ns275UntypedPairEmptyHeader;
echo 'BAD|';
class Box275 {
    public $tag = 17 {
        get { return $this->tag; }
        set /* before empty list */ () {
            $this->tag = $value;
            return 19;
        }
    }
}
