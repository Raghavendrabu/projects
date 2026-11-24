document.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('gminsta_theme');
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    }
});

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('gminsta_theme', isDark ? 'dark' : 'light');
}