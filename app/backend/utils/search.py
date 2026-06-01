from sqlalchemy import and_


def apply_words_filter(db_field, search_text):
    words = search_text.strip().split()
    conditions = []
    for word in words:
        condition = db_field.ilike(f"%{word}%")
        conditions.append(condition)

    return and_(*conditions)