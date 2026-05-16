def get_cache_key(resource: str, *args) -> str:
    parts = ["cache", resource] + [str(arg) for arg in args if arg is not None]
    return ":".join(parts)