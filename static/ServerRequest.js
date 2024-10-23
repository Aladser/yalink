// fetch-запрос на сервер
class ServerRequest {
    /** выполнить запрос на сервер
     * 
     * @param {*} URL адрес запроса
     * @param {*} processFunc функция успешного запроса
     * @param {*} method тип запроса
     * @param {*} errorPrg элемент для ошибок
     * @param {*} data данные
     * @param {*} headers заголовки
     */
    static async execute({URL, processFunc, method, errorPrg = null, data = null, headers = null}) {
        let response;
        if (headers) {
            response = await fetch(URL, {
                method: method,
                headers: headers,
                body: data,
            });
        } else {
            response = await fetch(URL, {
                method: method,
                body: data,
            });
        }

        switch (response.status) {
            case 200:
                let data = await response.text();
                processFunc(data);
                break;
            case 419:
                window.open("/auth_error", "_self");
                break;
            case 500:
                window.open("/500", "_self");
                break;
            default:
                if (errorPrg) {
                    errorPrg.textContent = "Серверная ошибка. Подробности в консоли браузера";
                }
                console.log(response.text().then(data => console.log(data)));
        }
    }
}