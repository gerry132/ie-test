class MobileMenu {
    static selector() {
        return '[data-mobile-menu-toggle]';
    }

    constructor(node, openCb = () => {}, closeCb = () => {}) {
        this.node = node;

        // search selectors
        this.searchToggles = document.querySelectorAll('[data-toggle-search]');
        this.searchDropdown = document.querySelector('[data-search-dropdown]');
        this.noticeBars = document.querySelector('.notice-bar');
        this.breadcrumb = document.querySelector('.breadcrumb');

        // Any callbacks to be called on open or close.
        this.openCb = openCb;
        this.closeCb = closeCb;

        this.state = {
            open: false,
        };

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            this.toggle();
        });

        // Listen for when the search opens and close any open desktop menu dropdowns
        document.addEventListener('onSearchOpen', () => {
            this.node.classList.remove('is-open');
            this.breadcrumb.classList.remove('breadcrumbs__hidden');
            this.noticeBars.classList.remove('notice-bar__hidden');
            this.closeCb();

            this.state.open = false;
        });
    }

    toggle() {
        if (this.state.open) {
            this.close();
        } else {
            this.open();
//            this.closeSearch();
        }
    }

    open() {
        // Fire a custom event so that any open search items can be closed
        const menuOpenEvent = new Event('onMenuOpen');
        document.dispatchEvent(menuOpenEvent);

        this.node.classList.add('is-open');
        this.node.setAttribute('aria-expanded', 'true');
        this.noticeBars.classList.add('notice-bar__hidden');
        this.breadcrumb.classList.add('breadcrumbs__hidden');
        this.openCb();

        this.state.open = true;
    }

    close() {
        this.node.classList.remove('is-open');
        this.node.setAttribute('aria-expanded', 'false');
        this.noticeBars.classList.remove('notice-bar__hidden');
        this.breadcrumb.classList.remove('breadcrumbs__hidden');
        this.closeCb();

        this.state.open = false;
    }
}

export default MobileMenu;
