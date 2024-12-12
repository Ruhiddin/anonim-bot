import random
import string
from utils import user_token as u
from utils import call_token as c
from redis_conf import redis_client as rc

async def unique_user_token(length=8):
    """
    Generate a unique callback token consisting of numbers and case-sensitive English letters for the user.
    
    Args:
        length (int): The length of the unique ID. Default is 8.
    
    Returns:
        str: A randomly generated unique ID.
    """
    characters = string.ascii_letters + string.digits
    while True:
        # Generate a random token
        token = ''.join(random.choices(characters, k=length))
        
        # Check if the token already exists for a user
        old = await u.get_user_by_token(token)  # assuming u is the module for user-related operations
        if old is None:
            return token


async def unique_callback_token(length=8):
    """
    Generate a unique callback token consisting of numbers and case-sensitive English letters for the callback.
    
    Args:
        length (int): The length of the unique ID. Default is 8.
    
    Returns:
        str: A randomly generated unique ID.
    """
    characters = string.ascii_letters + string.digits
    while True:
        # Generate a random token
        token = ''.join(random.choices(characters, k=length))
        
        # Check if the token already exists for a callback
        old = await c.cb_get_user_id(token)  # assuming c is the module for callback-related operations
        if old is None:
            return token
