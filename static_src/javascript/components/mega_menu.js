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
        window.addEventListener('click', (event) =>  {
            if (event.target != this.accordion) {
              this.close_all_dropdowns();
            }
          });
        this.bindEvents();
    }
    close_all_dropdowns(){
        var questions = document.querySelectorAll(
            '[data-mega-menu-question]',
        );
        var openMenus = document.querySelectorAll('.mega_menu.is-open');
        openMenus.forEach(openMenu => {
          openMenu.classList.remove('is-open');
        });

        var answers = document.querySelectorAll('[data-mega-menu-answer]');
        questions.forEach(question => {
            question.setAttribute('aria-expanded', 'false');
        });
        answers.forEach(answer => {
          answer.setAttribute('aria-hidden', 'true');
        });
    }

    bindEvents() {
        this.question.addEventListener('click', (e) => {
        let imageHeight = document.querySelector('.header-large .header__logo-wrapper');
        if(imageHeight && imageHeight.clientHeight < 75 ){
            this.answer.style.marginTop = 30 + "px";
        }

            let open = !this.accordion.classList.contains('is-open');
            e.preventDefault();
                this.close_all_dropdowns();
                if(open){
                this.accordion.classList.add('is-open');
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
                e.stopPropagation();
        });
    }

}

export default MegaMenu;
