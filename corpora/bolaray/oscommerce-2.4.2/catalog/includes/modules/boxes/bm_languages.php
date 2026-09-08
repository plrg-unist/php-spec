<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\HTML;
use OSC\OM\OSCOM;
use OSC\OM\Registry;

class bm_languages
{
    public $code = 'bm_languages';
    public $group = 'boxes';
    public $title;
    public $description;
    public $sort_order;
    public $enabled = false;

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->title = OSCOM::getDef('module_boxes_languages_title');
        $this->description = OSCOM::getDef('module_boxes_languages_description');

        if (defined('MODULE_BOXES_LANGUAGES_STATUS')) {
            $this->sort_order = MODULE_BOXES_LANGUAGES_SORT_ORDER;
            $this->enabled = (MODULE_BOXES_LANGUAGES_STATUS == 'True');

            $this->group = ((MODULE_BOXES_LANGUAGES_CONTENT_PLACEMENT == 'Left Column') ? 'boxes_column_left' : 'boxes_column_right');
        }
    }

    public function execute()
    {
        global $PHP_SELF, $oscTemplate;

        if (substr(basename($PHP_SELF), 0, 8) != 'checkout') {
            $languages = $this->lang->getAll();

            $languages_string = '';

            foreach ($languages as $code => $value) {
                $languages_string .= ' <a href="' . OSCOM::link($PHP_SELF, tep_get_all_get_params(array('language', 'currency')) . 'language=' . $code) . '">' . $this->lang->getImage($value['code']) . '</a> ';
            }

            ob_start();
            include('includes/modules/boxes/templates/languages.php');
            $data = ob_get_clean();

            $oscTemplate->addBlock($data, $this->group);
        }
    }

    public function isEnabled()
    {
        return $this->enabled;
    }

    public function check()
    {
        return defined('MODULE_BOXES_LANGUAGES_STATUS');
    }

    public function install()
    {
        $OSCOM_Db = Registry::get('Db');

        $OSCOM_Db->save('configuration', [
          'configuration_title' => 'Enable Languages Module',
          'configuration_key' => 'MODULE_BOXES_LANGUAGES_STATUS',
          'configuration_value' => 'True',
          'configuration_description' => 'Do you want to add the module to your shop?',
          'configuration_group_id' => '6',
          'sort_order' => '1',
          'set_function' => 'tep_cfg_select_option(array(\'True\', \'False\'), ',
          'date_added' => 'now()'
        ]);

        $OSCOM_Db->save('configuration', [
          'configuration_title' => 'Content Placement',
          'configuration_key' => 'MODULE_BOXES_LANGUAGES_CONTENT_PLACEMENT',
          'configuration_value' => 'Right Column',
          'configuration_description' => 'Should the module be loaded in the left or right column?',
          'configuration_group_id' => '6',
          'sort_order' => '1',
          'set_function' => 'tep_cfg_select_option(array(\'Left Column\', \'Right Column\'), ',
          'date_added' => 'now()'
        ]);

        $OSCOM_Db->save('configuration', [
          'configuration_title' => 'Sort Order',
          'configuration_key' => 'MODULE_BOXES_LANGUAGES_SORT_ORDER',
          'configuration_value' => '0',
          'configuration_description' => 'Sort order of display. Lowest is displayed first.',
          'configuration_group_id' => '6',
          'sort_order' => '0',
          'date_added' => 'now()'
        ]);
    }

    public function remove()
    {
        return Registry::get('Db')->exec('delete from :table_configuration where configuration_key in ("' . implode('", "', $this->keys()) . '")');
    }

    public function keys()
    {
        return array('MODULE_BOXES_LANGUAGES_STATUS', 'MODULE_BOXES_LANGUAGES_CONTENT_PLACEMENT', 'MODULE_BOXES_LANGUAGES_SORT_ORDER');
    }
}
