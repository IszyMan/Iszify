const modal = document.querySelector('.hamburger'); // Use querySelector to get a single element
const overlay = document.querySelector('.side_fold'); // Use querySelector to get a single element

function toggleActiveClass() {
    overlay.classList.toggle('active');
}