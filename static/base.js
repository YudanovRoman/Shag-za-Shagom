function toggleMenu() {
    let navbar = document.getElementById("myNavbar");
    navbar.classList.toggle("responsive");
}
document.getElementById('theme-toggle').addEventListener('click', function() {
    const currentTheme = document.body.className;
    if (currentTheme === 'light-theme') {
        document.body.className = 'dark-theme';
        document.getElementById("imgClickAndChange").src = "static/img/moon_button.png";
        getElementById('theme-toggle').classList.replace("light", "dark");
    } else {
        document.body.className = 'light-theme';
        document.getElementById("imgClickAndChange").src = "static/img/sun_button.png";
        getElementById('theme-toggle').classList.replace("dark", "light");
    }
    console.log("Switching theme");
}); 
