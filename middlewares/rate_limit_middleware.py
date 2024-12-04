import time
from aiogram import BaseMiddleware, types
from typing import Callable, Dict, Any, Awaitable, Tuple

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int, interval: int) -> None:
        super().__init__()
        self.limit = limit         # Max number of same consecutive actions
        self.interval = interval   # Time window in seconds
        self.user_actions = {}     # Dictionary to store actions

    def _get_action_key(self, event: types.TelegramObject) -> Tuple[int, str]:
        """Get a unique key based on user ID and event content."""
        user_id = event.from_user.id
        if isinstance(event, types.Message):
            content = event.text  # Text content for messages
        elif isinstance(event, types.CallbackQuery):
            content = event.data  # Data content for callback queries
        else:
            content = ''  # No rate limit on other event types

        return user_id, content

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
        *args,
        **kwargs  # Keep kwargs to allow extra arguments
    ) -> Any:
        # Apply rate limiting only to messages and callback queries
        if isinstance(event, (types.Message, types.CallbackQuery)):
            key = self._get_action_key(event)
            current_time = time.time()

            # Initialize or update user's action history for this key
            if key not in self.user_actions:
                self.user_actions[key] = {
                    "count": 0,
                    "last_time": current_time,
                    "last_content": None
                }

            action_record = self.user_actions[key]

            # Determine the current action content based on event type
            current_content = event.text if isinstance(event, types.Message) else event.data

            # Check if the action is the same as the last one
            if action_record["last_content"] == current_content:
                if current_time - action_record["last_time"] <= self.interval:
                    action_record["count"] += 1
                    # Check if the action count exceeds the limit
                    if action_record["count"] > self.limit:
                        if isinstance(event, types.CallbackQuery):
                            await event.answer("Juda ko'p bir xil amallar!\nTakroriy amallarga checklov o'rnatilgan.\n3 sekund ichida bitta amalni takror qila olmaysiz", show_alert=True)
                        else:
                            await event.reply("Juda ko'p bir xil amallar!\nTakroriy amallarga checklov o'rnatilgan.\n3 sekund ichida bitta amalni takror qila olmaysiz")
                        return  # Stop processing the event
                else:
                    # Reset count if the interval has expired
                    action_record["count"] = 1
            else:
                # Reset count for a different action
                action_record["count"] = 1

            # Update last action details
            action_record["last_time"] = current_time
            action_record["last_content"] = current_content

        # Call the next handler in the chain, ensuring kwargs are passed
        return await handler(event, data, *args, **kwargs)
