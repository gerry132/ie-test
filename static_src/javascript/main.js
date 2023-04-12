import '@babel/polyfill';
import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';
// DROPDOWN menus are disabled on desktop as it blocks the top level link.
// This may be required in the future.
// import DesktopSubMenu from './components/desktop-sub-menu';
import DesktopCloseMenus from './components/desktop-close-menus';
import SkipLink from './components/skip-link';
import Search from './components/search';
import VideoToggle from './components/video-toggle';
import MultimediaToggle from './components/multimedia-toggle';

/* feature:use_frontend_component_accordion */
import Accordion from './components/accordion';
/* endfeature */
/* feature:use_frontend_component_carousel */
import Carousel from './components/carousel';
/* endfeature */
/* feature:use_frontend_component_progress_bar */
import ProgressBar from './components/progress-bar';
/* endfeature */
/* feature:use_frontend_component_video_modal */
import VideoModal from './components/video-modal';
/* endfeature */

// IE11 polyfills
import foreachPolyfill from './polyfills/foreach-polyfill';
import closestPolyfill from './polyfills/closest-polyfill';

import '../sass/main.scss';

foreachPolyfill();
closestPolyfill();

// Open the mobile menu callback
function openMobileMenu() {
    document.querySelector('body').classList.add('no-scroll');
    document.querySelector('[data-mobile-menu]').classList.add('is-visible');
    document.querySelectorAll('[data-mobile-mega-menu]').forEach(function(menu) {
            menu.classList.add('is-hidden');
        });
    document.querySelectorAll('.sub-nav-hidden').forEach(function(menu) {
            menu.classList.add('is-visible');
        });
}

// Close the mobile menu callback.
function closeMobileMenu() {
    document.querySelector('body').classList.remove('no-scroll');
    document.querySelector('[data-mobile-menu]').classList.remove('is-visible');
    document.querySelectorAll('[data-mobile-mega-menu]').forEach(function(menus) {
            menus.classList.remove('is-hidden');
        });
    document.querySelectorAll('.sub-nav-hidden').forEach(function(menu) {
            menu.classList.remove('is-visible');
        });
}
/* image-credit */
let iicons = document.querySelectorAll('.story__button-image-credit');
let imagecredits = document.querySelectorAll('.story__image-credit');

for (let i = 0; i < iicons.length; i++) {
    iicons[i].addEventListener('click', function() {
        imagecredits[i].classList.toggle('visible');
    });
}
document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-restricted-syntax, no-new */

    /* feature:use_frontend_component_accordion */
    for (const accordion of document.querySelectorAll(Accordion.selector())) {
        new Accordion(accordion);
    }
    /* endfeature */
    /* feature:use_frontend_component_carousel */
    for (const carousel of document.querySelectorAll(Carousel.selector())) {
        new Carousel(carousel);
    }
    /* endfeature */

    for (const mobilemenu of document.querySelectorAll(MobileMenu.selector())) {
        new MobileMenu(mobilemenu, openMobileMenu, closeMobileMenu);
    }

    for (const mobilesubmenu of document.querySelectorAll(
        MobileSubMenu.selector(),
    )) {
        new MobileSubMenu(mobilesubmenu);
    }

    // DROPDOWN menus are disabled on desktop as it blocks the top level link.
    // This may be required in the future.
    // for (const desktopsubmenu of document.querySelectorAll(
    //     DesktopSubMenu.selector(),
    // )) {
    //     new DesktopSubMenu(desktopsubmenu);
    // }

    new DesktopCloseMenus();

    /* feature:use_frontend_component_progress_bar */
    for (const progressbar of document.querySelectorAll(
        ProgressBar.selector(),
    )) {
        new ProgressBar(progressbar);
    }
    /* endfeature */

    /* feature:use_frontend_component_video_modal */
    for (const videomodal of document.querySelectorAll(VideoModal.selector())) {
        new VideoModal(videomodal);
    }
    /* endfeature */

    for (const skiplink of document.querySelectorAll(SkipLink.selector())) {
        new SkipLink(skiplink);
    }

    for (const search of document.querySelectorAll(Search.selector())) {
        new Search(search);
    }

    for (const videotoggle of document.querySelectorAll(
        VideoToggle.selector(),
    )) {
        new VideoToggle(videotoggle);
    }
    for (const multimediatoggle of document.querySelectorAll(
        MultimediaToggle.selector(),
    )) {
        new MultimediaToggle(multimediatoggle);
    }
});
