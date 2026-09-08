<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\OSCOM;

class cfgm_shipping
{
    public $code = 'shipping';
    public $directory;
    public $language_directory;
    public $site = 'Shop';
    public $key = 'MODULE_SHIPPING_INSTALLED';
    public $title;
    public $template_integration = false;

    public function __construct()
    {
        $this->directory = OSCOM::getConfig('dir_root', $this->site) . 'includes/modules/shipping/';
        $this->language_directory = OSCOM::getConfig('dir_root', $this->site) . 'includes/languages/';
        $this->title = OSCOM::getDef('module_cfg_module_shipping_title');
    }
}
