import json

from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.schema import Data
from langflow.template import Output


class RedisGetComponent(Component):
    icon = "Redis"
    display_name = "Redis Get"
    description = "Retrieves a value from Redis using a key."
    name = "RedisGet"

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
            info="The key to retrieve from Redis.",
            required=True,
        ),
        MessageTextInput(
            name="default_value",
            display_name="Default Value",
            info="The default value to return if the key is not found in Redis.",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="get_from_redis"),
    ]

    async def get_from_redis(self) -> Data:
        """Retrieve a value from Redis using a key."""
        try:
            from redis.asyncio import from_url
        except ImportError as e:
            msg = "Could not import the redis package. Please install it with `pip install redis`."
            raise ImportError(msg) from e

        connection_string = self.connection_string
        key = self.key
        default_value = self.default_value if hasattr(self, "default_value") else ""

        if not connection_string:
            msg = "Redis connection string is required."
            raise ValueError(msg)

        if not key:
            msg = "Redis key is required."
            raise ValueError(msg)

        try:
            # Create Redis client from connection string
            redis_client = from_url(connection_string)
            
            # Get value from Redis
            value = await redis_client.get(key)
            
            # Close the Redis connection
            await redis_client.close()
            
            if value is None:
                # Use default value if key not found
                result = default_value
                self.status = f"Key '{key}' not found in Redis. Using default value."
            else:
                # Try to decode as JSON if possible
                try:
                    if isinstance(value, bytes):
                        decoded_value = value.decode("utf-8")
                        try:
                            result = json.loads(decoded_value)
                        except json.JSONDecodeError:
                            result = decoded_value
                    else:
                        result = value
                except Exception:
                    # Handle any unexpected errors in decoding
                    if isinstance(value, bytes):
                        result = value.decode("utf-8", errors="replace")
                    else:
                        result = str(value)
                
                self.status = f"Successfully retrieved value for key '{key}'."
            
            return Data(data=result)
        except Exception as e:
            msg = f"Error retrieving from Redis: {str(e)}"
            self.status = msg
            raise ValueError(msg) from e