<?php


if (! defined('ABSPATH')) {
    exit; // Exit if accessed directly
}


$cdm_download_file = new cdm_download_file();

add_action('init', array($cdm_download_file, 'download'), -100);
add_action('init', array($cdm_download_file, 'download_project'));

class cdm_download_file
{
    public function download_project()
    {
        if(@cdm_var('action') == 'cdm_download_project') {

            global $wpdb, $current_user;

            #ini_set('display_errors', 1);
            #ini_set('display_startup_errors', 1);
            #error_reporting(E_ALL);
            define('WP_MEMORY_LIMIT', '1024M');
            ini_set('memory_limit', '1024M');

            $pid     = sanitize_text_field(cdm_var('id'));


            if(cdm_folder_permissions($pid) == 0) {
                #exit('You do not have folder permissions');
            }
            if(!is_user_logged_in()) {
                exit('Not logged in');
            }





            $folders   = $wpdb->get_results($wpdb->prepare("SELECT *  FROM " . $wpdb->prefix . "sp_cu_project where id = %d", $pid), ARRAY_A);
            if($folders[0]['recycle'] == 1) {
                echo '<strong>Error:</strong> 404 Folder not found';
                die();
            }
            $zip_dir = "" . SP_CDM_UPLOADS_DIR."".md5(SP_CDM_UPLOADS_DIR)."/";
            $zip_path        = '' . SP_CDM_UPLOADS_DIR_URL . '' . md5(SP_CDM_UPLOADS_DIR). '/';

            $return_file = "" . preg_replace('/[^\w\d_ -]/si', '', sanitize_title($folders[0]['name'])) . "-".time().".zip";
            ob_start();
            $zip         = new SPCDM_Zip($return_file);

            for ($j = 0; $j < count($folders); $j++) {

                $zip->addDirectory(spdm_ajax::folder_name($folders[$j]['id']));

                $r =  spdm_ajax::folder_files($folders[$j]['id']);

                for ($i = 0; $i < count($r); $i++) {

                    $dir         = '' . SP_CDM_UPLOADS_DIR . '' . $r[$i]['uid'] . '/';

                    do_action('cdm/zip/before_add_file', $r[$i]);

                    if(file_exists($dir . $r[$i]['file'])) {
                        $zip->addFile(spdm_ajax::get_file($dir . $r[$i]['file']), spdm_ajax::folder_name($folders[$j]['id']).'/'.$r[$i]['file']);
                        do_action('cdm/zip/after_add_file', $r[$i]);

                        unset($dir);


                    }
                }
                spdm_ajax::sub_folders($folders[$j]['id'], spdm_ajax::folder_name($folders[$j]['id']), $zip);

            }
            $zip->finalize();
            ob_end_flush();
            #$zip->getZipData( $return_file);
            die();
        }
    }


    public function download($revision=false)
    {
        global $current_user,$wpdb;



        if($revision != false) {
            $file_id  = sanitize_text_field($revision);
        } else {
            $file_id  = sanitize_text_field(cdm_var('cdm-download-file-id'));
        }

        if($file_id) {


            ini_set('memory_limit', '1024M');









            if ((is_user_logged_in() && get_option('sp_cu_user_require_login_download') == 1) or (get_option('sp_cu_user_require_login_download') == '' or get_option('sp_cu_user_require_login_download') == 0)) {

                do_action('wp_cdm_download_before');


                $file_decrypt = base64_decode($file_id);
                $file_arr = explode("|", $file_decrypt);

                #print_r($file_arr);
                $fid = $file_arr[0];
                $file_date = $file_arr[1];
                $file_name = $file_arr[2];
                $file_name = str_replace('~', '%', $file_name);


                if(!is_numeric($fid)) {
                    header("HTTP/1.0 404 Not Found");
                    die();
                }
                if(class_exists('cdmProductivityLog')) {

                    $cdm_log = new cdmProductivityLog();

                    $cdm_log->add($fid, $current_user->ID);

                }

                if($revision != false) {
                    $query = $wpdb->prepare("SELECT *  FROM ".$wpdb->prefix."sp_cu   where id= %d ", sanitize_text_field($fid));

                } else {
                    $query = $wpdb->prepare("SELECT *  FROM ".$wpdb->prefix."sp_cu   where id= %d AND date = %s order by date desc", sanitize_text_field($fid), sanitize_text_field($file_date));

                }


                $r = $wpdb->get_results($query, ARRAY_A);

                if(get_option('sp_cu_user_require_login_download') == 1) {

                    if (
                        (
                            cdm_folder_permissions($r[0]['pid']) == 1 or
         $current_user->ID == $r[0]['uid'] or
         current_user_can('manage_options') == true or
         get_option('sp_cu_release_the_kraken') == 1 or
         (isset($_REQUEST['_ckey']) && wp_verify_nonce($_REQUEST['_ckey'], 'cdm-public-download')) or
          (isset($_REQUEST['_key']) && wp_verify_nonce($_REQUEST['_key'], 'cdm-public-download'))
                        )) {



                        $can_download = 1;
                    } else {


                        echo '<strong>Error:</strong> '.strip_tags(esc_attr(get_option('sp_cdm_permission_error_download', '404: File not found'))).'';
                        die();
                    }
                    if($r[0]['recycle'] == 1) {
                        echo '<strong>Error:</strong> 404 File not found';
                        die();
                    }
                }
                if($r[0]['file'] == 'link') {
                    cdm_event_log($r[0]['id'], $current_user->ID, 'file', ''.__('File Link Downloaded', 'sp-client-document-manager').'');


                    wp_redirect($r[0]['url']);
                    exit;
                }
                $parent_exists =	cdm_parent_exists($r[0]['parent']);
                if($parent_exists == false) {
                    header("HTTP/1.0 404 Not Found");
                    die();
                }




                if($r[0]['aws_key'] == '' && $r[0]['gdo_file_id'] == '') {
                    #print_r($_SERVER);
                    #echo SP_CDM_UPLOADS_DIR;
                    #$cdm_upload_dir = wp_upload_dir();
                    #print_r($cdm_upload_dir);


                    if($r == false or (!file_exists(''.SP_CDM_UPLOADS_DIR.''.$r[0]['uid'].'/'.$r[0]['file'].'') && !file_exists(''.SP_CDM_UPLOADS_DIR.''.$r[0]['uid'].'/'.$r[0]['file'].'.lock'))) {


                        header("HTTP/1.0 404 Not Found");
                        die();
                    }


                    $r_rev_check = $wpdb->get_results("SELECT *  FROM ".$wpdb->prefix."sp_cu   where parent= '".$r[0]['id']."'  order by date desc", ARRAY_A);

                    if(count($r_rev_check) > 0 && cdm_var('original') == '') {



                        unset($r);

                        $r = $wpdb->get_results("SELECT *  FROM ".$wpdb->prefix."sp_cu   where id= '".$r_rev_check[0]['id']."'  order by date desc", ARRAY_A);

                    }

                }





                do_action('sp_download_file_after_query', $r);





                if(get_option('sp_cu_js_redirect') == 1) {

                    $file = ''.SP_CDM_UPLOADS_DIR_URL.''.$r[0]['uid'].'/'.$r[0]['file'].'';

                    echo '<script type="text/javascript">

<!--

window.location = "'.$file.'"

//-->

</script>';
                    cdm_event_log($r[0]['id'], $current_user->ID, 'file', ''.__('File Downloaded', 'sp-client-document-manager').'');


                    exit;

                } else {



                    $file = ''.SP_CDM_UPLOADS_DIR.''.$r[0]['uid'].'/'.$r[0]['file'].'';






                    // grab the requested file's name

                    $file_name = $file ;


                    // make sure it's a file before doing anything!

                    if(is_file($file_name)) {



                        /*

                          Do any processing you'd like here:

                          1.  Increment a counter

                          2.  Do something with the DB

                          3.  Check user permissions

                          4.  Anything you want!

                        */





                        $mime = mime_content_type($file_name);


                        if(! is_readable($file_name)) {
                            echo 'Error: File does not exist';
                            exit;
                        }
                        cdm_event_log($r[0]['id'], $current_user->ID, 'file', ''.__('File Downloaded', 'sp-client-document-manager').'');



                        if(cdm_var('thumb')== 1) {
                            // required for IE
                            ob_start();
                            ob_clean();


                            header('Content-Type: '.$mime);

                            readfile($file_name);    // push it out

                            exit();

                        } else {
                            if(function_exists('set_time_limit')) {
                                set_time_limit(0);
                            }

                            smartReadFile($file_name, sp_client_upload_filename_direct($r[0]['id']), $mime);

                            exit(0);

                        }

                    }









                }

            } else {

                auth_redirect();


            }
        }
    }
}
