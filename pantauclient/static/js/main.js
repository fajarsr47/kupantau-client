const menuBtn = document.getElementById('menu-btn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('menu-overlay');
function toggleMenu() {
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}
menuBtn.addEventListener('click', toggleMenu);
overlay.addEventListener('click', toggleMenu);