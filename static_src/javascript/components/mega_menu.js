class MegaMenu {
    static selector() {
        return '[data-mega-menu]';
    }

    constructor(node) {
        this.megamenu = node;
        this.question = this.megamenu.querySelector(
            '[data-mega-menu-question]',
        );
        this.answer = this.megamenu.querySelector('[data-mega-menu-answer]');
        this.mega_menu_nav = this.megamenu.querySelectorAll(".mega_menu_nav");
        this.rich_text_Height = this.megamenu.querySelectorAll(".rich_text_mega_menu");
        this.rich_text_image_Height = this.megamenu.querySelectorAll('.image_withlinks');
        this.image_Height = this.megamenu.querySelectorAll('.image_container');
        this.image_caption = this.megamenu.querySelector('.image-block__caption');
        this.sub_links = this.megamenu.querySelectorAll('[data-sub-links]');
        this.sub_links_question = this.megamenu.querySelectorAll('[data-sub-links-question]');
        this.sub_links_answer = this.megamenu.querySelectorAll('[data-sub-links-answer]');
        this.sub_links_open = this.megamenu.querySelectorAll('.mega_menu_sub_links.is-open');


        this.tallest = 0;
        this.tallest_richtext = 0;
        this.tallest_sub_links = 0;
        this.currentlyOpenSubLinks = null;

        this.bindEvents();
    }


    bindEvents() {
        document.addEventListener("click", function(event) {
            const primary_nav_mega_menu = document.querySelectorAll(".primary-nav__link.mega_menu");
            const custom_nav_mega_menu = document.querySelectorAll(".custom-nav__link.mega_menu");
            var dropdowns = null;

            if(custom_nav_mega_menu.length != 0){
                dropdowns = custom_nav_mega_menu;
            }else{
                dropdowns = primary_nav_mega_menu;
            }

            // Check if the click event's target is inside any of the dropdowns
            let clickedInsideDropdown = false;

            dropdowns.forEach(function(dropdown) {
                if (dropdown.contains(event.target)) {
                    clickedInsideDropdown = true;
                }
            });

            // Close all dropdowns if the click was outside of any dropdown
            if (!clickedInsideDropdown) {
                dropdowns.forEach(function(dropdown) {
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
                });
            }
        });

        this.question.addEventListener('click', (e) => {
        let imageHeight = document.querySelector('.header-large .header__logo-wrapper');
        if(imageHeight && imageHeight.clientHeight < 75 ){
            this.answer.style.marginTop = 30 + "px";
        }
            let open = !this.megamenu.classList.contains('is-open');
            e.preventDefault();
                this.close_all_dropdowns();
                if(open){
                this.megamenu.classList.add('is-open');
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

        this.sub_links_question.forEach((question, index) => {
            question.addEventListener('click', (e) => {
                e.preventDefault();

                if (this.currentlyOpenSubLinks !== this.sub_links[index]) {
                    this.closeOpenSubLinks();
                }

                // Toggle the "is-open" class on the corresponding .sub_links element
                this.sub_links[index].classList.toggle('is-open');

                // Update ARIA attributes based on the open state
                const isOpen = this.sub_links[index].classList.contains('is-open');
                question.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                this.sub_links_answer[index].setAttribute('aria-hidden', isOpen ? 'false' : 'true');

                 this.currentlyOpenSubLinks = isOpen ? this.sub_links[index] : null;

                 this.updateContainerHeight(this.sub_links_answer[index].offsetHeight, this.tallest);
            });
        });

    }

    closeOpenSubLinks() {
        if (this.currentlyOpenSubLinks) {
            this.currentlyOpenSubLinks.classList.remove("is-open");
        }
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
        this.closeOpenSubLinks();
    }


    updateContainerHeight(answer_opened, tallest_reset) {

        if (answer_opened != 0) {
            this.new_Height = answer_opened + tallest_reset;

            for (let i = 0; i < this.mega_menu_nav.length; i++) {
                this.mega_menu_nav[i].style.height = this.new_Height + "px";
            }
        } else {
            for (let i = 0; i < this.mega_menu_nav.length; i++) {
                this.mega_menu_nav[i].style.height = tallest_reset + "px";
            }
        }
    }

}

export default MegaMenu;
