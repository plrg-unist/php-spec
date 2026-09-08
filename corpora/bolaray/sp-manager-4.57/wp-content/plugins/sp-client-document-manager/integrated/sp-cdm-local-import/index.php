<?php


$sp_cdm_local_import  = new sp_cdm_local_import_integrated();


define('SP_CDM_LOCAL_IMPORT_DIR', plugin_dir_path(__FILE__));
define('SP_CDM_LOCAL_IMPORT_URL', plugins_url('', __FILE__));

include_once ''.dirname(__FILE__).'/includes/functions.php';
include_once ''.dirname(__FILE__).'/admin/importer.php';


add_action('admin_enqueue_scripts', array($sp_cdm_local_import,'admin_js'));
add_action('admin_enqueue_scripts', array($sp_cdm_local_import,'admin_css'));


add_action('admin_init', array($sp_cdm_local_import ,'permissions'));
add_action('admin_init', array($sp_cdm_local_import ,'install'));

add_action('wp_enqueue_scripts', array($sp_cdm_local_import,'js'));
add_action('wp_enqueue_scripts', array($sp_cdm_local_import,'css'));

add_action('admin_enqueue_scripts', array($sp_cdm_local_import,'js'));
add_action('admin_enqueue_scripts', array($sp_cdm_local_import,'css'));


class sp_cdm_local_import_integrated
{
    public function __construct()
    {

        $this->namesake = 'cdm_local_import';
        $this->version = '1.0.2';
        $this->name = 'SP Client Document Manager Local Import';
        $this->item_name = $this->name;

    }


    public function permissions()
    {

        global $current_user;
        if($current_user != '') {

            if (user_can($current_user->ID, 'manage_options') && !current_user_can('sp_cdm_local_import')) {

                @require_once(ABSPATH . 'wp-includes/pluggable.php');
                $role = get_role('administrator');
                $role->add_cap('sp_cdm_local_import');

            }

        }

    }
    public function install()
    {
        global $wpdb;

        if(get_option('sp_cdm_'.$this->namesake.'_version') == '' or get_option('sp_cdm_'.$this->namesake.'_version') < $this->version) {



            update_option('sp_cdm_'.$this->namesake.'_version', $this->version);
        }
    }

    public function admin_js()
    {

        wp_enqueue_script($this->namesake, plugins_url('js/scripts.js', __FILE__));

    }
    public function admin_css()
    {

    }


    public function js()
    {

    }

    public function css()
    {

    }







}
