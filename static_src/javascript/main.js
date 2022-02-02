import '@babel/polyfill';
import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';
import DesktopSubMenu from './components/desktop-sub-menu';
import DesktopCloseMenus from './components/desktop-close-menus';
import SkipLink from './components/skip-link';
import StoryLinksExpander from './components/story-links-expander';
import VideoToggle from './components/video-toggle';

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
/* feature:use_frontend_component_tabs */
import Tabs from './components/tabs';
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
}

// Close the mobile menu callback.
function closeMobileMenu() {
    document.querySelector('body').classList.remove('no-scroll');
    document.querySelector('[data-mobile-menu]').classList.remove('is-visible');
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

    for (const desktopsubmenu of document.querySelectorAll(
        DesktopSubMenu.selector(),
    )) {
        new DesktopSubMenu(desktopsubmenu);
    }

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

    /* feature:use_frontend_component_tabs */
    for (const tabs of document.querySelectorAll(Tabs.selector())) {
        new Tabs(tabs);
    }
    /* endfeature */

    for (const skiplink of document.querySelectorAll(SkipLink.selector())) {
        new SkipLink(skiplink);
    }

    for (const storylinksexpander of document.querySelectorAll(
        StoryLinksExpander.selector(),
    )) {
        new StoryLinksExpander(storylinksexpander);
    }

    for (const videotoggle of document.querySelectorAll(
        VideoToggle.selector(),
    )) {
        new VideoToggle(videotoggle);
    }
});
