class VideoAutoplay {
    static selector() {
        return '[data-video-autoplay]';
    }

    constructor(node) {
        this.videoautoplay = node;
        this.str = this.videoautoplay.querySelectorAll('.starter');
       this.starter_button = this.videoautoplay.querySelectorAll('.starter_button');
       this.vimeo_player = this.videoautoplay.querySelectorAll('.vimeo_player');
       this.youtube_player = this.videoautoplay.querySelectorAll('.youtube_player');
        this.bindEvents();
    }

    bindEvents() {
        var c;
        for ( c = 0; c < this.str.length; c ++ ) {
                if(this.starter_button){
                   if(this.youtube_player){
                        this.starter_button[c].addEventListener('click', (e) => {
                            e.preventDefault();
                            this.youtube_player.forEach(e =>
                                e.src = e.src+'&autoplay=1'
                            );
                            this.starter_button.forEach(e => e.classList.add("hide"));
                            this.str.forEach(e => e.classList.add("hide"));
                        }, false);
                   }
                   if(this.vimeo_player){
                            this.starter_button[c].addEventListener('click', (e) => {
                            e.preventDefault();
                            this.vimeo_player.forEach(e =>
                                e.src = e.src+'?autoplay=1'
                            );
                            this.starter_button.forEach(e => e.classList.add("hide"));
                            this.str.forEach(e => e.classList.add("hide"));
                        }, false);
                   }
                }
        }
    }
}

export default VideoAutoplay;
