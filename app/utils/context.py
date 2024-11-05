from threading import local

_thread_local = local()

def get_index_name():
    return getattr(_thread_local, 'index_name', 'default_collection')

def set_index_name(index_name: str):
    _thread_local.index_name = index_name

def clear_index_name():
    if hasattr(_thread_local, 'index_name'):
        del _thread_local.index_name 