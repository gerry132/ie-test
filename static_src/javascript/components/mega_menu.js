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
        this.mega_menu_nav = this.accordion.querySelectorAll(".mega_menu_nav");
        this.rich_text_Height = this.accordion.querySelectorAll(".rich_text_mega_menu");
        this.rich_text_image_Height = this.accordion.querySelectorAll('.image_withlinks');
        this.image_Height = this.accordion.querySelectorAll('.image_container');
        this.image_caption = this.accordion.querySelector('.image-block__caption');
        this.tallest = 0;
        this.tallest_richtext = 0;
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
                    for(var i = 0; i < this.mega_menu_nav.length; i++)
                        {
                            var ele = this.mega_menu_nav[i];
                            var eleHeight = ele.offsetHeight;
                            this.tallest = (eleHeight>this.tallest ? eleHeight : this.tallest);
                        }
                    for(var i = 0; i < this.mega_menu_nav.length; i++)
                        {
                        this.mega_menu_nav[i].style.height = this.tallest + "px";
                        }
                    for(i = 0; i < this.rich_text_Height.length; i++)
                        {
                            var eleHeight = this.rich_text_Height[i].offsetHeight;
                            this.tallest_richtext = (eleHeight>this.tallest_richtext ? eleHeight : this.tallest_richtext);
                        }
                    for(i = 0; i < this.rich_text_Height.length; i++)
                        {
                            this.rich_text_Height[i].style.height = this.tallest_richtext + "px";
                        }
                    for(i = 0; i < this.rich_text_image_Height.length; i++)
                        {
                            this.rich_text_image_Height[i].style.height = this.tallest_richtext + "px";
                        }
                    if(this.image_caption){
                    for(i = 0; i < this.image_Height.length; i++)
                        {
                            this.image_Height[i].style.height = this.tallest+this.tallest_richtext-"52"+'px';
                        }
                    }else{
                    for(i = 0; i < this.image_Height.length; i++)
                        {
                            this.image_Height[i].style.height = 20+this.tallest+this.tallest_richtext+'px';
                        }
                    }
                }
        });
    }
}

export default MegaMenu;
