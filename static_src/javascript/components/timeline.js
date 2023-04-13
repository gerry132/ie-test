import Glide from '@glidejs/glide';


class Timeline {
    static selector() {
        return '[data-timeline]';
    }

    constructor(node) {
        this.node = node;
        this.slideTotal = 0;
        this.lastPosition = "top_pull";
        this.initialBuild = false;
        this.slideObj = {};
        this.type = "carousel";

        this.carousel = new Glide(node, {
            type: this.type,
            gap: 60,
            perView: 2,
            peek: {
                before: 90,
                after: 0
            },
            breakpoints: {
                1440: {
                gap: 45,
                },
                1024: {
                  perView: 2,
                  gap: 25,
                },
                800: {
                  gap: 20,
                  peek: 100,
                  perView: 1,
                  focusAt: 'center',
                },
                480: {
                  perView: 1,
                  gap: 10,
                  peek: 30,
                }
            },
        });
        if (!this.initialBuild) {
            this.lastPosition = "top_pull";
            this.initClassDisplay();
            this.initialBuild = true;
        } 
        this.carousel.mount();
        this.bindEvents();
    }

    bindEvents() {
        this.carousel.on('move.after', () => {
            this.updateAriaRoles();
        });
    }
    updateSpecific(slide, style) {
        slide.style.cssText += style;
        slide.setAttribute("position", this.lastPosition);
        slide.classList.add(this.lastPosition); 
    }
    updateClassDisplay(slide) {
        let style = null;
        if (this.lastPosition === "top_pull") {
            this.lastPosition = "bottom_pull";
            style = "padding-bottom: 2%;";
        } else {
            this.lastPosition = "top_pull"
            style = "padding-top: 2%;";
        }
        this.updateSpecific(slide, style); 
    }

    initClassDisplay() {
        this.node
        .querySelectorAll('.glide__slide')
        .forEach((slide) => {
            slide.setAttribute('slide-no', this.slideTotal);
            this.slideObj[this.slideTotal] = slide;
            this.updateClassDisplay(slide);
            this.slideTotal++;
        });
    }
    // sets aria-hidden on inactive slides
    updateAriaRoles() {
        this.node
            .querySelectorAll('.glide__slide:not(.glide__slide--active)')
            .forEach((slide) => {
                slide.setAttribute('aria-hidden', 'true');
                // ensure slide is not focusable when hidden
                slide.setAttribute('tabindex', '-1');
                // ensure all links within slide are not focusable when hidden
                // this.updateClassDisplay(slide);

                slide.classList.add(this.lastPosition);

                slide.querySelectorAll('a').forEach((slideLink) => {
                    slideLink.setAttribute('tabindex', '-1');
                });
            });
        const activeSlide = this.node.querySelector('.glide__slide--active');
        activeSlide.removeAttribute('aria-hidden');
        // re-enable focus on slide & all slide links while active
        activeSlide.setAttribute('tabindex', '');
        activeSlide.querySelectorAll('a').forEach((activeSlideLink) => {
            activeSlideLink.setAttribute('tabindex', '');
        });
    }
}

export default Timeline;