<?php

$sp_cdm_media_uploader= new sp_cdm_media_uploader();
add_action('sp_cdm_after_file_upload', array($sp_cdm_media_uploader, 'after_upload'), 10, 2);

add_filter('sp_cdm_add_buttons', array($sp_cdm_media_uploader, 'button'));
add_filter('sp_cdm_upload_bottom', array($sp_cdm_media_uploader, 'add_form'));





add_action('wp_ajax_sp_cdm_media_save_embed', array($sp_cdm_media_uploader, 'save_embed'));

add_filter('sp_cdm_viewfile_image', array($sp_cdm_media_uploader, 'thumbnail'), 10, 2);


class sp_cdm_media_uploader
{
    public function thumbnail($img, $r)
    {

        if($r['file'] == 'embed') {

            $img = '<img src="' . SP_CDM_PLUGIN_URL . 'images/video.png" width="32" >';

        }

        return $img;
    }

    public function after_upload($target_path, $uid)
    {


        sp_cdm_media_screenshot($target_path);


    }


    public function save_embed()
    {
        global $wpdb,$current_user;



        $insert_file['uid'] = cdm_var('uid');
        $insert_file['cid'] = cdm_var('cid');
        $insert_file['name'] = cdm_var('file-name');
        $insert_file['file'] = 'embed';


        $insert_file['embed'] =strip_tags(cdm_var('embed'), '<iframe><embed><video><source>');

        $insert_file['pid'] = cdm_var('pid');
        $insert_file['notes'] = cdm_var('notes');
        $insert_file['tags'] = cdm_var('tags');

        #check if its a group
        if(cdm_cookie('cdm_group_id')) {
            $insert_file['group_id'] = cdm_cookie('cdm_group_id');
            if(sp_cdm_group_client(cdm_cookie('cdm_group_id')) != false) {
                $insert_file['client_id'] = sp_cdm_group_client(cdm_cookie('cdm_group_id'));
            }

        }
        #check if client is set
        if(cdm_cookie('cdm_client_id') != '') {



            $insert_file['client_id'] = cdm_cookie('cdm_client_id');
        }
        foreach($insert_file as $key=>$value) {
            if(is_null($value)) {
                unset($insert_file[$key]);
            }
        }

        $wpdb->insert("".$wpdb->prefix."sp_cu", $insert_file);
        $json['file_id'] = $wpdb->insert_id;
        $file_id = $wpdb->insert_id;
        $uid = cdm_var('uid');
        $post = $insert_file;

        #mail
        if (cdm_var('page') == 'sp-client-document-manager-fileview') {
            $to            = $user_info->user_email;
            $email_subject = 'sp_cu_admin_user_email_subject';
            $email_body    = 'sp_cu_admin_user_email';
            $email_cc      = 'sp_cu_additional_admin_cc';
            $user_email    = false;
        } else {
            $to            = apply_filters('sp_cdm/mail/admin_email', get_option('admin_email'));
            $email_subject = 'sp_cu_admin_email_subject';
            $email_body    = 'sp_cu_admin_email';
            $email_cc      = 'sp_cu_additional_admin_emails';
            $user_email    = true;
        }
        #send admin email
        if (get_option($email_body) != "") {
            $headers[] = "" . __("From:", "sp-client-document-manager") . " " . $current_user->user_firstname . " " . $current_user->user_lastname . " <" . $current_user->user_email . ">\r\n";
            if (get_option($email_cc) != "") {
                $cc_admin = explode(",", get_option($email_cc));
                foreach ($cc_admin as $key => $email) {
                    if ($email != "") {
                        $pos = strpos($email, '@');
                        if ($pos === false) {
                            $role_emails = sp_cdm_find_users_by_role($email);
                            foreach ($role_emails as $keys => $role_email) {
                                $headers[] = 'Cc: ' . $role_email . '';
                            }
                        } else {
                            $headers[] = 'Cc: ' . $email . '';
                        }
                    }
                }
            }
            $message = sp_cu_process_email($file_id, stripslashes(get_option($email_body)));
            $subject = sp_cu_process_email($file_id, stripslashes(get_option($email_subject)));
            add_filter('wp_mail_content_type', 'set_html_content_type');
            wp_mail($to, $subject, $message, apply_filters('sp_cdm/mail/headers', $headers, wp_get_current_user(), $to, $subject, $message), $attachments);
            remove_filter('wp_mail_content_type', 'set_html_content_type');
            unset($headers);
            unset($pos);
        }
        if (get_option('sp_cu_user_email') != "" && $user_email == true) {
            $subject = sp_cu_process_email($file_id, stripslashes(get_option('sp_cu_user_email_subject')));
            $message = sp_cu_process_email($file_id, stripslashes(get_option('sp_cu_user_email')));

            $user_info = get_userdata($user_ID);
            $to      = $user_info->user_email;
            if (get_option('sp_cu_additional_user_emails') != "") {
                $cc_user = explode(",", get_option('sp_cu_additional_user_emails'));
                foreach ($cc_user as $key => $user_email) {
                    if ($user_email != "") {
                        $pos = strpos($user_email, '@');
                        if ($pos === false) {
                            $role_user_emails = sp_cdm_find_users_by_role($user_email);
                            foreach ($role_user_emails as $keys => $role_user_email) {
                                $user_headers[] = 'Cc: ' . $role_user_email . '';
                            }
                        } else {
                            $user_headers[] = 'Cc: ' . $user_email . '';
                        }
                    }
                }
            }
            $message      = apply_filters('spcdm_user_email_message', $message, $post, $uid);
            $to           = apply_filters('spcdm_user_email_to', $to, $post, $uid);
            $subject      = apply_filters('spcdm_user_email_subject', $subject, $post, $uid);
            $attachments  = apply_filters('spcdm_user_email_attachments', $attachments, $post, $uid);
            $user_headers = apply_filters('spcdm_user_email_headers', $user_headers, $post, $uid);
            add_filter('wp_mail_content_type', 'set_html_content_type');
            wp_mail($to, $subject, $message, apply_filters('sp_cdm/mail/headers', $user_headers, apply_filters('sp_cdm/mail/admin_email', get_option('admin_email')), $to, $subject, $message), $attachments);
            remove_filter('wp_mail_content_type', 'set_html_content_type');
        }



        #mail
        $json['success'] = '1';
        echo json_encode($json);
        die();



    }

    public function add_form($html)
    {

        global $wpdb;



        $html = apply_filters('sp_cdm_media_before_form', $html);
        $html .='<div style="display:none">
		
			
			<div class="remodal" data-remodal-id="add-embed" data-remodal-options="{ \'hashTracking\': false }">
			'. sp_cdm_media_uploader::upload_dialog().'
					</div></div>';

        return $html;
    }



     public function upload_dialog()
     {
         global $wpdb;
         global $current_user;

         if($current_user->ID != '') {
             if (cdm_var('id') != '') {
                 $uid =cdm_var('id');
             } else {
                 $uid = $current_user->ID;
             }

             $html = '




<form  action="' . $_SERVER['REQUEST_URI'] . '" method="post" enctype="multipart/form-data" id="cdm_embed_media" >
<input type="hidden" name="pid" value="0" class="cdm_premium_pid_field">
<input type="hidden" name="action" value="sp_cdm_media_save_embed">
<input type="hidden" name="uid" value="'.$uid .'">
';

             if(cdm_var('page') == 'sp-client-document-manager-fileview') {
                 $html .='<input type="hidden" name="admin-uploader" value="1">';
             }
             $html .= '<div>';



             $html .='<p>
		<label>' . __("File Name", "sp-client-document-manager") . ' <span style="color:red">*<span></label>
		<input  type="text" name="file-name" class="required_name" >';

             $html .='</p> ';
             if(function_exists('sp_cdm_display_categories')) {
                 //$html .= sp_cdm_display_projects();
                 $html .= sp_cdm_display_categories();

             }


             $html .=' <p>
 <label>' . __("Embed Code", "sp-client-document-manager") . '</label>
   <textarea id="tags" name="embed"  style="width:90%;height:100px"></textarea>

  </p>';



             if (get_option('sp_cu_enable_tags') == 1) {
                 $html .= '

 <p>
 <label>' . __("Tags:", "sp-client-document-manager") . '</label>
   <textarea id="tags" name="tags"  style="width:90%;height:30px"></textarea>

  </p>';


             } else {
                 $html .= '<p>

    <label>' . __("Notes", "sp-client-document-manager") . ':</label>
	<textarea style="width:90%;height:50px" name="dlg-upload-notes"></textarea>

  </p>

  ';


             }
             if(function_exists('display_sp_cdm_form')) {
                 $html .= display_sp_cdm_form();
             }
             $spcdm_form_upload_fields = '';
             $spcdm_form_upload_fields .= apply_filters('spcdm_form_upload_fields', $spcdm_form_upload_fields);

             $html .= $spcdm_form_upload_fields;


             $html .= '

		
			<div style="padding-top:15px">
					<input type="submit"  class="btn btn-primary" value="' . __("Add Embeded Video", "sp-client-document-manager").'">
</div>
			
				

						<div class="sp_change_indicator" ></div>	
			<div class="cdm_debug"></div>
						';
             $html .= '

</div>';
             $timestamp = time();
             $html .= '



	</form>

		

	

	';

             return $html;
         }
     }
    public function button($html)
    {
        if(sp_cdm_is_featured_disabled('base', 'cdm_add_video') == false) {
            $html .= '  <a href="#" data-modal="add-embed" class="sp_cdm_open_modal sp_cdm_add_file hide_add_file_permission">'.__('Embed Video', 'sp-client-document-manager').'</a> ';
        }
        return $html;
    }



}
