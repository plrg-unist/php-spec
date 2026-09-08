<?php

require_once('../config.php');
class Users extends DBConnection
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
    public function save_users()
    {
        extract($_POST);
        $id = $_POST['id'];
        $username = $_POST['username'];
        $password = $_POST['password'];
        $firstname = $_POST['firstname'];
        $lastname = $_POST['lastname'];
        $avatar = $_POST['avatar'];
        $type = $_POST['type'];
        $data = '';
        $qry = $this->conn->query("SELECT * FROM `users` where username ='{$username}' ".($id<=0 ? "" : " and id!= '{$id}' "));
        $chk = $qry->num_rows;
        if($chk > 0) {
            return 3;
            exit;
        }
        foreach($_POST as $k => $v) {
            if(!in_array($k, array('id','password'))) {
                if(!empty($data)) {
                    $data .=" , ";
                }
                $data .= " {$k} = '{$v}' ";
            }
        }
        if(!empty($password)) {
            $password = md5($password);
            if(!empty($data)) {
                $data .=" , ";
            }
            $data .= " `password` = '{$password}' ";
        }

        if(isset($_FILES['img']) && $_FILES['img']['tmp_name'] != '') {
            $fname = 'uploads/'.strtotime(date('y-m-d H:i')).'_'.$_FILES['img']['name'];
            $move = move_uploaded_file($_FILES['img']['tmp_name'], '../'. $fname);
            if($move) {
                $data .=" , avatar = '{$fname}' ";
                if(isset($_SESSION['userdata']['avatar']) && is_file('../'.$_SESSION['userdata']['avatar']) && $_SESSION['userdata']['id'] == $id) {
                    unlink('../'.$_SESSION['userdata']['avatar']);
                }
            }
        }
        if(empty($id)) {
            $qry = $this->conn->query("INSERT INTO users set firstname = '{$firstname}', lastname = '{$lastname}', username = '{$username}', password = '{$password}', avatar = '$avatar', type = '{$type}'");
            if($qry) {
                $this->settings->set_flashdata('success', 'User Details successfully saved.');
                return 1;
            } else {
                return 2;
            }

        } else {
            $qry = $this->conn->query("UPDATE users set firstname = '{$firstname}', lastname = '{$lastname}', username = '{$username}', password = '{$password}', avatar = '$avatar', type = '{$type}' where id = {$id}");
            if($qry) {
                $this->settings->set_flashdata('success', 'User Details successfully updated.');
                foreach($_POST as $k => $v) {
                    if($k != 'id') {
                        if(!empty($data)) {
                            $data .=" , ";
                        }
                        $this->settings->set_userdata($k, $v);
                    }
                }
                if(isset($fname) && isset($move)) {
                    $this->settings->set_userdata('avatar', $fname);
                }

                return 1;
            } else {
                return "UPDATE users set firstname = '{$firstname}', lastname = '{$lastname}', username = '{$username}', password = '{$password}', avatar = '$avatar', type = '{$type}' where id = {$id}";
            }

        }
    }
    public function delete_users()
    {
        extract($_POST);
        $id = $_POST['id'];
        $qry = $this->conn->query("SELECT avatar FROM users where id = '{$id}'");
        $avatars = $qry->fetch_array();
        $avatar = $avatars['avatar'];
        $qry = $this->conn->query("DELETE FROM users where id = $id");
        if($qry) {
            $this->settings->set_flashdata('success', 'User Details successfully deleted.');
            if(is_file(base_app.$avatar)) {
                unlink(base_app.$avatar);
            }
            $resp['status'] = 'success';
        } else {
            $resp['status'] = 'failed';
        }
        return json_encode($resp);
    }
}

$users = new users();
$action = !isset($_GET['f']) ? 'none' : strtolower($_GET['f']);
switch ($action) {
    case 'save':
        echo $users->save_users();
        break;
    case 'delete':
        echo $users->delete_users();
        // no break
    default:
        // echo $sysset->index();
        break;
}
