<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\OSCOM;

class cfgm_navbar_modules
{
    public $code = 'navbar_modules';
    public $directory;
    public $language_directory;
    public $site = 'Shop';
    public $key = 'MODULE_CONTENT_NAVBAR_INSTALLED';
    public $title;
    public $template_integration = false;

    public function __construct()
    {
        $this->directory = OSCOM::getConfig('dir_root', $this->site) . 'includes/modules/navbar_modules/';
        $this->language_directory = OSCOM::getConfig('dir_root', $this->site) . 'includes/languages/';
        $this->title = OSCOM::getDef('module_cfg_module_content_navbar_title');
    }
}
