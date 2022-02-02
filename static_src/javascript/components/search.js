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

        // mobile menu selectors
        this.mobileMenu = document.querySelector('[data-mobile-menu]');
        this.mobileMenuToggle = document.querySelector(
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
            this.hideMobileMenu();
            this.hideDesktopMenu();
            this.toggleSearch();
        });
    }

    // hide the mobile menu
    hideMobileMenu() {
        this.mobileMenu.classList.remove(this.activeClass);
        this.mobileMenuToggle.classList.remove(this.activeClass);
    }

    hideDesktopMenu() {
        this.allDesktopMenuItems.forEach((item) =>
            item.classList.remove(this.activeClass),
        );
    }

    toggleSearch() {
        // toggle both desktop and mobile icons
        this.searchToggles.forEach((toggle) => {
            toggle.classList.toggle(this.activeClass);
        });

        // toggle search dropdown
        this.searchDropdown.classList.toggle(this.activeClass);

        // focus the input
        this.searchInput.focus();
    }
}

export default Search;
