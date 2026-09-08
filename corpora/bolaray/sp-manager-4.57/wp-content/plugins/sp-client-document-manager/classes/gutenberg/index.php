<?php
/*
new cdm_blocks;
class cdm_blocks{

    function __construct(){

    $this->name_space = 'sp_client_document_manager';
    $this->block_dir = ''.SP_CDM_UPLOADS_DIR.'/classes/gutenberg/blocks/';
    $this->block_dir_uri = ''.SP_CDM_PLUGIN_URL.'/classes/gutenberg/blocks/';

    $this->block_ver = '1.0.1';

        add_action("init",array($this,'sp_client_document_manager'));
    }
public function sp_client_document_manager( ) {

        $block_name = 'uploader';

        $block_namespace = 'sp-cdm/' . $block_name;

        $script_slug = $this->name_space. '-' . $block_name;

        // The JS block script
        $script_file =  $this->block_dir_uri.$block_name . '/block.build.js';
        # $script_path =  $this->block_dir.$block_name . '/block.build.js';

        wp_enqueue_script(
            $script_slug,
           $script_file,
            [   // Dependencies that will have to be imported on the block JS file
                'wp-blocks', // Required: contains registerBlockType function that creates a block
                'wp-element', // Required: contains element function that handles HTML markup
                'wp-editor', // Required: contains RichText component for editable inputs
                'wp-i18n', // contains registerBlockType function that creates a block

            ],
            $this->block_ver
        );



        // Registering the block
        register_block_type(
            $block_namespace,  // Block name with namespace
           [
             'api_version' => 2,

        'attributes'      => array(
            'selectControl'             => array(
                'type' => 'string',
                'default' => '0',
            )
        ),
            'render_callback' => [$this,'main_shortcode'],
            ]
        );

    }

    function main_shortcode(){

            return do_shortcode('[sp-client-document-manager]');
    }

}

*/
