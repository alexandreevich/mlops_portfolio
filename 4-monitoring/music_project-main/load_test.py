import asyncio
import aiohttp
import time


async def simple_load_test(url: str, rps: int, duration: int = 10):
    """Простой тест на заданный RPS"""

    async def make_request(session):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status
        except:
            return 0

    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=500)
    ) as session:

        print(f"Генерируем {rps} RPS в течение {duration} секунд")
        start_time = time.time()
        total_requests = 0

        while time.time() - start_time < duration:
            # Партия запросов на 0.1 секунды
            batch_size = max(1, rps // 10)
            tasks = [make_request(session) for _ in range(batch_size)]

            batch_start = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_requests += len(results)

            # Контроль времени
            elapsed = time.time() - batch_start
            await asyncio.sleep(max(0, 0.1 - elapsed))

        actual_rps = total_requests / (time.time() - start_time)
        print(f"Фактический RPS: {actual_rps:.1f}")


# Использование
if __name__ == "__main__":
    for rps in [50, 75, 100, 125, 150, 175, 200, 250]:
        asyncio.run(simple_load_test("http://localhost:8081/api/recommend/?track_title=Love&n=5", rps, 30))
