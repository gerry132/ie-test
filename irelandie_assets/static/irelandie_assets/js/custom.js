document.body.innerHTML += `<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<div id="alert-wrapper" style="display: none;">
        <h2>Logout in:</h2>
        <div id="countdown"></div>
        <h2>Press Ok to remain logged in</h2>
        <input type="button" value="OK" id="btn" onclick="setNewExpiryCookie()">
    </div>`


function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function setNewExpiryCookie() {
    let date = new Date()
    clearInterval(timer);
    date.setTime(date.getTime() + 1 * 60 * 60 * 1000);
    document.cookie = "logout_at=" + date.toISOString() + ";secure;path=/";
    timer = setInterval(showRemaining, 1000);
    document.getElementById('alert-wrapper').style.display = 'none';
}

function checkLogoutExpiry() {
    logout_at = getCookie('logout_at');
    l_time = new Date(logout_at);
    return l_time < Date.now();
}

function logout() {
    $.ajax({
        url: '/admin/logout/',
        method: "GET",
        data : "logout",
        success: function () {
          document.cookie = "logout_at=invali;path=/";
          window.location.replace("/admin");
          return true
        },
        error: function() {
          return false
        }
      });
}

$("#alert-wrapper").css({ 'zoom': 0.8, 'opacity':0 }).animate({ 'zoom': 1, 'opacity':1 },100)

let start_date = getCookie('logout_at');
let logged_in = getCookie('user_logged_in');

function returnUtcObj(date) {
    let now_utc = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(),
    date.getUTCDate(), date.getUTCHours(),
    date.getUTCMinutes(), date.getUTCSeconds());
    return now_utc;
}

function showRemaining() {
    let start_date = getCookie('logout_at');

    let end = new Date(start_date);
    let _second = 1000;
    let _minute = _second * 60;
    let _hour = _minute * 60;
    let _day = _hour * 24;
    let timer;
    let date = new Date();
    let now_utc = returnUtcObj(date);
    let end_utc = returnUtcObj(end);
    let new_d = new Date(now_utc);
    let new_e = new Date(end_utc)

    let distance = new_e - new_d;

    if (distance/1000 < 60) {
        document.getElementById('alert-wrapper').style.display = 'block';
    }

    if (distance < 0) {
        clearInterval(timer);
        if (logged_in) {
            logout();
        }
        return;
    }
    let seconds = Math.floor((distance % _minute) / _second);
    document.getElementById('countdown').innerHTML = seconds + 'secs';
}

if (start_date != 'invalid') {   
    showRemaining(); // adding this so as to immediately show the time after alert is loaded
    timer = setInterval(showRemaining, 1000);  
}
document.addEventListener("DOMContentLoaded", function () {
    const videoSections = document.querySelectorAll(".jarallax__video");

    if (videoSections.length === 0) {
        return; // Exit if no videos exist on the page
    }

    jarallax(document.querySelectorAll(".jarallax"), {
        videoPlayOnlyVisible: false
    });

    videoSections.forEach(section => {
        const videoElement = section.querySelector("video");
        const playButton = section.querySelector(".playButton");
        const pauseButton = section.querySelector(".pauseButton");
        const toggleButton = section.querySelector(".parallax__video-toggle-double");

        if (!videoElement || !toggleButton || !playButton || !pauseButton) {
            console.error("Missing video elements in section:", section);
            return;
        }

        videoElement.pause();
        videoElement.muted = true; // Start muted
        pauseButton.style.display = "none"; // Hide pause button initially

        toggleButton.addEventListener("click", function () {
            if (videoElement.paused) {
                videoElement.muted = false;
                videoElement.play();
                playButton.style.display = "none";
                pauseButton.style.display = "inline";
            } else {
                videoElement.pause();
                playButton.style.display = "inline";
                pauseButton.style.display = "none";
            }
        });
    });
});
