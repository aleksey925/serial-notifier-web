def _get_prefixes_patch(cols):
    """Доработанная версия функции get_prefixes из библиотеки asyncom. Данная реализация решает проблему с моделими в
    которых есть поля имя которых включает в себя наименование самой модели.
    Проблема оригинальной реализации в том, что replace удаляет prefix из key столько раз, сколько данная подстрока
    встречается в key, а не только 1 раз, как было задумано.

    Пример:
    class Campaign(Base):
        __tablename__ = 'campaign'

        campaign_id = Column(Integer, primary_key=True)

    """
    res = {}
    for key, col in cols:
        name = []
        if col.table.schema:
            name.append(col.table.schema)
        name.append(col.table.name)
        prefix = "_".join(name)
        res[key] = key.replace(prefix + '_', "", 1)
    return res
