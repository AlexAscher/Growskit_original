def callfunc(func, *args, fail_silently=False, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if not fail_silently:
            raise
        print(f'${func.__module__}.{func.__name__} Exception: {e}')

def get_chat_id(tg_link: str):
    if 't.me/' in tg_link:
        return tg_link.split('t.me/')[1].split('/')[0]
    return tg_link

def clear_user(tg: str):
    if not tg:
        return ""
    
    chat_id = get_chat_id(tg)
    if not chat_id.isdigit():
        chat_id = '@' + chat_id

    return chat_id
