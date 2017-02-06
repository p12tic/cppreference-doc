<?php
/**
 * Cppreference2 skin. Based on Vector skin as of Mediawiki 1.19.
 *
 * Vector - Modern version of MonoBook with fresh look and many usability
 * improvements.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 *
 * @todo document
 * @file
 * @ingroup Skins
 */

if( !defined( 'MEDIAWIKI' ) ) {
	die( -1 );
}

#require_once(dirname(__FILE__)."/cppreference2/resourcemodules.php");

/**
 * SkinTemplate class for Cppreference2 skin
 * @ingroup Skins
 */
class SkinCppreference2 extends SkinTemplate {

	protected static $bodyClasses = array( 'vector-animateLayout' );

	var $skinname = 'cppreference2', $stylename = 'cppreference2',
		$template = 'Cppreference2Template', $useHeadElement = true;

	/**
	 * Initializes output page and sets up skin-specific parameters
	 * @param $out OutputPage object to initialize
	 */
	public function initPage( OutputPage $out ) {
		global $wgLocalStylePath;

		parent::initPage( $out );

		// Append CSS which includes IE only behavior fixes for hover support -
		// this is better than including this in a CSS fille since it doesn't
		// wait for the CSS file to load before fetching the HTC file.
		$min = $this->getRequest()->getFuzzyBool( 'debug' ) ? '' : '.min';
		$out->addHeadItem( 'csshover',
			'<!--[if lt IE 7]><style type="text/css">body{behavior:url("' .
				htmlspecialchars( $wgLocalStylePath ) .
				"/{$this->stylename}/csshover{$min}.htc\")}</style><![endif]-->"
		);

		$out->addModules( 'skins.cppreference2.js' );
	}

	/**
	 * Load skin and user CSS files in the correct order
	 * fixes bug 22916
	 * @param $out OutputPage object
	 */
	function setupSkinUserCss( OutputPage $out ) {
		parent::setupSkinUserCss( $out );
		$out->addModuleStyles( 'skins.cppreference2' );
	}

	/**
	 * Adds classes to the body element.
	 *
	 * @param $out OutputPage object
	 * @param &$bodyAttrs Array of attributes that will be set on the body element
	 */
	function addToBodyAttributes( $out, &$bodyAttrs ) {
		if ( isset( $bodyAttrs['class'] ) && strlen( $bodyAttrs['class'] ) > 0 ) {
			$bodyAttrs['class'] .= ' ' . implode( ' ', static::$bodyClasses );
		} else {
			$bodyAttrs['class'] = implode( ' ', static::$bodyClasses );
		}
	}
}

/**
 * QuickTemplate class for Cppreference2 skin
 * @ingroup Skins
 */
class Cppreference2Template extends BaseTemplate {

	/* Functions */

	/**
	 * Outputs the entire contents of the (X)HTML page
	 */
	public function execute() {
		global $wgVectorUseIconWatch;

		// Build additional attributes for navigation urls
		$nav = $this->data['content_navigation'];

		if ( $wgVectorUseIconWatch ) {
			$mode = $this->getSkin()->getUser()->isWatched( $this->getSkin()->getRelevantTitle() ) ? 'unwatch' : 'watch';
			if ( isset( $nav['actions'][$mode] ) ) {
				$nav['views'][$mode] = $nav['actions'][$mode];
				$nav['views'][$mode]['class'] = rtrim( 'icon ' . $nav['views'][$mode]['class'], ' ' );
				$nav['views'][$mode]['primary'] = true;
				unset( $nav['actions'][$mode] );
			}
		}

		$xmlID = '';
		foreach ( $nav as $section => $links ) {
			foreach ( $links as $key => $link ) {
				if ( $section == 'views' && !( isset( $link['primary'] ) && $link['primary'] ) ) {
					$link['class'] = rtrim( 'collapsible ' . $link['class'], ' ' );
				}

				$xmlID = isset( $link['id'] ) ? $link['id'] : 'ca-' . $xmlID;
				$nav[$section][$key]['attributes'] =
					' id="' . Sanitizer::escapeId( $xmlID ) . '"';
				if ( $link['class'] ) {
					$nav[$section][$key]['attributes'] .=
						' class="' . htmlspecialchars( $link['class'] ) . '"';
					unset( $nav[$section][$key]['class'] );
				}
				if ( isset( $link['tooltiponly'] ) && $link['tooltiponly'] ) {
					$nav[$section][$key]['key'] =
						Linker::tooltip( $xmlID );
				} else {
					$nav[$section][$key]['key'] =
						Xml::expandAttributes( Linker::tooltipAndAccesskeyAttribs( $xmlID ) );
				}
			}
		}
		$this->data['namespace_urls'] = $nav['namespaces'];
		$this->data['view_urls'] = $nav['views'];
		$this->data['action_urls'] = $nav['actions'];
		$this->data['variant_urls'] = $nav['variants'];

		// Reverse horizontally rendered navigation elements
		if ( $this->data['rtl'] ) {
			$this->data['view_urls'] =
				array_reverse( $this->data['view_urls'] );
			$this->data['namespace_urls'] =
				array_reverse( $this->data['namespace_urls'] );
		}
		// Output HTML Page
		$this->html( 'headelement' );

		global $Cppreference2SkinRootLink;
		$root_link = '/';
		if (isset($Cppreference2SkinRootLink)) {
			$root_link = htmlspecialchars($Cppreference2SkinRootLink);
		}
?>
		<!-- header -->
		<div id="mw-head" class="noprint">
			<div id="cpp-head-first-base">
				<div id="cpp-head-first">
					<h5><a href="<?php echo $root_link; ?>">
						<?php global $wgSitename; echo $wgSitename;?>
					</a></h5>
					<div id="cpp-head-search">
						<?php $this->renderNavigation( 'SEARCH' ); ?>
					</div>
					<div id="cpp-head-personal">
						<?php $this->renderNavigation( 'PERSONAL' ); ?>
					</div>

				</div>
			</div>
			<div id="cpp-head-second-base">
				<div id="cpp-head-second">
					<div id="cpp-head-tools-left">
						<?php $this->renderNavigation( array( 'NAMESPACES', 'VARIANTS' ) ); ?>
					</div>
					<div id="cpp-head-tools-right">
						<?php $this->renderNavigation( array( 'VIEWS', 'ACTIONS' ) ); ?>
					</div>
				</div>
			</div>
		</div>
		<!-- /header -->
		<!-- content -->
		<div id="cpp-content-base">
			<div id="content" class="mw-body" role="main">
				<a id="top"></a>
				<div id="mw-js-message" style="display:none;"<?php $this->html( 'userlangattributes' ) ?>></div>
				<?php if ( $this->data['sitenotice'] ): ?>
				<!-- sitenotice -->
				<div id="siteNotice"><?php $this->html( 'sitenotice' ) ?></div>
				<!-- /sitenotice -->
				<?php endif; ?>
				<!-- firstHeading -->
				<h1 id="firstHeading" class="firstHeading" lang="<?php
					$this->data['pageLanguage'] = $this->getSkin()->getTitle()->getPageViewLanguage()->getCode();
					$this->html( 'pageLanguage' );
				?>"><span dir="auto"><?php $this->html( 'title' ) ?></span></h1>
				<!-- /firstHeading -->
				<!-- bodyContent -->
				<div id="bodyContent">
					<?php if ( $this->data['isarticle'] ): ?>
					<!-- tagline -->
					<div id="siteSub"><?php $this->msg( 'tagline' ) ?></div>
					<!-- /tagline -->
					<?php endif; ?>
					<!-- subtitle -->
					<div id="contentSub"<?php $this->html( 'userlangattributes' ) ?>><?php $this->html( 'subtitle' ) ?></div>
					<!-- /subtitle -->
					<?php if ( $this->data['undelete'] ): ?>
					<!-- undelete -->
					<div id="contentSub2"><?php $this->html( 'undelete' ) ?></div>
					<!-- /undelete -->
					<?php endif; ?>
					<?php if( $this->data['newtalk'] ): ?>
					<!-- newtalk -->
					<div class="usermessage"><?php $this->html( 'newtalk' )  ?></div>
					<!-- /newtalk -->
					<?php endif; ?>
					<!-- bodycontent -->
					<?php $this->html( 'bodycontent' ) ?>
					<!-- /bodycontent -->
					<?php if ( $this->data['printfooter'] ): ?>
					<!-- printfooter -->
					<div class="printfooter">
					<?php $this->html( 'printfooter' ); ?>
					</div>
					<!-- /printfooter -->
					<?php endif; ?>
					<?php if ( $this->data['catlinks'] ): ?>
					<!-- catlinks -->
					<?php $this->html( 'catlinks' ); ?>
					<!-- /catlinks -->
					<?php endif; ?>
					<?php if ( $this->data['dataAfterContent'] ): ?>
					<!-- dataAfterContent -->
					<?php $this->html( 'dataAfterContent' ); ?>
					<!-- /dataAfterContent -->
					<?php endif; ?>
					<div class="visualClear"></div>
					<!-- debughtml -->
					<?php $this->html( 'debughtml' ); ?>
					<!-- /debughtml -->
				</div>
				<!-- /bodyContent -->
			</div>
		</div>
		<!-- /content -->
		<!-- footer -->
		<div id="cpp-footer-base" class="noprint">
			<div id="footer" role="contentinfo"<?php $this->html( 'userlangattributes' ) ?>>
				<?php $this->renderBottomNavigation();?>
				<?php $this->renderToolbox(); ?>
				<?php $this->renderFooter(); ?>
			</div>
		</div>
		<!-- /footer -->
		<?php $this->printTrail(); ?>

	</body>
</html>
<?php
	}

	private function renderToolbox()
	{
		$name = 'tb';

		$content = $this->getToolbox();

		$msg = 'toolbox';
		$msg_obj = wfMessage( $msg );
		$message = htmlspecialchars($msg_obj->exists() ? $msg_obj->text() : $msg);

		?>
		<div id="cpp-toolbox">
			<h5><span><?php echo $message; ?></span><a href="#"></a></h5>
			<ul>
<?php	   foreach( $content as $key => $val ):
				echo $this->makeListItem( $key, $val );
			endforeach;
			wfRunHooks( 'SkinTemplateToolboxEnd', array( &$this, true ));
			?>
			</ul>
		</div>
<?php
	}

	private function renderBottomNavigation()
	{
		$content = $this->data['sidebar']['navigation'];

		$msg = 'navigation';
		$msg_obj = wfMessage( $msg );
		$message = htmlspecialchars($msg_obj->exists() ? $msg_obj->text() : $msg);

		?>
		<div id="cpp-navigation">
			<h5><?php echo $message; ?></h5>
			<ul>
<?php	   foreach( $content as $key => $val ):
				echo $this->makeListItem( $key, $val );
			endforeach; ?>
			</ul>
		</div>
<?php
	}

	private function renderLanguages()
	{
		$content = $this->data['language_urls'];

		$msg = 'otherlanguages';
		$msg_obj = wfMessage( $msg );
		$message = htmlspecialchars($msg_obj->exists() ? $msg_obj->text() : $msg);

		?>
		<div id="cpp-languages">
			<div><ul><li><?php echo $message; ?></li></ul></div>
			<div><ul>
<?php	   foreach( $content as $key => $val ):
				echo $this->makeListItem( $key, $val );
			endforeach; ?>
			</ul></div>
		</div>
<?php
	}

	private function renderFooter()
	{
		if ( $this->data['language_urls'] ) { $this->renderLanguages(); }
		foreach( $this->getFooterLinks() as $category => $links ): ?>
			<ul id="footer-<?php echo $category ?>">
				<?php foreach( $links as $link ): ?>
					<li id="footer-<?php echo $category ?>-<?php echo $link ?>"><?php $this->html( $link ) ?></li>
				<?php endforeach; ?>
			</ul>
		<?php endforeach; ?>
		<?php $footericons = $this->getFooterIcons("icononly");
				if ( count( $footericons ) > 0 ): ?>
					<ul id="footer-icons" class="noprint">
			<?php   foreach ( $footericons as $blockName => $footerIcons ): ?>
						<li id="footer-<?php echo htmlspecialchars( $blockName ); ?>ico">
				<?php   foreach ( $footerIcons as $icon ): ?>
							<?php echo $this->getSkin()->makeFooterIcon( $icon ); ?>
				<?php   endforeach; ?>
						</li>
			<?php   endforeach; ?>
					</ul>
		<?php   endif; ?>
				<div style="clear:both">
			</div>
<?php
	}

	/**
	 * Render one or more navigations elements by name, automatically reveresed
	 * when UI is in RTL mode
	 *
	 * @param $elements array
	 */
	protected function renderNavigation( $elements ) {
		global $wgVectorUseSimpleSearch;

		// If only one element was given, wrap it in an array, allowing more
		// flexible arguments
		if ( !is_array( $elements ) ) {
			$elements = array( $elements );
		// If there's a series of elements, reverse them when in RTL mode
		} elseif ( $this->data['rtl'] ) {
			$elements = array_reverse( $elements );
		}
		// Render elements
		foreach ( $elements as $name => $element ) {
			echo "\n<!-- {$name} -->\n";
			switch ( $element ) {
				case 'NAMESPACES':
?>
<div id="p-namespaces" role="navigation" class="vectorTabs<?php if ( count( $this->data['namespace_urls'] ) == 0 ) echo ' emptyPortlet'; ?>">
	<h3><?php $this->msg( 'namespaces' ) ?></h3>
	<ul<?php $this->html( 'userlangattributes' ) ?>>
		<?php foreach ( $this->data['namespace_urls'] as $link ): ?>
			<li <?php echo $link['attributes'] ?>><span><a href="<?php echo htmlspecialchars( $link['href'] ) ?>" <?php echo $link['key'] ?>><?php echo htmlspecialchars( $link['text'] ) ?></a></span></li>
		<?php endforeach; ?>
	</ul>
</div>
<?php
				break;
				case 'VARIANTS':
?>
<div id="p-variants" role="navigation" class="vectorMenu<?php if ( count( $this->data['variant_urls'] ) == 0 ) echo ' emptyPortlet'; ?>">
	<h3 id="mw-vector-current-variant">
	<?php foreach ( $this->data['variant_urls'] as $link ): ?>
		<?php if ( stripos( $link['attributes'], 'selected' ) !== false ): ?>
			<?php echo htmlspecialchars( $link['text'] ) ?>
		<?php endif; ?>
	<?php endforeach; ?>
	</h3>
	<h3><span><?php $this->msg( 'variants' ) ?></span><a href="#"></a></h3>
	<div class="menu">
		<ul>
			<?php foreach ( $this->data['variant_urls'] as $link ): ?>
				<li<?php echo $link['attributes'] ?>><a href="<?php echo htmlspecialchars( $link['href'] ) ?>" lang="<?php echo htmlspecialchars( $link['lang'] ) ?>" hreflang="<?php echo htmlspecialchars( $link['hreflang'] ) ?>" <?php echo $link['key'] ?>><?php echo htmlspecialchars( $link['text'] ) ?></a></li>
			<?php endforeach; ?>
		</ul>
	</div>
</div>
<?php
				break;
				case 'VIEWS':
?>
<div id="p-views" role="navigation" class="vectorTabs<?php if ( count( $this->data['view_urls'] ) == 0 ) { echo ' emptyPortlet'; } ?>">
	<h3><?php $this->msg('views') ?></h3>
	<ul<?php $this->html('userlangattributes') ?>>
		<?php foreach ( $this->data['view_urls'] as $link ): ?>
			<li<?php echo $link['attributes'] ?>><span><a href="<?php echo htmlspecialchars( $link['href'] ) ?>" <?php echo $link['key'] ?>><?php
				// $link['text'] can be undefined - bug 27764
				if ( array_key_exists( 'text', $link ) ) {
					echo array_key_exists( 'img', $link ) ?  '<img src="' . $link['img'] . '" alt="' . $link['text'] . '" />' : htmlspecialchars( $link['text'] );
				}
				?></a></span></li>
		<?php endforeach; ?>
	</ul>
</div>
<?php
				break;
				case 'ACTIONS':
?>
<div id="p-cactions" role="navigation" class="vectorMenu<?php if ( count( $this->data['action_urls'] ) == 0 ) echo ' emptyPortlet'; ?>">
	<h3><span><?php $this->msg( 'actions' ) ?></span><a href="#"></a></h3>
	<div class="menu">
		<ul<?php $this->html( 'userlangattributes' ) ?>>
			<?php foreach ( $this->data['action_urls'] as $link ): ?>
				<li<?php echo $link['attributes'] ?>><a href="<?php echo htmlspecialchars( $link['href'] ) ?>" <?php echo $link['key'] ?>><?php echo htmlspecialchars( $link['text'] ) ?></a></li>
			<?php endforeach; ?>
		</ul>
	</div>
</div>
<?php
				break;
				case 'PERSONAL':
?>
<div id="p-personal" role="navigation" class="<?php if ( count( $this->data['personal_urls'] ) == 0 ) echo ' emptyPortlet'; ?>">
<?php
		$personalTools = $this->getPersonalTools();
		$item = reset($personalTools);
		$key = key($personalTools);
		array_shift($personalTools);

		echo $this->makeListItem( $key, $item, array( 'tag' => 'span' ) );
		if ( count( $personalTools ) > 0 ) {
?>
	<div class="menu">
		<ul<?php $this->html( 'userlangattributes' ) ?>>
<?php			   foreach( $personalTools as $key => $item ) {
						echo $this->makeListItem( $key, $item );
					} ?>
		</ul>
	</div>
<?php   } ?>
</div>
<?php
				break;
				case 'SEARCH':
?>
<div id="p-search" role="search">
	<h3<?php $this->html( 'userlangattributes' ) ?>><label for="searchInput"><?php $this->msg( 'search' ) ?></label></h3>
	<form action="<?php $this->text( 'wgScript' ) ?>" id="searchform">
		<?php if ( true ): ?>
		<div id="simpleSearch">
			<?php if ( $this->data['rtl'] ): ?>
			<?php echo $this->makeSearchButton( 'image', array( 'id' => 'searchButton', 'src' => $this->getSkin()->getSkinStylePath( 'images/search-rtl.png' ), 'width' => '12', 'height' => '13' ) ); ?>
			<?php endif; ?>
			<?php echo $this->makeSearchInput( array( 'id' => 'searchInput', 'type' => 'text' ) ); ?>
			<?php if ( !$this->data['rtl'] ): ?>
			<?php echo $this->makeSearchButton( 'image', array( 'id' => 'searchButton', 'src' => $this->getSkin()->getSkinStylePath( 'images/search-ltr.png' ), 'width' => '12', 'height' => '13' ) ); ?>
			<?php endif; ?>
		</div>
		<?php else: ?>
		<div>
			<?php echo $this->makeSearchInput( array( 'id' => 'searchInput' ) ); ?>
			<?php echo $this->makeSearchButton( 'go', array( 'id' => 'searchGoButton', 'class' => 'searchButton' ) ); ?>
			<?php echo $this->makeSearchButton( 'fulltext', array( 'id' => 'mw-searchButton', 'class' => 'searchButton' ) ); ?>
			<input type='hidden' name="title" value="<?php $this->text( 'searchtitle' ) ?>"/>
		</div>
		<?php endif; ?>
	</form>
</div>
<?php

				break;
			}
			echo "\n<!-- /{$name} -->\n";
		}
	}
}
