class MobileMenu {
    static selector() {
        return '[data-mobile-menu-toggle]';
    }

    constructor(node, openCb = () => {}, closeCb = () => {}) {
        this.node = node;

        // search selectors
        this.searchToggles = document.querySelectorAll('[data-toggle-search]');
        this.searchDropdown = document.querySelector('[data-search-dropdown]');

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
    }

    toggle() {
        if (this.state.open) {
            this.close();
        } else {
            this.open();
            this.closeSearch();
        }
    }

    open() {
        this.node.classList.add('is-open');
        this.openCb();

        this.state.open = true;
    }

    close() {
        this.node.classList.remove('is-open');
        this.closeCb();

        this.state.open = false;
    }

    closeSearch() {
        this.searchToggles.forEach((searchToggle) =>
            searchToggle.classList.remove('is-active'),
        );
        this.searchDropdown.classList.remove('is-active');
    }
}

export default MobileMenu;
