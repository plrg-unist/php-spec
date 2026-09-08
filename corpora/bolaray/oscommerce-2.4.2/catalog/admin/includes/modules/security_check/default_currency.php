<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\OSCOM;
use OSC\OM\Registry;

class securityCheck_default_currency
{
    public $type = 'error';

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->lang->loadDefinitions('modules/security_check/default_currency');
    }

    public function pass()
    {
        return defined('DEFAULT_CURRENCY');
    }

    public function getMessage()
    {
        return OSCOM::getDef('error_no_default_currency_defined');
    }
}
