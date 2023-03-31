import Glide from '@glidejs/glide';

class Carousel {
    static selector() {
        return '[data-carousel]';
    }

    constructor(node) {
        this.node = node;
        this.slideTotal = this.node.dataset.slidetotal;

        this.carousel = new Glide(node, {
            type: 'carousel',
            startAt: 0,
            perView: 2,
            peek: 100,
            hoverpause: true, // keep this for accessibility if using autoplay
            breakpoints: {
                800: {
                  perView: 1,
                  focusAt: 'center',
                },
                480: {
                  perView: 1,
                  peek: 0,
                }
            },
        });

        this.carousel.mount();
        this.bindEvents();
        this.setLiveRegion();
    }

    bindEvents() {
        this.carousel.on('move.after', () => {
            this.updateAriaRoles();
            this.updateLiveRegion();
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

export default Carousel;
