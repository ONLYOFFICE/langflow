import json

from langflow.custom import Component
from langflow.inputs import MessageTextInput, IntInput, DataInput
from langflow.schema import Data
from langflow.template import Output


class RedisSetComponent(Component):
    icon = "Redis"
    display_name = "Redis Set"
    description = "Inserts a value into Redis using a key."
    name = "RedisSet"

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
            info="The key to store the value in Redis.",
            required=True,
        ),
        IntInput(
            name="ttl",
            display_name="TTL",
            info="Time-to-live in seconds for the key. Set to 0 for no expiration.",
            required=False,
        ),
        DataInput(
            name="data",
            display_name="Data",
            info="The data to store in Redis.",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="output_data", method="set_to_redis"),
    ]

    async def set_to_redis(self) -> Data:
        """Insert a value into Redis using a key."""
        try:
            from redis.asyncio import from_url
        except ImportError as e:
            msg = "Could not import the redis package. Please install it with `pip install redis`."
            raise ImportError(msg) from e

        connection_string = self.connection_string
        key = self.key
        ttl = self.ttl if hasattr(self, "ttl") else 0
        data_to_store = self.data

        if not connection_string:
            msg = "Redis connection string is required."
            raise ValueError(msg)

        if not key:
            msg = "Redis key is required."
            raise ValueError(msg)

        try:
            # Create Redis client from connection string
            redis_client = from_url(connection_string)
            
            # Prepare data for storage
            if isinstance(data_to_store, Data):
                # Extract data from Data object
                value_to_store = data_to_store.data
                # Convert to JSON string for storage
                if isinstance(value_to_store, dict):
                    value_to_store = json.dumps(value_to_store)
                elif not isinstance(value_to_store, str):
                    value_to_store = str(value_to_store)
            else:
                # If it's not a Data object, convert to string
                value_to_store = str(data_to_store)
            
            # Set value in Redis with TTL if provided and greater than 0
            if ttl and ttl > 0:
                await redis_client.set(key, value_to_store, ex=ttl)
            else:
                await redis_client.set(key, value_to_store)
            
            # Close the Redis connection
            await redis_client.close()
            
            # Prepare result
            result = {
                "text": value_to_store if isinstance(value_to_store, str) else json.dumps(value_to_store),
                "value": value_to_store,
                "key": key,
                "ttl": ttl
            }
            
            self.status = f"Successfully stored value for key '{key}'."
            if ttl and ttl > 0:
                self.status += f" TTL set to {ttl} seconds."
            
            return Data(data=result)
        except Exception as e:
            msg = f"Error storing to Redis: {str(e)}"
            self.status = msg
            raise ValueError(msg) from e
