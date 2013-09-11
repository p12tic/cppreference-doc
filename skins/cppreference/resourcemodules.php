<?php
/*
 * Definition of resources (CSS and Javascript) required for this skin.
 * This file must be included from LocalSettings.php since that is the only way
 * that this file is included by loader.php
 */
global $wgResourceModules;

$wgResourceModules['skins.cppreference'] = array(
   'styles' => array( 'cppreference/screen.css' => array( 'media' => 'screen' ) ),
   'remoteBasePath' => &$GLOBALS['wgStylePath'],
   'localBasePath' => &$GLOBALS['wgStyleDirectory'],
);
?>
