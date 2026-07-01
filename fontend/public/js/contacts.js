//menu
const menu = document.getElementById('menu');
    const  nav_links = document.getElementById('nav-links');
    menu.addEventListener('click', function() {
    nav_links.classList.toggle('nav-hidden')
    });

//add contact button
    const add_button =document.getElementById('add-button');
    const add_contact = document.getElementById('add-contact');
    add_button.addEventListener('click', function() {
    add_contact.classList.toggle('show-form')
    });


