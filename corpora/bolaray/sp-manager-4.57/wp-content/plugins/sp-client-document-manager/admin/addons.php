<?php

new sp_cdm_premium_addons();

class sp_cdm_premium_addons
{
    public function __construct()
    {



        add_action('sp_cu_admin_menu', array($this,'menu'), 2, 99);
        add_filter('sp_client_upload_top_menu', array($this,'topmenu'));
        add_action('wp_ajax_sp_rm_activate_addon', array($this,'activate'));
        add_action('sp_cdm_errors', array($this,'check_licenses'));
        add_action('network_admin_menu', array($this,'network_tab'));
    }

    public function network_tab()
    {
        if (is_multisite()) {
            add_menu_page(__("CDM Licenses", 'sp-client-document-manager'), __("CDM Licenses", 'sp-client-document-manager'), 'sp_cdm', 'cdm-document-licenses', array($this,'network_tab_content'));
        }
    }
        public function network_tab_content()
        {
            if (is_multisite()) {
                $this->view();
            }
        }


    public function activate()
    {
        $license_key = sanitize_text_field(cdm_var('license_key'));
        $product_name =sanitize_text_field(cdm_var('name'));
        $product_slug = sanitize_text_field(cdm_var('slug'));

        if (!wp_verify_nonce(cdm_var('_cdm_activate_product'.$product_slug.''), '_cdm_activate_product'.$product_slug.'')) {

            print 'Sorry, your nonce did not verify.';
            exit;

        } else {


            $message =array();
            #

            // data to send in our API request

            $edd_action = sanitize_text_field(cdm_var('set_action'));
            $api_params = array(
                'edd_action'=> $edd_action,
                'license' 	=> trim($license_key),
                'item_name' => urlencode($product_name) // the name of our product in EDD
            );

            // Call the custom API.
            $response = wp_remote_get(add_query_arg($api_params, EDD_CDM_STORE_URL), array( 'timeout' => 15, 'body' => $api_params, 'sslverify' => false ));
            if (is_array($response) && ! is_wp_error($response)) {
                // decode the license data
                $license_data = json_decode(wp_remote_retrieve_body($response));
                $message['result'] = $license_data;

                if($license_data->success == false) {
                    if($license_data->license == 'expired' || $license_data->error == 'expired') {
                        $message['error'] = 	'License expired, <a target="_blank" href="https://smartypantsplugins.com/digital-checkout/?edd_license_key='.$license_key.'">Please renew your license by clicking here</a>.';
                    } else {
                        $message['error'] = 	'License error, please check your license and try again.';
                    }
                } else {
                    $message['error'] = '';
                }
                set_transient(''.$product_slug.'-l', $license_data, 6 * HOUR_IN_SECONDS);
                update_option($product_slug, sanitize_text_field(cdm_var('license_key')));
            } else {
                $message['error'] = $response->get_error_message().' <br>Connection Info: '.EDD_CDM_STORE_URL.' '.json_encode($api_params).'  ';
            }
            echo json_encode($message);
            die();
        }
    }

    public function license_status($addon)
    {






        // data to send in our API request
        $api_params = array(
            'edd_action'=> 'check_license',
            'license' 	=> trim($addon['license_key']),
            'item_name' => urlencode($addon['name']) // the name of our product in EDD
        );

        // Call the custom API.
        $response = wp_remote_get(add_query_arg($api_params, EDD_CDM_STORE_URL), array( 'timeout' => 15, 'body' => $api_params, 'sslverify' => false ));

        // decode the license data
        $license_data = json_decode(wp_remote_retrieve_body($response));



        set_transient(''.$addon['slug'].'-l', $license_data, 6 * HOUR_IN_SECONDS);



        return $license_data;



    }
    public function deactivate()
    {


    }
    public function menu()
    {

        add_submenu_page('sp-client-document-manager', __('Addons', 'sp-client-document-manager'), __('Addons', 'sp-client-document-manager'), 'sp_cdm_addons', 'sp-cdm-addons-view', array($this,'view'));



    }
    public function topmenu($menu)
    {

        $menu .= '<li><a class="button" href="admin.php?page=sp-cdm-addons-view">'.__("Addons & Licenses", 'sp-client-document-manager').'</a></li> ';
        return $menu;
    }


    public function check_licenses()
    {

        $addons = apply_filters('spcdm/addons', array());

        if(count($addons)>0) {

            $invalid_licenses = false;
            foreach($addons as $addon) {

                if($addon['license_key'] == '') {

                    $invalid_licenses = true;
                    break;
                }


                $license_data = get_transient(''.$addon['slug'].'-l');
                if($license_data == false) {

                    $this->license_status($addon);
                }
                $license_data = get_transient(''.$addon['slug'].'-l');


                if($license_data->license !=  'valid') {
                    $invalid_licenses = true;
                    break;
                }


            }

            if($invalid_licenses == true) {
                echo '<div class="sp_cdm_error" style="margin-bottom:20px"><a style="color:#000;text-decoration:none" href="admin.php?page=sp-cdm-addons-view">'.__("There is a problem with some licenses, please click here to go to the license manager to update your licenses", 'sp-client-document-manager').'</a></div>';
            }
        }

    }

    public function view()
    {



        echo '<h2>Addons & Licenses</h2>' . sp_client_upload_nav_menu() . '';


        $addons = apply_filters('spcdm/addons', array());

        if(count($addons)==0) {


            echo '<div class="sprm-error"><p>'.__("You do not have any addons activated", 'sp-client-document-manager').'</p></div>';

        } else {



            foreach($addons as $addon) {

                $error = 0;
                $license_status = get_transient(''.$addon['slug'].'-l');

                if($license_status == false) {
                    $license_status = $this->license_status($addon);
                }
                #print_r($license_status);
                if($license_status->license == 'active' || $license_status->license == 'valid') {

                    $status = '<p style="color:green">License Active! Expires: '.date("m/d/Y", strtotime($license_status->expires)).'</p>';
                } elseif($license_status->license == 'inactive') {
                    $status = '<p style="color:red">License not activated.</p>';
                    $error = 1;
                } elseif($license_status->license == 'expired' || $license_status->error == 'expired') {
                    $status = 	'<p style="color:red">License expired, <a target="_blank" href="https://smartypantsplugins.com/digital-checkout/?edd_license_key='.$addon['license_key'].'">'.__("Please renew your license by clicking here", 'sp-client-document-manager').'</a>.</p>';
                    $error = 1;

                } else {




                    $error = 1;
                    $status = '<p style="color:red">'.__("License error, please check your license and try again.", 'sp-client-document-manager').'</p>';
                }


                if($error == 1) {
                    $style=' style="background-color:#FFD5D5"' ;

                } else {
                    $style='';
                }
                echo '<div class="sp-rm-addon-item sprm-addon-container-'.$addon['slug'].'" '.$style.'><form action="" method="post" class="sp-addon-activate sp-addon-'.$addon['slug'].'" >'.wp_nonce_field('_cdm_activate_product'.$addon['slug'].'', '_cdm_activate_product'.$addon['slug'].'').'
								  <input type="hidden" name="action" value="sp_rm_activate_addon">
								  <input type="hidden" name="slug" value="'.$addon['slug'].'">
								   <input type="hidden" name="name" value="'.$addon['name'].'">
								  <h4>'.$addon['name'].'</h4>
								  <p>Activate the license for '.$addon['name'].'. </p>
								  <input type="text" name="license_key" value="'.$addon['license_key'].'" style="width:100%"> ';
                echo'<div style="padding:4px;text-align:right">';
                if($license_status->license == 'valid') {
                    echo '
									<input type="hidden"  class="set_action"   name="set_action" value="deactivate_license">
									<input type="submit" name="save" value="Deactivate" class="sprm-activate-button button">';
                } else {

                    echo '
									<input type="hidden"  class="set_action"   name="set_action" value="activate_license">
									<input type="submit" name="save" value="Activate" class="sprm-activate-button button">';

                }

                echo'</div>
								  <div class="sp-rm-license-message-'.$addon['slug'].'" style="font-weight:bold;">'.$status .'</div>
								</form>
									</div>
								';


            }
            echo '<div style="clear:both"></div>';

        }

        do_action('spcdm/addons/forms', $addons);


        $p_addons = get_transient('sp_cdm_premium_feed');

        if($p_addons == false) {
            $request = wp_remote_get('https://smartypantsplugins.com/addons.php?premium=1');
            if (is_array($request) && ! is_wp_error($request)) {
                set_transient('sp_cdm_premium_feed', json_decode($request['body']), 24 * HOUR_IN_SECONDS);
                $p_addons = get_transient('sp_cdm_premium_feed');
            } else {
                echo esc_html('<div class="sp_cdm_error"> '.$request->get_error_message().'<br> '.__("Connection Info", 'sp-client-document-manager').': https://smartypantsplugins.com/addons.php?premium=1</div>');
            }
        }









        echo '<div class="sp-rm-addon-purchase-items"><h1>Available Addons</h1><p>'.__("Premium addons require the premium version of Smarty Document Manager", 'sp-client-document-manager').'</p>';




        $available_addons = get_transient('sp_cdm_premium_addon_feed');
        if($available_addons == false) {
            $request = wp_remote_get('https://smartypantsplugins.com/addons.php');
            if (is_array($request) && ! is_wp_error($request)) {
                set_transient('sp_cdm_premium_addon_feed', json_decode($request['body']), 24 * HOUR_IN_SECONDS);
                $available_addons = get_transient('sp_cdm_premium_addon_feed');
            } else {
                echo esc_html('<div class="sp_cdm_error"> '.$request->get_error_message().' <br>Connection Info: https://smartypantsplugins.com/addons.php</div>');
            }


        }





        foreach($p_addons as $a) {
            $image = '<p class="sp-rm-addon-purchase-item-image" ><img style="height:120px" src="'.SP_CDM_UPLOADS_DIR_URL.'/Capture.jpg"></p>';

            echo '<div class="sp-rm-addon-purchase-item" style="background-color:#418AD0">
								<h3 class="sp-rm-addon-purchase-item-name" style="color:#FFF">'.$a->name.'</h3>
								'.$image.'
								<p class="sp-rm-addon-purchase-item-desc" style="color:#FFF">'.$a->description.'</p>
								<div class="sp-rm-addon-purchase-item-price" style="color:#FFF"><a href="'.$a->url.'" target="_blank" class="button">Purchase</a></div>
								</div>';

        }



        foreach($available_addons as $a) {
            if($a->image) {
                $image = '<p class="sp-rm-addon-purchase-item-image"><img src="'.$a->image.'"></p>';
            } else {
                $image = '';
            }

            echo '<div class="sp-rm-addon-purchase-item">
								<h3 class="sp-rm-addon-purchase-item-name">'.$a->name.'</h3>
								'.$image.'
								<p class="sp-rm-addon-purchase-item-desc">'.$a->description.'</p>
								
								
								<div> <a href="'.$a->url.'" target="_blank" class="button">Purchase</a></div>
								</div>';

        }

        echo '<div style="clear:both"></div></div>';

    }



}
