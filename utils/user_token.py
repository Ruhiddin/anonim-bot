import json
from redis_conf import redis_client as rc


async def get_my_tokens(user_id):
    """
    Retrieve all tokens for a given user from Redis.
    
    Args:
        user_id (str): The user ID.

    Returns:
        dict: Dictionary of tokens and their names or an empty dictionary if none exist.
    """
    data = await rc.get(f"{user_id}:tokens")
    if data:
        return json.loads(data)
    return {}


async def create_my_new_token(user_id, token, name):
    """
    Create a new token for a user and store it in Redis.

    Args:
        user_id (str): The user ID.
        token (str): The token to store.
        name (str): The name associated with the token.

    Returns:
        bool: True if the token was created successfully, False if it already exists.
    """
    tokens = await get_my_tokens(user_id)
    if token in tokens:
        return False  # Token already exists
    tokens[token] = name
    await rc.set(f"{user_id}:tokens", json.dumps(tokens))
    await rc.set(f"token:{token}", str(user_id))  # Add reverse mapping
    return True


async def delete_my_token(user_id, token):
    """
    Delete a specific token for a user from Redis.

    Args:
        user_id (str): The user ID.
        token (str): The token to delete.

    Returns:
        bool: True if the token was deleted, False if it didn't exist.
    """
    tokens = await get_my_tokens(user_id)
    print(tokens, user_id)
    if token not in tokens:
        return False  # Token doesn't exist
    del tokens[token]
    await rc.set(f"{user_id}:tokens", json.dumps(tokens))
    await rc.delete(f"token:{token}")  # Remove reverse mapping
    return True


async def update_my_token(user_id, token, new_name):
    """
    Update the name associated with a token for a user.

    Args:
        user_id (str): The user ID.
        token (str): The token to update.
        new_name (str): The new name to associate with the token.

    Returns:
        bool: True if the token was updated successfully, False if the token doesn't exist.
    """
    tokens = await get_my_tokens(user_id)
    if token not in tokens:
        return False  # Token doesn't exist
    tokens[token] = new_name
    await rc.set(f"{user_id}:tokens", json.dumps(tokens))
    return True


async def get_user_by_token(token):
    """
    Retrieve the user ID associated with a specific token.

    Args:
        token (str): The token to search.

    Returns:
        str: The user ID if found, None otherwise.
    """
    user_id = await rc.get(f"token:{token}")
    return user_id if user_id else None
