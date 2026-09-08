<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\OSCOM;
use OSC\OM\Registry;

class securityCheck_download_directory
{
    public $type = 'warning';

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->lang->loadDefinitions('modules/security_check/download_directory');
    }

    public function pass()
    {
        if (DOWNLOAD_ENABLED != 'true') {
            return true;
        }

        return is_dir(OSCOM::getConfig('dir_root', 'Shop') . 'download/');
    }

    public function getMessage()
    {
        return OSCOM::getDef('warning_download_directory_non_existent', [
          'download_path' => OSCOM::getConfig('dir_root', 'Shop') . 'download/'
        ]);
    }
}
