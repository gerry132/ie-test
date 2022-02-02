class VideoToggle {
    static selector() {
        return '[data-video-container]';
    }

    constructor(node) {
        this.videoContainer = node;
        this.video = this.videoContainer.querySelector('[data-video]');
        this.videoToggle = this.videoContainer.querySelector(
            '[data-video-toggle]',
        );
        this.bindEvents();
    }

    playPause() {
        this.videoToggle.classList.add('active');

        if (this.video.paused) {
            this.video.play();
            this.videoToggle.classList.remove('active');
        } else {
            this.video.pause();
            this.videoToggle.classList.add('active');
        }
    }

    bindEvents() {
        this.videoToggle.addEventListener('click', () => {
            this.playPause();
        });
    }
}

export default VideoToggle;
