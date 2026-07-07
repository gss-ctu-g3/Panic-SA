//menu
    const menu = document.getElementById('menu');
    const  nav_links = document.getElementById('nav-links');
    menu.addEventListener('click', function() {
    nav_links.classList.toggle('nav-hidden')
    });

 //Panic button alert
     const panic_button = document.getElementById('panic-button');
    panic_button.addEventListener('click', function() {
        alert('Help is on the way!')
    });