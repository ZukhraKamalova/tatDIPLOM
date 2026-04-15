const header = document.querySelector('header');

// Функция для добавления/удаления класса 'scroll' при прокрутке страницы
function fixedNavbar() {
    header.classList.toggle('scroll', window.pageYOffset > 0);
}

fixedNavbar();

window.addEventListener('scroll', fixedNavbar);

let menu = document.querySelector('#menu-btn');
let userBtn = document.querySelector('#user-btn');

// Обработчик клика по кнопке меню
menu.addEventListener('click', function() {
    // Получаем навигационное меню
    let nav = document.querySelector('.navbar');
    nav.classList.toggle('active');
});

// Обработчик клика по кнопке пользователя
userBtn.addEventListener('click', function() {
    let userBox = document.querySelector('.user-box');
    userBox.classList.toggle('active');
});

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.slider-container').forEach(container => {
        const track = container.querySelector('.slider-track');
        const leftArrow = container.querySelector('.left-arrow');
        const rightArrow = container.querySelector('.right-arrow');

        if (!track || !leftArrow || !rightArrow) return;

        let scrollAmount = track.clientWidth;

        function scrollRight() {
            if (track.scrollLeft + scrollAmount >= track.scrollWidth) {
                track.scrollTo({ left: 0, behavior: "smooth" });
            } else {
                track.scrollBy({ left: scrollAmount, behavior: "smooth" });
            }
        }

        function scrollLeft() {
            track.scrollBy({ left: -scrollAmount, behavior: "smooth" });
        }

        let timer = setInterval(scrollRight, 7000);

        rightArrow.addEventListener('click', () => {
            scrollRight();
            clearInterval(timer);
            timer = setInterval(scrollRight, 7000);
        });

        leftArrow.addEventListener('click', () => {
            scrollLeft();
            clearInterval(timer);
            timer = setInterval(scrollRight, 7000);
        });
    });
});



let slides = document.querySelectorAll('.testimonial-item');
let index = 0; 

// Функция для перехода к следующему слайду
function nextSlide() {
    slides[index].classList.remove('active');
    index = (index + 1) % slides.length;
    slides[index].classList.add('active');
}

// Функция для перехода к предыдущему слайду
function prevSlide() {
    slides[index].classList.remove('active');
    index = (index - 1 + slides.length) % slides.length;
    slides[index].classList.add('active');
}


