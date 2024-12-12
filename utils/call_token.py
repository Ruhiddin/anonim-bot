from redis_conf import redis_client as rc


async def cb_get_user_id(token):
    """
    Retrieve the user ID associated with a specific token.

    Args:
        token (str): The token to search.

    Returns:
        str: The user ID if found, None otherwise.
    """
    user_id = await rc.get(f'{token}')
    if not user_id:
        return None
    return user_id.decode() if isinstance(user_id, bytes) else user_id


async def cb_get_token_by_user_id(user_id):
    """
    Retrieve the token associated with a specific user ID.

    Args:
        user_id (str): The user ID to search.

    Returns:
        str: The token if found, None otherwise.
    """
    token = await rc.get(f'user:{user_id}:token')
    if not token:
        return None
    return token.decode() if isinstance(token, bytes) else token


async def cb_set_user_id(token, user_id):
    """
    Set the user ID for a specific token and vice versa.

    Args:
        token (str): The token to associate with the user ID.
        user_id (str): The user ID to associate with the token.

    Returns:
        bool: True if the operation was successful.
    """
    # Set token → user_id mapping
    await rc.set(f'{token}', user_id)
    # Set user_id → token mapping
    await rc.set(f'user:{user_id}:token', token)
    return True


async def cb_remove(token):
    """
    Remove a token and its associated user ID.

    Args:
        token (str): The token to remove.

    Returns:
        bool: True if the operation was successful.
    """
    user_id = await cb_get_user_id(token)
    if not user_id:
        return False  # Token not found
    
    # Remove the token → user_id and user_id → token mappings
    await rc.delete(f'{token}')
    await rc.delete(f'user:{user_id}:token')
    return True
