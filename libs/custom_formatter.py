from django.forms import BooleanField


class CustomFormatter:
    @staticmethod
    def get_form_required_field_labels(form) -> tuple:
        """Получает обязательные поля формы"""

        return tuple(field.label for field in form.fields.values() if field.required)

    @staticmethod
    def format_form_fields(form) -> None:
        """Форматирует поля формы"""

        for field in form.fields.values():
            if not isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-control mb-2 bgcolor-beige border-theme'
            else:
                field.widget.attrs['class'] = 'mb-2'
