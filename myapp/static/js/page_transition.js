document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;


    //Para que la transición sea suave de una pagina a otra
    body.classList.add('page-loaded');

    //Para los clics en los enlaces
    document.querySelectorAll('a').forEach(link => {

        //Para excluir enlaces externos
        if (link.href && !link.target && !link.href.startsWith('#') && !link.href.endsWith('.pdf')) {
            link.addEventListener('click', (e) => {
                const targetUrl = link.href;

                //Para prevenir la navegación inmediata
                e.preventDefault();

                // Añadir una clase para la animación de salida
                body.classList.remove('page-loaded'); 
                body.classList.add('page-transition-out');

                // Esperar a que la animación termine antes de navegar
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 500);
            });
        }
    });
});