from django import db


class TruncateTableMixin:
    """Удаление записей таблицы со сбросом автооинкремента"""

    @classmethod
    def truncate(cls):
        """Удаляет записи таблицы и сбрасывает автооинкремент"""

        truncate_query = f'TRUNCATE TABLE {cls._meta.db_table} RESTART IDENTITY CASCADE;'
        with db.connection.cursor() as cursor:
            cursor.execute(truncate_query)
