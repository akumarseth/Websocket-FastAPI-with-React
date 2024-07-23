import redis
import time
import os
import json
import random

# Get Redis host and port from environment variables or use default values
redis_host = os.environ.get("REDIS_HOST", "10.11.153.189")
redis_port = int(os.environ.get("REDIS_PORT", 6379))

def main():
    try:
        # Connect to Redis
        r = redis.Redis(host=redis_host, port=redis_port, db=0)

        # Check if the connection is successful
        if not r.ping():
            raise Exception("Failed to connect to Redis")

        # Publish messages to a channel
        channel = 'channel_test'
        while True:
            resp = {'value': random.uniform(0, 1)}
            print(resp)
            r.publish(channel, json.dumps(resp))  # Serialize the message to JSON
            # time.sleep(1)  # Sleep for a while before publishing the next message

    except redis.ConnectionError:
        print("Failed to connect to Redis server")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
