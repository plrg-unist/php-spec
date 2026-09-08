<?php
/**
  * osCommerce Online Merchant
  *
  * @copyright (c) 2016 osCommerce; https://www.oscommerce.com
  * @license MIT; https://www.oscommerce.com/license/mit.txt
  */

use OSC\OM\Apps;
use OSC\OM\OSCOM;
use OSC\OM\Registry;

class oscTemplate
{
    public $_title;
    public $_code = 'Sail';
    public $_blocks = array();
    public $_content = array();
    public $_grid_container_width = 12;
    public $_grid_content_width = BOOTSTRAP_CONTENT;
    public $_grid_column_width = 0; // deprecated
    public $_data = array();

    protected $lang;

    public function __construct()
    {
        $this->lang = Registry::get('Language');

        $this->_title = OSCOM::getDef('title', ['store_name' => STORE_NAME]);

        $this->addBlock('<meta name="generator" content="osCommerce Online Merchant" />', 'header_tags');
    }

    public function setGridContainerWidth($width)
    {
        $this->_grid_container_width = $width;
    }

    public function getGridContainerWidth()
    {
        return $this->_grid_container_width;
    }

    public function setGridContentWidth($width)
    {
        $this->_grid_content_width = $width;
    }

    public function getGridContentWidth()
    {
        return $this->_grid_content_width;
    }

    public function setGridColumnWidth($width)
    {
        $this->_grid_column_width = $width;
    }

    public function getGridColumnWidth()
    {
        return (12 - BOOTSTRAP_CONTENT) / 2;
    }

    public function setTitle($title)
    {
        $this->_title = $title;
    }

    public function getTitle()
    {
        return $this->_title;
    }

    public function setCode($code)
    {
        $this->_code = $code;
    }

    public function getCode()
    {
        return $this->_code;
    }

    public function addBlock($block, $group)
    {
        $this->_blocks[$group][] = $block;
    }

    public function hasBlocks($group)
    {
        return (isset($this->_blocks[$group]) && !empty($this->_blocks[$group]));
    }

    public function getBlocks($group)
    {
        if ($this->hasBlocks($group)) {
            return implode("\n", $this->_blocks[$group]);
        }
    }

    public function buildBlocks()
    {
        if (defined('TEMPLATE_BLOCK_GROUPS') && tep_not_null(TEMPLATE_BLOCK_GROUPS)) {
            $tbgroups_array = explode(';', TEMPLATE_BLOCK_GROUPS);

            foreach ($tbgroups_array as $group) {
                $module_key = 'MODULE_' . strtoupper($group) . '_INSTALLED';

                if (defined($module_key) && tep_not_null(constant($module_key))) {
                    $modules_array = explode(';', constant($module_key));

                    foreach ($modules_array as $module) {
                        $class = basename($module, '.php');

                        if (!class_exists($class)) {
                            if ($this->lang->definitionsExist('modules/' . $group . '/' . pathinfo($module, PATHINFO_FILENAME))) {
                                $this->lang->loadDefinitions('modules/' . $group . '/' . pathinfo($module, PATHINFO_FILENAME));
                            }

                            if (is_file('includes/modules/' . $group . '/' . $class . '.php')) {
                                include('includes/modules/' . $group . '/' . $class . '.php');
                            }
                        }

                        if (class_exists($class)) {
                            $mb = new $class();

                            if ($mb->isEnabled()) {
                                $mb->execute();
                            }
                        }
                    }
                }
            }
        }
    }

    public function addContent($content, $group)
    {
        $this->_content[$group][] = $content;
    }

    public function hasContent($group)
    {
        return (isset($this->_content[$group]) && !empty($this->_content[$group]));
    }

    public function getContent($group)
    {
        if (!class_exists('tp_' . $group) && is_file('includes/modules/pages/tp_' . $group . '.php')) {
            include('includes/modules/pages/tp_' . $group . '.php');
        }

        if (class_exists('tp_' . $group)) {
            $template_page_class = 'tp_' . $group;
            $template_page = new $template_page_class();
            $template_page->prepare();
        }

        foreach ($this->getContentModules($group) as $module) {
            if (strpos($module, '\\') !== false) {
                $class = Apps::getModuleClass($group . '/' . $module, 'Content');

                $mb = new $class();

                if ($mb->isEnabled()) {
                    $mb->execute();
                }
            } else {
                if (!class_exists($module)) {
                    if (is_file('includes/modules/content/' . $group . '/' . $module . '.php')) {
                        if ($this->lang->definitionsExist('modules/content/' . $group . '/' . $module)) {
                            $this->lang->loadDefinitions('modules/content/' . $group . '/' . $module);
                        }

                        include('includes/modules/content/' . $group . '/' . $module . '.php');
                    }
                }

                if (class_exists($module)) {
                    $mb = new $module();

                    if ($mb->isEnabled()) {
                        $mb->execute();
                    }
                }
            }
        }

        if (class_exists('tp_' . $group)) {
            $template_page->build();
        }

        if ($this->hasContent($group)) {
            return implode("\n", $this->_content[$group]);
        }
    }

    public function getContentModules($group)
    {
        $result = array();

        foreach (explode(';', MODULE_CONTENT_INSTALLED) as $m) {
            $module = explode('/', $m, 2);

            if ($module[0] == $group) {
                $result[] = $module[1];
            }
        }

        return $result;
    }

    public function getFile($file, $template = null)
    {
        if (!isset($template)) {
            $template = $this->getCode();
        }

        return OSCOM::BASE_DIR . 'Sites/' . OSCOM::getSite() . '/Templates/' . $template . '/' . $file;
    }

    public function getPublicFile($file, $template = null)
    {
        if (!isset($template)) {
            $template = $this->getCode();
        }

        return OSCOM::linkPublic('Templates/' . $template . '/' . $file);
    }
}
