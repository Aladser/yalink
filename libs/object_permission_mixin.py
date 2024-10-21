from django.shortcuts import render
from django.db import models

from authen.models import User


class ListObjectPermissionMixin:
    """Проверяет права пользователя на просмотр списка объектов"""

    def get(self, request, *args, **kwargs):
        if str(request.user) == 'AnonymousUser':
            return render(request, 'index.html')
        return super().get(request, *args, **kwargs)


class DetailObjectPermissionMixin:
    """Проверяет права пользователя на просмотр объекта"""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # проверка прав на просмотр объекта
        validation_context = validate_owner('detail', self.request.user, self.object)
        if validation_context:
            return render(request, 'information.html', context=validation_context)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class UpdateDeleteObjectPermissionMixin:
    """Проверяет права пользователя на обновление и удаление объекта """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # проверка прав на просмотр объекта
        validation_context = validate_owner('update', self.request.user, self.object)
        if validation_context:
            return render(request, 'information.html', context=validation_context)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # проверка прав на просмотр объекта
        validation_context = validate_owner('delete', self.request.user, self.object)
        if validation_context:
            return render(request, 'information.html', context=validation_context)

        return super().post(request, *args, **kwargs)


def validate_owner(action: str, authuser: User, object: models.Model):
    """Проверяет права доступа к объекту

    @param action: detail, update, delete
    @param authuser:
    @param object:
    """

    action_name_list = {
        'detail': 'просмотра',
        'update': 'обновления',
        'delete': 'удаления'
    }

    if authuser != object.owner and not authuser.is_superuser:
        context = {
            'title': 'доступ запрещен',
            'description': f"Нет прав для {action_name_list[action]} этого объекта"
        }
        return context
    else:
        return False
