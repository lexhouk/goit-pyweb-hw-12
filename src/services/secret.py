from aiofile import async_open


async def secret() -> str:
    async with async_open('.secret', encoding='utf-8') as file:
        return await file.read()
