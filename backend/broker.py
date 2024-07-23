import asyncio

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend, PubSubBroker

redis_async_result = RedisAsyncResultBackend(
    redis_url="redis://localhost:6379",
)

# Or you can use PubSubBroker if you need broadcasting
# broker = ListQueueBroker(
#     url="redis://10.11.153.189:6379",
#     result_backend=redis_async_result,
# )

broker = PubSubBroker(
    url="redis://localhost:6379",
    result_backend=redis_async_result,
    queue_name="channel_test"
    # connection_kwargs={"decode_responses": True},
)


@broker.task
async def best_task_ever() -> None:
    print("Starting the best task ever!")
    broker.listen()
    """Solve all problems in the world."""
    await asyncio.sleep(5.5)
    print("All problems are solved!")


async def main():
    task = await best_task_ever.kiq()
    print(await task.wait_result())


if __name__ == "__main__":
    asyncio.run(main())