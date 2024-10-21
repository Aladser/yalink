from libs.custom_formatter import CustomFormatter


class AuthenMixin:
    """Кастомизированный миксин авторизации и регистрации пользователя"""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["required_fields"] = CustomFormatter.get_form_required_field_labels(context["form"])
        return context
