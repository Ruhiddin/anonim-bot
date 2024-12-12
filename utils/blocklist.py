from redis_conf import redis_client as rc

import json


async def get_blocklist(user_id):
    """
    Retrieve the blocklist of a user from Redis.

    Args:
        user_id (str): The ID of the user.

    Returns:
        set: A set of user IDs that the user has blocked.
    """
    data = await rc.get(f"{user_id}:blocklist")
    if data:
        return set(json.loads(data))
    return set()

async def user_block(my_id, user_id):
    """
    Add a user to the blocklist of the calling user.

    Args:
        my_id (str): The ID of the user performing the block.
        user_id (str): The ID of the user to block.

    Returns:
        bool: True if the user was successfully blocked, False if they were already blocked.
    """
    blocklist = await get_blocklist(my_id)
    if user_id in blocklist:
        return False  # User is already blocked
    blocklist.add(user_id)
    await rc.set(f"{my_id}:blocklist", json.dumps(list(blocklist)))
    return True

async def user_unblock(my_id, user_id):
    """
    Remove a user from the blocklist of the calling user.

    Args:
        my_id (str): The ID of the user performing the unblock.
        user_id (str): The ID of the user to unblock.

    Returns:
        bool: True if the user was successfully unblocked, False if they were not blocked.
    """
    blocklist = await get_blocklist(my_id)
    if user_id not in blocklist:
        return False  # User is not blocked
    blocklist.remove(user_id)
    await rc.set(f"{my_id}:blocklist", json.dumps(list(blocklist)))
    return True

async def is_user_blocked(my_id, sender_id):
    """
    Check if a specific user is blocked by the calling user.

    Args:
        my_id (str): The ID of the user performing the check.
        sender_id (str): The ID of the user to check.

    Returns:
        bool: True if the user is blocked, False otherwise.
    """
    blocklist = await get_blocklist(my_id)
    return sender_id in blocklist
