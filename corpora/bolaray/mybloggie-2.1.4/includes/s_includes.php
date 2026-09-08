<?php

class cls_encrypt
{
    public $_key;

    public function cls_encrypt()
    {

        // This is your private key. Set to something else
        // when using in your site.

        $this->_key = "php_example";
        return 1;
    }

    public function keyED($txt)
    {
        $encrypt_key = md5($this->_key);
        $ctr=0;
        $tmp = "";
        for ($i=0;$i<strlen($txt);$i++) {
            if ($ctr==strlen($encrypt_key)) {
                $ctr=0;
            }
            $tmp.= substr($txt, $i, 1) ^ substr($encrypt_key, $ctr, 1);
            $ctr++;
        }
        return $tmp;
    }

    public function html_encrypt($txt)
    {
        return urlencode($this->encrypt($txt));
    }

    public function encrypt($txt)
    {

        // Public key, which we always set to a unique value.

        $encrypt_key = md5(microtime());
        $ctr=0;
        $tmp = "";
        for ($i=0;$i<strlen($txt);$i++) {
            if ($ctr==strlen($encrypt_key)) {
                $ctr=0;
            }
            $tmp.= substr($encrypt_key, $ctr, 1) .
            (substr($txt, $i, 1) ^ substr($encrypt_key, $ctr, 1));
            $ctr++;
        }
        return $this->keyED($tmp);
    }

    public function html_decrypt($txt)
    {
        return $this->decrypt(str_replace('\0', chr(0), urldecode($txt))); // 2.1.4
        //return $this->decrypt(urldecode($txt));
    }

    public function decrypt($txt)
    {
        $txt = $this->keyED($txt);
        $tmp = "";
        for ($i=0;$i<strlen($txt);$i++) {
            $md5 = substr($txt, $i, 1);
            $i++;
            $tmp.= (substr($txt, $i, 1) ^ $md5);
        }
        return $tmp;
    }
}
