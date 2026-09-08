<?php

class sp_cdm_fileview
{
    public function __construct()
    {


        add_action('sp_cdm/enqueue_scripts', array( $this, 'scripts' ));
    }

    public function scripts()
    {

        if (cdm_var('page') == 'sp-client-document-manager-fileview' || cdm_var('page') == 'sp-client-document-manager') {
            wp_enqueue_script('select2', plugins_url('js/select2/select2.min.js', dirname(__FILE__)));
            wp_enqueue_style('select2', plugins_url('js/select2/select2.min.css', dirname(__FILE__)));

        }
    }

    public function view()
    {

        global $wpdb;

        echo '
	
	<script type="text/javascript">
	jQuery(document).ready(function() {
		jQuery("select#user_uid").select2();
	
		
		
		
	});
	</script>
	';

        $dropdown = '
	
	
	<h2>' . __("User Files", "sp-client-document-manager") . '</h2>' . sp_client_upload_nav_menu() . '' . __("Choose a user below to view their files", "sp-client-document-manager") . '<p>
	<div style="margin-top:20px;margin-bottom:20px">
	<script type="text/javascript">
	jQuery(document).ready(function() {

	jQuery("#user_uid").on("change",function() {
	
		jQuery.cookie("pid", 0, { expires: 7 , path:"/" });
		jQuery.cookie("uid", jQuery("#user_uid").val(), { expires: 7 , path:"/" });
	window.location = "admin.php?page=sp-client-document-manager-fileview&id=" + jQuery("#user_uid").val();
	
	
	})
	});
	</script>
	<form>';

        $siteusers =  apply_filters('spcdm/premium/select_user/query', get_users()); // you can pass filters and option


        $re = '';
        if (count($siteusers) > 0) {
            $selected = '';
            if(isset($_REQUEST['id'])) {
                $selected =  sanitize_text_field(cdm_var('id'));
            }

            $dropdown .= '<select name="user_uid" id="user_uid"><option value="">'.__('Choose a user', "sp-client-document-manager").'</option>';
            foreach ($siteusers as $user) {
                if($selected  == $user->ID) {
                    $chosen = 'selected="selected"';
                } else {
                    $chosen = '';
                }
                if(isset($user->user_firstname) && $user->user_firstname != '') {
                    $name = ''.$user->user_firstname.' '.$user->user_lastname.'';
                } else {
                    $name = $user->user_nicename;
                }
                $dropdown .= '<option value="' . $user->ID . '" '.$chosen .'>'.apply_filters('spcdm/premium/select_user/name', $name, $user) .'</option>';
                #$dropdown .= '<option value="' . $user->ID . '">'.$user->user_nicename . ' ('.$user->user_email .')</option>';
            }
            $dropdown .= '</select>';
            #$dropdown = str_replace('value="' . $selected . '"','value="' . $selected . '" selected="selected"', $dropdown );
        }

        # $dropdown .= wp_dropdown_users( array( 'name' => 'user_uid', 'show_option_none' => 'Choose a user', 'selected' => sanitize_text_field( cdm_var( 'id' ) ), 'echo' => false ) );

        $dropdown .= '</form></div>';

        echo apply_filters('sp_cdm/admin/fileview/dropdown', $dropdown);
        if (cdm_var('id') != '') {


            echo do_shortcode('[sp-client-document-manager uid="' . sanitize_text_field(cdm_var('id')) . '"]');

        }


    }

}
