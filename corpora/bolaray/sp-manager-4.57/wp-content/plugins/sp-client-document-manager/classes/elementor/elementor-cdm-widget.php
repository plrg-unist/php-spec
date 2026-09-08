<?php
/**
 * Plugin Name: Elementor CDM Widget
 * Description: Add CDM to any page
 * Plugin URI:  https://elementor.com/
 * Version:     1.0.0
 * Author:      Elementor Developer
 * Author URI:  https://developers.elementor.com/
 * Text Domain: elementor-oembed-widget
 *
 * Elementor tested up to: 3.5.0
 * Elementor Pro tested up to: 3.5.0
 */

if (! defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

/**
 * Register oEmbed Widget.
 *
 * Include widget file and register widget class.
 *
 * @since 1.0.0
 * @param \Elementor\Widgets_Manager $widgets_manager Elementor widgets manager.
 * @return void
 */
function register_cdm_widget($widgets_manager)
{

    require_once(__DIR__ . '/widgets/cdm-widget.php');

    $widgets_manager->register(new \Elementor_CDM_Widget());

}
add_action('elementor/widgets/register', 'register_cdm_widget');
