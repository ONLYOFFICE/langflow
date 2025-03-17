from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.schema import Data
from langflow.template import Output


class RedisDeleteComponent(Component):
    icon = "Redis"
    display_name = "Redis Delete"
    description = "Deletes a key from Redis."
    name = "RedisDelete"

    inputs = [
        MessageTextInput(
            name="connection_string",
            display_name="Redis Connection String",
            info="The Redis connection string (e.g., redis://localhost:6379/0).",
            required=True,
        ),
        MessageTextInput(
            name="key",
            display_name="Key",
            info="The key to delete from Redis.",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="output_data", method="delete_from_redis"),
    ]

    async def delete_from_redis(self) -> Data:
        """Delete a key from Redis."""
        try:
            from redis.asyncio import from_url
        except ImportError as e:
            msg = "Could not import the redis package. Please install it with `pip install redis`."
            raise ImportError(msg) from e

        connection_string = self.connection_string
        key = self.key

        if not connection_string:
            msg = "Redis connection string is required."
            raise ValueError(msg)

        if not key:
            msg = "Redis key is required."
            raise ValueError(msg)

        try:
            # Create Redis client from connection string
            redis_client = from_url(connection_string)
            
            # Delete key from Redis
            deleted_count = await redis_client.delete(key)
            
            # Close the Redis connection
            await redis_client.close()
            
            # Prepare result
            result = {
                "key": key,
                "deleted": deleted_count > 0,
                "count": deleted_count
            }
            
            if deleted_count > 0:
                self.status = f"Successfully deleted key '{key}' from Redis."
            else:
                self.status = f"Key '{key}' not found in Redis."
            
            return Data(data=result)
        except Exception as e:
            msg = f"Error deleting from Redis: {str(e)}"
            self.status = msg
            raise ValueError(msg) from e
