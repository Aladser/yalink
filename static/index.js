// Фильтрация файлов
let type_select = document.querySelector("#type-select");
if(type_select) {
    type_select.addEventListener('change', function(e){
        let currentURL = window.location.href + `&type=` + e.target.value;
        fetch(currentURL).then(response => response.json()).then(data=> console.log(data));
    })
}
