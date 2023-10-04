// Expected markup - see primarynav.html
/* <ul class="primary-nav" data-primary-nav="">
    <li class="primary-nav__item primary-nav__item--is-parent" data-has-subnav="">
        <a class="primary-nav__link" data-open-subnav="" href="/" aria-haspopup="true" aria-expanded="false">
            Home
            <span class="primary-nav__icon">›</span>
        </a>
        <ul class="sub-nav" data-subnav="">
            <li class="sub-nav__item sub-nav__item--back"><a data-subnav-back="" href="#">‹ Back</a></li>
            <li class="sub-nav__item">
                <a class="sub-nav__link" href="/">About us overview</a>
            </li>
            <li class="sub-nav__item sub-nav__item--secondary">
                <a class="sub-nav__link" href="/page-1/">page 1</a>
            </li>
        </ul>
    </li>
</ul> */

class MobileSubMenu {
    static selector() {
        return '[data-mobile-menu] [data-open-subnav]';
    }

    constructor(node) {
        this.node = node;
        this.subnav = this.node.nextElementSibling;
        this.backLink = this.subnav.querySelector('[data-subnav-back]');
        this.sub_links = this.subnav.querySelectorAll('[data-sub-links]');
        this.sub_links_question = this.subnav.querySelectorAll('[data-sub-links-question]');
        this.sub_links_answer = this.subnav.querySelectorAll('[data-sub-links-answer]');
        this.sub_links_open = this.subnav.querySelectorAll('.mega_menu_sub_links.is-open');
        this.currentlyOpenSubLinks = null;
        this.bindEventListeners();
    }

    bindEventListeners() {
        // Open submenu
        if (window.innerWidth < 1024){

            // Click back button to close it
            this.backLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
                this.subnav.classList.remove('is-visible');
                this.node.setAttribute('aria-expanded', 'false');
                this.closeOpenSubLinks();
            });

            this.node.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
            });
        }
        this.sub_links_question.forEach((question, index) => {
                question.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleSubLink(question, index);
                });
            });

    }

    open() {
        if (this.subnav.classList.contains('is-visible')) {
            // If submenu is currently visible, close it
            this.subnav.classList.remove('is-visible');
            this.node.setAttribute('aria-expanded', 'false');
        } else {
            this.subnav.classList.add('is-visible');
            this.node.setAttribute('aria-expanded', 'true');
            var header_primary = document.querySelector('.header__menu--primary').offsetHeight;
            if (document.querySelector('.header__menu--extended')) {
                var header_extended = document.querySelector('.header__menu--extended').offsetHeight;
                }
            var sub_nav_header = this.subnav.offsetHeight;
            var height_4 = header_primary+header_extended+sub_nav_header;
            if (header_extended) {
                this.subnav.style.height = height_4+'px';

            }else{
               this.subnav.style.height = sub_nav_header+header_primary+'px';
            }
        }

    }
    toggleSubLink(question, index) {
        if (this.currentlyOpenSubLinks !== this.sub_links[index]) {
            this.closeOpenSubLinks();
        }

        this.sub_links[index].classList.toggle('is-open');

        const isOpen = this.sub_links[index].classList.contains('is-open');
        question.setAttribute('aria-expanded', isOpen ? 'true' : 'false');

        this.sub_links_answer[index].setAttribute('aria-hidden', isOpen ? 'false' : 'true');

        this.currentlyOpenSubLinks = isOpen ? this.sub_links[index] : null;

    }


    closeOpenSubLinks() {
        if (this.currentlyOpenSubLinks) {
            this.currentlyOpenSubLinks.classList.remove("is-open");
        }
    }
}

export default MobileSubMenu;
