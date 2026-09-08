<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\Cache;
use OSC\OM\OSCOM;
use OSC\OM\Registry;

class securityCheckExtended_version_check
{
    public $type = 'warning';
    public $has_doc = true;

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->lang->loadDefinitions('modules/security_check/extended/version_check');

        $this->title = OSCOM::getDef('module_security_check_extended_version_check_title');
    }

    public function pass()
    {
        $VersionCache = new Cache('core_version_check');

        return $VersionCache->exists() && ($VersionCache->getTime() > strtotime('-30 days'));
    }

    public function getMessage()
    {
        return '<a href="' . OSCOM::link('online_update.php') . '">' . OSCOM::getDef('module_security_check_extended_version_check_error') . '</a>';
    }
}
