<?php

$cdm_virtual_directory_admin = new cdm_virtual_directory_admin();



add_action('cdm_virtual_directory_admin', array($sp_cdm_premium_projects, 'cdm_virtual_directory_admin'));



class cdm_virtual_directory_admin
{
    public function menu()
    {
        add_submenu_page('sp-client-document-manager', __(sprintf('Sort %s', sp_cdm_folder_name(1)), 'sp-client-document-manager'), __(sprintf('Sort %s', sp_cdm_folder_name(1)), 'sp-client-document-manager'), 'sp_cdm_projects', 'sp-client-document-manager-projects-sort', array(
        $this,
        'view_sortable'
                ));


    }


    public function view()
    {







    }







}
