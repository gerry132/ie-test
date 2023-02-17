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
    document.cookie = "logout_at=" + date.toISOString() + ";path=/";
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
          console.log(1234)
          return false
        }
      });
}

$("#alert-wrapper").css({ 'zoom': 0.8, 'opacity':0 }).animate({ 'zoom': 1, 'opacity':1 },100)

let start_date = getCookie('logout_at');
let logged_in = getCookie('user_logged_in');

function showRemaining() {
    let start_date = getCookie('logout_at');

    let end = new Date(start_date);
    let _second = 1000;
    let _minute = _second * 60;
    let _hour = _minute * 60;
    let _day = _hour * 24;
    let timer;
    let now = new Date();
    let distance = end.getTime() - now.getTime();

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