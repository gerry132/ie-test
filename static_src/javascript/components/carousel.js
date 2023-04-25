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
            width: 500,
            startAt: 0,
            perView: 3,
            gap: 40,
            peek: {
                before: 300,
                after: 0,
              },
            hoverpause: true, // keep this for accessibility if using autoplay
            breakpoints: {
                1440: {
                  perView: 2,
                  peek: {
                        before: 250,
                        after: 0,
                      },
                },
                1024: {
                  perView: 2,
                  peek: {
                        before: 150,
                        after: 0,
                      },
                },
                800: {
                  gap: 20,
                  perView: 1,
                  peek: 100,
                  focusAt: 'center',
                },
                480: {
                  gap: 10,
                  perView: 1,
                  peek: 30,
                }
            },
        });

        this.carousel.mount();
        this.bindEvents();
    }

    bindEvents() {
        this.carousel.on('move.after', () => {
            this.updateAriaRoles();
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
