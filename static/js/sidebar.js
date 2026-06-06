document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const items = sidebar.querySelectorAll('.sidebar-item');
    const userArea = sidebar.querySelector('.sidebar-user');

    items.forEach(item => {
        const btn = item.querySelector('.sidebar-icon');

        btn.addEventListener('click', () => {
            const wasActive = item.classList.contains('active');

            // Remove active de todos
            items.forEach(i => i.classList.remove('active'));

            if (wasActive) {
                // Clicou no mesmo: colapsa
                sidebar.classList.remove('expanded');
            } else {
                // Clicou em outro: expande e ativa
                item.classList.add('active');
                sidebar.classList.add('expanded');
            }
        });
    });

    // Clique no icone do usuario expande a sidebar
    if (userArea) {
        userArea.addEventListener('click', (e) => {
            // Nao interferir no botao Sair
            if (e.target.closest('.sidebar-logout')) return;

            items.forEach(i => i.classList.remove('active'));
            sidebar.classList.toggle('expanded');
        });
    }

    // Clique fora fecha a sidebar
    document.getElementById('main-content').addEventListener('click', () => {
        items.forEach(i => i.classList.remove('active'));
        sidebar.classList.remove('expanded');
    });
});
