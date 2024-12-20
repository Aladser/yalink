# Публичные файлы Яндекс Диска

#### Настройки проекта
+ создать файл *.env* по аналогии c *.env.example*
+ ``pip install -r requirements.txt``
+ создать базу данных PostgreSQL *yalink*
+ ``python manage.py migrate``
+ ``python manage.py makeusers``
+ запуск проекта:
  * локальный сервер ``python manage.py runserver``
  * настройки для nginx в папке *install* для имени сайта *yalink.local*

#### Описание

Проект предназначен для просмотра папок и файлов публичных ссылок Яндекс Диска. Для этого не используется токен доступа.
Рекурсивный просмотр файлов. Реализовано так, что можно посмотреть содержимое вложенных папок, но не загрузить их полностью.

+ Индексная страница

  ![index](/readme/index.png)
+ Если нажать на получение файлов ссылки Яндекс Диска без авторизации, редирект на страницу авторизации. 
  Два вида авторизации:
  * логин-пароль 
  * Яндекс

  ![auth](/readme/auth.png)
+ Открытие ссылки. У файлов есть кнопка *Скачать*. Можно скачать все содержимое и открыть для просмотра содержимого.

  ![search](/readme/search.png)
+ Открытие вложенной папки. В пути появляется GET-параметр path - путь до папки внутри ресурса

  ![search2](/readme/search2.png)
+ Можно скачать несколько файлов. Реализовано через JS(*index.js*): программное нажатие кнопок *Скачать* у соответствующих файлов 
  ![search_download](/readme/search_download.png)
  + Можно отфильтровать файлы по их типу. Реализовано через JS(*index.js*): показываются только элементы, соответствующие фильтру.
  ![search_filter](/readme/search_filter.png)
#### Приложения
+ ``authen`` - аутентификация пользователя
+ ``main`` - главная страница

#### Представления
+ ``main``
  * ``MainView``(`` get_context_data()`` ) - представление главной страницы
      + перенаправление на страницу авторизации, если идет запрос на получение содержимого ссылки без авторизации
      + проверка корректности ссылки
      + получение списка файлов ссылки из кэша, если ранее было запрос на их получение
      + если нет кэша, то получение списка элементов ссылки из внешнего ресурса
+ ``authen``
  * ``UserLoginView`` - авторизация логин-пароль через БД
  * ``yalogin`` - авторизация через Яндекс
  * ``RegisterView`` - регистрация пользователя в БД
  * ``ProfileView`` - профилья пользователя
  * ``CustomPasswordResetView`` - сброс пароля - отправка ссылки на почту
  * ``CustomUserPasswordResetConfirmView`` - сброс пароля - ввод нового пароля
  * ``CustomPasswordResetCompleteView`` - сброс пароля - проверка ввода нового пароля
  * ``VerificateEmailView`` - подтверждение почты
  * ``RegisterCompleteView`` - завершение регистрации
