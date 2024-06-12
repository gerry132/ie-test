class VideoToggleParallax {
    static selector() {
        return '[data-video-parallax-container]';
    }

    constructor(node) {
        this.videoContainer = node;
        this.video = this.videoContainer.querySelector('[data-video-parallax]');
        this.videoToggle = this.videoContainer.querySelector(
            '[data-video-parallax-toggle]',
        );
        this.bindEvents();
    }

    playPause() {

        if (this.video.paused) {
            this.video.play();
            this.videoToggle.classList.add('active');
        } else {
            this.video.pause();
            this.videoToggle.classList.remove('active');
        }
    }

    bindEvents() {
        this.videoToggle.addEventListener('click', () => {
            this.playPause();
        });
    }
}

export default VideoToggleParallax;
