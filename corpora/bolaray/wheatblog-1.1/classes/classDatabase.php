<?php

// File:    classDatabase.php
// License: GNU GPL
// Descrip: Abstracts the database into a PHP class.



class DatabaseClass
{
    public $db;
    public $result;



    public function DatabaseClass()
    {
        global $site, $user, $pass, $database;

        $this->db = DB_connect($site, $user, $pass);
        DB_select_db($database, $this->db);
    }



    public function query($qry)
    {
        $this->result = DB_query($qry, $this->db);
        return $this->result;
    }



    public function num_rows($argResult = '')
    {
        $argResult = ($argResult=='') ? $this->result : $argResult;
        return DB_num_rows($argResult);
    }


    public function fetchArray($argResult='')
    {
        $argResult = ($argResult=='') ? $this->result : $argResult;
        return DB_fetch_array($argResult);
    }


    public function insertId($argDB='')
    {
        $argDB = ($argDB == '') ? $this->db : $argDB;
        return DB_insert_id($argDB);
    }


    public function debug($arg)
    {
        die("$arg");
    }
    public function warn($arg)
    {
        echo("$arg");
    }
    public function quote($txt)
    {
        return DB_quote($txt);
    }

}
