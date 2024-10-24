/**список файлов/папок-строк публичной ссылки */
let public_link_rows = document.querySelectorAll('.public-link-row');
/** select выбора типа файлов */
let type_select = document.querySelector("#type-select")
/** кнопка загрузки нскольких файлов */
let multiple_download_button = document.querySelector("#multiple-download-button");
/** массив чекбоксов загрузки файлов */
let public_link_row_checkboxes = document.querySelectorAll(".public-link-row__checkbox");
/** массив активных чекбоксов загрузки файлов */
let active_public_link_row_checkboxes = null;

// Фильтрация файлов
if(type_select) {
    type_select.addEventListener('change', function(e){
        if (e.target.value == 'Все') {
            public_link_rows.forEach(row => row.classList.remove('d-none'));
        } else {
            public_link_rows.forEach(row => {
                switch_visibility(row, row.querySelector('.public-link-row__type').textContent == e.target.value);
            })
        }
    });
}

// действия с чекбоксами папок и файлов
if(public_link_row_checkboxes) {
    public_link_row_checkboxes.forEach(checkbox => checkbox.addEventListener('change', function(e){
        // поиск активных чекбоксов
        active_public_link_row_checkboxes = document.querySelectorAll('.public-link-row__checkbox:checked');
        switch_visibility(multiple_download_button, active_public_link_row_checkboxes.length > 0);
    }));
}

// кнопка множественной загрузки файлов
if(multiple_download_button) {
    multiple_download_button.addEventListener('click', function(e){
        // поиск кнопок загрузки из строки чекбокса
        downloadButtons = [];
        active_public_link_row_checkboxes.forEach(checkbox => {
            btn = checkbox.closest(".public-link-row").querySelector('.public-link-row__download-link');
            downloadButtons.push(btn);
        })
        downloadFilesSequentially(Array.from(downloadButtons));
    });
}


/** Переключает видимость dom-элемента
 * @param {*} dom_element DOM-элемента
 * @param {*} value - значение истинности условия
 */
function switch_visibility (dom_element, value) {
    if (value) {
        dom_element.classList.remove('d-none');
    } else {
        dom_element.classList.add('d-none');
    }
}

/** замыкание - последовательно загружает файлы */
function downloadFilesSequentially(links) {
    let index = 0;

    const downloadNext = () => {
        if (index < links.length) {
            let link = links[index];
            link.click();
            index++;
            setTimeout(downloadNext, 1000);
        } else {
            active_public_link_row_checkboxes.forEach(checkbox => checkbox.click());
        }
    };

    downloadNext();
}
