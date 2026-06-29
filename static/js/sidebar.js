/* Sidebar de nível único.
   Desktop: expande no hover / foco de teclado (CSS).
   Toque (sem hover): tocar na régua — fora dos links — abre/fecha. */
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    if (window.matchMedia('(hover: none)').matches) {
        sidebar.addEventListener('click', (e) => {
            if (e.target.closest('a, button, form')) return;  // links/ações navegam normalmente
            sidebar.classList.toggle('open');
        });
        const main = document.getElementById('main-content');
        if (main) main.addEventListener('click', () => sidebar.classList.remove('open'));
    }
});
