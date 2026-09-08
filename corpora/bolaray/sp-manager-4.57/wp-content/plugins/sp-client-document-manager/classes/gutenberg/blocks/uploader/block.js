/** 
 * Simple block 
 * 
 * Creates a simple block that makes a red title
 * 
 * @requires Gutenberg 4.3
 */

// Required components
const { registerBlockType } = wp.blocks;        // registerBlockType function that creates a block
const { Fragment } = wp.element;
// Other components
const { __ } = wp.i18n;     // Internationalisation
const { serverSideRender: ServerSideRender } = wp;
/**
 * Registers and creates block
 * 
 * @param {string} Name Name of the block with a required name space
 * @param {object} ObjectArgs Block configuration {
 *      title - Title, displayed in the editor
 *      icon - Icon, from WP icons
 *      category - Block category, where the block will be added in the editor
 *      attributes - Object with all binding elements between the view HTML and the functions 
 *      edit function - Returns the markup for the editor interface.
 *      save function - Returns the markup that will be rendered on the site page
 * }
 */
registerBlockType(
    'sp-cdm/uploader', // Name of the block with a required name space
    {
	    title: __('Smarty Document Manager Uploader'), // Title, displayed in the editor
	    icon: 'universal-access-alt', // Icon, from WP icons
	    category: 'common', // Block category, where the block will be added in the editor
        
        /**
         * edit function
         * 
         * Makes the markup for the editor interface.
         * 
         * @param {object} ObjectArgs {
         *      className - Automatic CSS class. Based on the block name: gutenberg-block-samples-block-simple
         * }
         * 
         * @return {JSX object} ECMAScript JSX Markup for the editor 
         */
    edit: props => {
        return <ServerSideRender
        block="sp-cdm/uploader"
        attributes={ props.attributes }
    />
    },
 
		  save() {
        return null;
    },

    } 
);