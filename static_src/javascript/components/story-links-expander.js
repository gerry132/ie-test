class StoryLinksExpander {
    static selector() {
        return '[data-story-links-expander]';
    }

    constructor(node) {
        this.expander = node;
        this.toggle = this.expander.querySelector('[data-story-links-toggle]');
        this.bindEvents();
    }

    bindEvents() {
        if (this.toggle) {
            this.toggle.addEventListener('click', (e) => {
                e.preventDefault();
                let open = this.expander.classList.contains('is-open');
                this.expander.classList.toggle('is-open');

                if (open) {
                    open = false;
                } else {
                    open = true;
                }
            });
        }
    }
}

export default StoryLinksExpander;
