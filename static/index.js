/**список файлов/папок-строк публичной ссылки */
let public_link_rows = document.querySelectorAll('.public-link-row');

// Фильтрация файлов
let type_select = document.querySelector("#type-select");
if(type_select) {
    type_select.addEventListener('change', function(e){
        if (e.target.value == 'Все') {
            public_link_rows.forEach(row => row.classList.remove('d-none'));
        } else {
            public_link_rows.forEach(row => {
                if(row.querySelector('.public-link-row__type').textContent == e.target.value) {
                    row.classList.remove('d-none');
                } else{
                    row.classList.add('d-none');
                }
            })
        }
    });
}
