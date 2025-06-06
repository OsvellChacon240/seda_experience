(function(){
    const btnEliminacion = document.querySelectorAll(".btnEliminacion");

    btnEliminacion.forEach(btn => {
        btn.addEventListener('click',(e) => {
            const confirmacion = confirm('Are you sure you want to delete?');
            if (!confirmacion){
                e.preventDefault();
            }
        });
    });
})();