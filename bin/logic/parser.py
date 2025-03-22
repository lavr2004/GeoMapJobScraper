def recursive_json_search_fc(json_dc, key_str):
    """
    Рекурсивно ищет ключ в JSON-данных любой вложенности и возвращает его значение.
    Поиск прекращается при первом же нахождении ключа.

    Аргументы:
        json_dc: JSON-данные в виде Python словаря или списка.
        key_str: Ключ, значение которого нужно найти (строка).

    Возвращает:
        Значение ключа, если ключ найден, иначе None.
    """

    if isinstance(json_dc, dict):
        if key_str in json_dc:
            return json_dc[key_str]
        for element in json_dc.values():
            res = recursive_json_search_fc(element, key_str)
            if res is not None:
                return res
    elif isinstance(json_dc, list):
        for element in json_dc:
            res = recursive_json_search_fc(element, key_str)
            if res is not None:
                return res
    return None # Ключ не найден в текущей ветке