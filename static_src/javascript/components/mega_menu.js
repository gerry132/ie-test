class MegaMenu {
    static selector() {
        return '[data-mega-menu]';
    }

    constructor(node) {
        this.accordion = node;
        this.question = this.accordion.querySelector(
            '[data-mega-menu-question]',
        );
        this.answer = this.accordion.querySelector('[data-mega-menu-answer]');
        this.bindEvents();
    }

    bindEvents() {
        this.question.addEventListener('click', (e) => {
            e.preventDefault();
            let open = this.accordion.classList.contains('is-open');
            this.accordion.classList.toggle('is-open');

            if (open) {
                this.question.setAttribute('aria-expanded', 'false');
                this.answer.setAttribute('aria-hidden', 'true');
                open = false;

            } else {
                this.question.setAttribute('aria-expanded', 'true');
                this.answer.setAttribute('aria-hidden', 'false');
                open = true;
                var rich_text_Height = document.querySelector('.rich-text_1').clientHeight;
                var rich_text_image_Height = document.querySelector('.image');
                rich_text_image_Height.style.height = rich_text_Height+'px';
                var elemHeight = document.getElementById('left_mega__menu');
                if(elemHeight){
                    elemHeight = elemHeight.clientHeight;
                    var image_Height = document.getElementById('image_container');
                    var image_caption = document.querySelector('.image-block__caption');
                    if(image_caption){
                        image_Height.style.height = elemHeight-"72"+'px';
                    }else{
                        image_Height.style.height = elemHeight+'px';
                    }
                }
            }
        });
    }
}

export default MegaMenu;
