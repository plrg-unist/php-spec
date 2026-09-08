<?php

require_once('../config.php');
class Master extends DBConnection
{
    private $settings;
    public function __construct()
    {
        global $_settings;
        $this->settings = $_settings;
        parent::__construct();
    }
    public function __destruct()
    {
        parent::__destruct();
    }
    public function capture_err()
    {
        if(!$this->conn->error) {
            return false;
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = $this->conn->error;
            return json_encode($resp);
            exit;
        }
    }
    public function delete_img()
    {
        extract($_POST);
        $path = $_POST['path'];
        $resp = array();
        if(is_file($path)) {
            if(unlink($path)) {
                $resp['status'] = 'success';
            } else {
                $resp['status'] = 'failed';
                $resp['error'] = 'failed to delete '.$path;
            }
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = 'Unkown '.$path.' path';
        }
        return json_encode($resp);
    }
    public function save_category()
    {
        extract($_POST);
        $id = $_POST['id'];
        $name = $_POST['name'];
        $description = $_POST['description'];
        $status = $_POST['status'];
        $delete_flag = $_POST['delete_flag'];
        $data = "";
        foreach($_POST as $k =>$v) {
            if(!in_array($k, array('id'))) {
                if(!empty($data)) {
                    $data .=",";
                }
                $v = $this->conn->real_escape_string($v);
                $data .= " `{$k}`='{$v}' ";
            }
        }
        $qry = $this->conn->query("SELECT * FROM `category_list` where `name` = '{$name}' ".(empty($id) ? "" : " and id != {$id} ")." ");
        $check = $qry->num_rows;
        if($this->capture_err()) {
            return $this->capture_err();
        }
        if($check > 0) {
            $resp['status'] = 'failed';
            $resp['msg'] = "Category Name already exists.";
            return json_encode($resp);
            exit;
        }
        if(empty($id)) {
            $sql = "INSERT INTO `category_list` set name = $name, description = $description, status = $status, delete_flag = $delete_flag ";
        } else {
            $sql = "UPDATE `category_list` set name = $name, description = $description, status = $status, delete_flag = $delete_flag  where id = '{$id}' ";
        }
        $save = $this->conn->query($sql);
        if($save) {
            $bid = !empty($id) ? $id : $this->conn->insert_id;
            $resp['status'] = 'success';
            if(empty($id)) {
                $resp['msg'] = "New Category successfully saved.";
            } else {
                $resp['msg'] = " Category successfully updated.";
            }

        } else {
            $resp['status'] = 'failed';
            $resp['err'] = $this->conn->error."[{$sql}]";
        }
        if($resp['status'] == 'success') {
            $this->settings->set_flashdata('success', $resp['msg']);
        }
        return json_encode($resp);
    }
    public function delete_category()
    {
        extract($_POST);
        $id = $_POST['id'];
        $del = $this->conn->query("UPDATE `category_list` set `delete_flag` = 1 where id = '{$id}'");
        if($del) {
            $resp['status'] = 'success';
            $this->settings->set_flashdata('success', " category successfully deleted.");
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = $this->conn->error;
        }
        return json_encode($resp);

    }
    public function save_post()
    {
        if(empty($_POST['id'])) {
            $_POST['user_id'] = $this->settings->userdata('id');
        }
        if(isset($_POST['status'])) {
            $_POST['status'] = 1;
        } else {
            $_POST['status'] = 0;
        }

        extract($_POST);
        $id = $_POST['id'];
        $user_id = $_POST['userid'];
        $category_id = $_POST['category_id'];
        $title = $_POST['title'];
        $content = $_POST['content'];
        $status = $_POST['status'];
        $delete_flag = $_POST['delete_flag'];
        $data = "";
        foreach($_POST as $k =>$v) {
            if(!in_array($k, array('id'))) {
                if(!empty($data)) {
                    $data .=",";
                }
                $v = $this->conn->real_escape_string($v);
                $data .= " `{$k}`='{$v}' ";
            }
        }
        if(empty($id)) {
            $sql = "INSERT INTO `post_list` set user_id = $user_id, category_id = $category_id, title = $title, content = $content, status = $status, delete_flag = $delete_flag ";
        } else {
            $sql = "UPDATE `post_list` set user_id = $user_id, category_id = $category_id, title = $title, content = $content, status = $status, delete_flag = $delete_flag where id = '{$id}' ";
        }
        $save = $this->conn->query($sql);
        if($save) {
            $pid = !empty($id) ? $id : $this->conn->insert_id;
            $resp['pid'] = $pid;
            $resp['status'] = 'success';
            if(empty($id)) {
                $resp['msg'] = "New Post successfully saved.";
            } else {
                $resp['msg'] = " Post successfully updated.";
            }

        } else {
            $resp['status'] = 'failed';
            $resp['err'] = $this->conn->error."[{$sql}]";
        }
        if($resp['status'] == 'success') {
            $this->settings->set_flashdata('success', $resp['msg']);
        }
        return json_encode($resp);
    }
    public function delete_post()
    {
        extract($_POST);
        $id = $_POST['id'];
        $del = $this->conn->query("UPDATE `post_list` set `delete_flag` = 1 where id = '{$id}'");
        if($del) {
            $resp['status'] = 'success';
            $this->settings->set_flashdata('success', " Post successfully deleted.");
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = $this->conn->error;
        }
        return json_encode($resp);

    }
    public function save_comment()
    {
        if(empty($_POST['id'])) {
            $_POST['user_id'] = $this->settings->userdata('id');
        }
        extract($_POST);
        $id = $_POST['id'];
        $user_id = $_POST['userid'];
        $post_id = $_POST['post_id'];
        $comment = $_POST['comment'];
        $data = "";
        foreach($_POST as $k =>$v) {
            if(!in_array($k, array('id'))) {
                if(!empty($data)) {
                    $data .=",";
                }
                $v = $this->conn->real_escape_string($v);
                $data .= " `{$k}`='{$v}' ";
            }
        }
        if(empty($id)) {
            $sql = "INSERT INTO `comment_list` set user_id = $user_id, post_id = $post_id, comment = $comment ";
        } else {
            $sql = "UPDATE `comment_list` set user_id = $user_id, post_id = $post_id, comment = $comment  where id = '{$id}' ";
        }
        $save = $this->conn->query($sql);
        if($save) {
            $pid = !empty($id) ? $id : $this->conn->insert_id;
            $resp['status'] = 'success';
            if(empty($id)) {
                $resp['msg'] = "New Comment successfully added.";
            } else {
                $resp['msg'] = " Comment successfully updated.";
            }

        } else {
            $resp['status'] = 'failed';
            $resp['err'] = $this->conn->error."[{$sql}]";
        }
        if($resp['status'] == 'success') {
            $this->settings->set_flashdata('success', $resp['msg']);
        }
        return json_encode($resp);
    }
    public function delete_comment()
    {
        extract($_POST);
        $id = $_POST['id'];
        $del = $this->conn->query("DELETE FROM `comment_list` where id = '{$id}'");
        if($del) {
            $resp['status'] = 'success';
            $this->settings->set_flashdata('success', " Comment successfully deleted.");
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = $this->conn->error;
        }
        return json_encode($resp);

    }
    public function save_transaction()
    {
        if(empty($_POST['id'])) {
            $_POST['user_id'] = $this->settings->userdata('id');
            $prefix = date("Ymd");
            $code = sprintf("%'.04d", 1);
            while(true) {
                $qry = $this->conn->query("SELECT * FROM `transaction_list` where code = '{$prefix}{$code}' ");
                $check = $qry->num_rows;
                if($check > 0) {
                    $code = sprintf("%'.04d", abs($code) + 1);
                } else {
                    $_POST['code'] = $prefix.$code;
                    break;
                }
            }
        }
        extract($_POST);
        $data = "";
        foreach($_POST as $k =>$v) {
            if(!in_array($k, array('id')) && !is_array($_POST[$k])) {
                if(!empty($data)) {
                    $data .=",";
                }
                $v = $this->conn->real_escape_string($v);
                $data .= " `{$k}`='{$v}' ";
            }
        }
        if(empty($id)) {
            $sql = "INSERT INTO `transaction_list` set {$data} ";
        } else {
            $sql = "UPDATE `transaction_list` set {$data} where id = '{$id}' ";
        }
        $save = $this->conn->query($sql);
        if($save) {
            $tid = !empty($id) ? $id : $this->conn->insert_id;
            $resp['tid'] = $tid;
            $resp['status'] = 'success';
            if(empty($id)) {
                $resp['msg'] = "New Transaction successfully saved.";
            } else {
                $resp['msg'] = " Transaction successfully updated.";
            }
            if(isset($category_id)) {
                $data = "";
                foreach($category_id as $k =>$v) {
                    $sid = $v;
                    $price = $this->conn->real_escape_string($category_price[$k]);
                    if(!empty($data)) {
                        $data .= ", ";
                    }
                    $data .= "('{$tid}', '{$sid}', '{$price}')";
                }
                if(!empty($data)) {
                    $this->conn->query("DELETE FROM `transaction_categorys` where transaction_id = '{$tid}'");
                    $sql_category = "INSERT INTO `transaction_categorys` (`transaction_id`, `category_id`, `price`) VALUES {$data}";
                    $save_categorys = $this->conn->query($sql_category);
                    if(!$save_categorys) {
                        $resp['status'] = 'failed';
                        $resp['sql'] = $sql_category;
                        $resp['error'] = $this->conn->error;
                        if(empty($id)) {
                            $resp['msg'] = "Transaction has failed save.";
                            $this->conn->query("DELETE FROM `transaction_categorys` where transaction_id = '{$tid}'");
                        } else {
                            $resp['msg'] = "Transaction has failed update.";
                        }
                        return json_encode($resp);
                    }
                }
            }
            if(isset($comment_id)) {
                $data = "";
                foreach($comment_id as $k =>$v) {
                    $pid = $v;
                    $price = $this->conn->real_escape_string($comment_price[$k]);
                    $qty = $this->conn->real_escape_string($comment_qty[$k]);
                    if(!empty($data)) {
                        $data .= ", ";
                    }
                    $data .= "('{$tid}', '{$pid}', '{$qty}', '{$price}')";
                }
                if(!empty($data)) {
                    $this->conn->query("DELETE FROM `transaction_comments` where transaction_id = '{$tid}'");
                    $sql_comment = "INSERT INTO `transaction_comments` (`transaction_id`, `comment_id`,`qty`, `price`) VALUES {$data}";
                    $save_comments = $this->conn->query($sql_comment);
                    if(!$save_comments) {
                        $resp['status'] = 'failed';
                        $resp['sql'] = $sql_comment;
                        $resp['error'] = $this->conn->error;
                        if(empty($id)) {
                            $resp['msg'] = "Transaction has failed save.";
                            $this->conn->query("DELETE FROM `transaction_comments` where transaction_id = '{$tid}'");
                        } else {
                            $resp['msg'] = "Transaction has failed update.";
                        }
                        return json_encode($resp);
                    }
                }
            }
        } else {
            $resp['status'] = 'failed';
            $resp['err'] = $this->conn->error."[{$sql}]";
        }
        if($resp['status'] == 'success') {
            $this->settings->set_flashdata('success', $resp['msg']);
        }
        return json_encode($resp);
    }
    public function delete_transaction()
    {
        extract($_POST);
        $del = $this->conn->query("DELETE FROM `transaction_list` where id = '{$id}'");
        if($del) {
            $resp['status'] = 'success';
            $this->settings->set_flashdata('success', " Transaction successfully deleted.");
        } else {
            $resp['status'] = 'failed';
            $resp['error'] = $this->conn->error;
        }
        return json_encode($resp);

    }
    public function update_status()
    {
        extract($_POST);
        $update = $this->conn->query("UPDATE `transaction_list` set `status` = '{$status}' where id = '{$id}'");
        if($update) {
            $resp['status'] = 'success';
        } else {
            $resp['status'] = 'failed';
            $resp['msg'] = "Transaction's status has failed to update.";
        }
        if($resp['status'] == 'success') {
            $this->settings->set_flashdata('success', 'Transaction\'s Status has been updated successfully.');
        }
        return json_encode($resp);
    }
}

$Master = new Master();
$action = !isset($_GET['f']) ? 'none' : strtolower($_GET['f']);
$sysset = new SystemSettings();
switch ($action) {
    case 'delete_img':
        echo $Master->delete_img();
        break;
    case 'save_category':
        echo $Master->save_category();
        break;
    case 'delete_category':
        echo $Master->delete_category();
        break;
    case 'save_post':
        echo $Master->save_post();
        break;
    case 'delete_post':
        echo $Master->delete_post();
        break;
    case 'save_comment':
        echo $Master->save_comment();
        break;
    case 'delete_comment':
        echo $Master->delete_comment();
        break;
    case 'save_inventory':
        echo $Master->save_inventory();
        break;
    case 'delete_inventory':
        echo $Master->delete_inventory();
        break;
    case 'save_transaction':
        echo $Master->save_transaction();
        break;
    case 'delete_transaction':
        echo $Master->delete_transaction();
        break;
    case 'update_status':
        echo $Master->update_status();
        break;
    default:
        // echo $sysset->index();
        break;
}
