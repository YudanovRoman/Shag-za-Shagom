function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
  }

function toggleMenu() {
    let navbar = document.getElementById("myNavbar");
    navbar.classList.toggle("responsive");
}

const delay = 150;
const currentTheme = getCookie('theme');
if (currentTheme === 'dark') {
    document.body.className = 'dark-theme';
    document.getElementById("imgClickAndChange").src = "/static/img/moon_button.png";
    document.getElementById('theme-toggle').classList.replace("light", "dark");
    if (document.getElementById('img_border')) {
        document.getElementById('img_border').classList.add('border-light');
    }
} else {
    document.body.className = 'light-theme';
    document.getElementById("imgClickAndChange").src = "/static/img/sun_button.png";
    document.getElementById('theme-toggle').classList.replace("dark", "light");
    if (document.getElementById('img_border')) {
        document.getElementById('img_border').classList.add('border-secondary');
    }
}

document.getElementById('theme-toggle').addEventListener('click', function() {
    const currentTheme = document.body.className;
    if (currentTheme === 'light-theme') {
        document.cookie = "theme=dark; path=/";
        document.body.className = 'dark-theme';
        document.getElementById("imgClickAndChange").src = "/static/img/moon_button.png";
        document.getElementById('theme-toggle').classList.replace("light", "dark");
        if (document.getElementById('img_border')) {
            document.getElementById('img_border').classList.replace('border-secondary', 'border-light');
        }
    } else {
        document.cookie = "theme=light; path=/";
        document.body.className = 'light-theme';
        document.getElementById("imgClickAndChange").src = "/static/img/sun_button.png";
        document.getElementById('theme-toggle').classList.replace("dark", "light");
        if (document.getElementById('img_border')) {
            document.getElementById('img_border').classList.replace('border-light', 'border-secondary');
        }
    }
});
