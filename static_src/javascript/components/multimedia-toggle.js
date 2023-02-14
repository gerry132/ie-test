class MultimediaToggle {
    static selector() {
        return '[data-multimedia-container]';
    }

    constructor(node) {
        this.multimeidaContainer = node;
        this.videoplay = this.multimeidaContainer.querySelector('[data-multimedia]');
        this.MultimediaToggle = this.multimeidaContainer.querySelector(
            '[data-multimedia-toggle]',
        );
        this.bindEvents();
    }

    playPause() {
        this.MultimediaToggle.classList.add('active');

        if (this.videoplay.paused) {
            this.videoplay.play();
            this.MultimediaToggle.classList.add('active');
        } else {
            this.videoplay.pause();
            this.MultimediaToggle.classList.remove('active');
        }
    }

    bindEvents() {
        this.MultimediaToggle.addEventListener('click', () => {
            this.playPause();
        });
    }
}

export default MultimediaToggle;
