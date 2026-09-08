<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\OSCOM;
use OSC\OM\Registry;

class securityCheck_file_uploads
{
    public $type = 'warning';

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->lang->loadDefinitions('modules/security_check/file_uploads');
    }

    public function pass()
    {
        return (bool)ini_get('file_uploads');
    }

    public function getMessage()
    {
        return OSCOM::getDef('warning_file_uploads_disabled');
    }
}
