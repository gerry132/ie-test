class Search {
    static selector() {
        return '[data-toggle-search]';
    }

    constructor(node) {
        this.node = node;

        // search selectors
        this.searchToggles = document.querySelectorAll('[data-toggle-search]');
        this.searchDropdown = document.querySelector('[data-search-dropdown]');
        this.searchInput = this.searchDropdown.querySelector(
            '[data-search-input]',
        );
        this.noticeBar = document.querySelector('.notice-bar--extended');
        this.breadCrumbs = document.querySelector('.breadcrumb');

        // mobile menu selectors
        this.mobileMenu = document.querySelectorAll('[data-mobile-menu]');
        this.mobileMenuToggle = document.querySelectorAll(
            '[data-mobile-menu-toggle]',
        );

        // desktop menu selectors
        this.allDesktopMenuItems = document.querySelectorAll(
            '[data-desktop-nav-item]',
        );

        // classes
        this.activeClass = 'is-active';

        this.bindEvents();
    }

    bindEvents() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleSearch();
        });

        // Hide the search dropdown if the mobile or desktop menus are opened
        document.addEventListener('onMenuOpen', () => {
            this.searchToggles.forEach((toggle) => {
                toggle.classList.remove(this.activeClass);
            });

            if (this.breadCrumbs !== null) {
                this.breadCrumbs.classList.remove('generic-hero__search-is-active');
            }

            // toggle search dropdown
            this.searchDropdown.classList.remove(this.activeClass);
            if (this.noticeBar !== null){
                this.noticeBar.classList.remove('notice-bar--extended__search-is-active');
            }
        });
    }

    toggleSearch() {
        const searchEvent = new Event('onSearchOpen');
        document.dispatchEvent(searchEvent);

        // toggle both desktop and mobile icons
        this.searchToggles.forEach((toggle) => {
            toggle.classList.toggle(this.activeClass);
        });

        // toggle search dropdown
        this.searchDropdown.classList.toggle(this.activeClass);

        if (this.breadCrumbs !== null) {
            this.breadCrumbs.classList.toggle('generic-hero__search-is-active');
        }

        // focus the input
        this.searchInput.focus();
        if (this.noticeBar !== null) {
            this.noticeBar.classList.toggle('notice-bar--extended__search-is-active');
        }
    }
}

export default Search;
