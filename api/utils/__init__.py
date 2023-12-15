def verification_cache_key(email: str) -> str:
    return f"verification:{email}"
