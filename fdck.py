
import psycopg2
import asyncio
import asyncpg


async def test():
    try:
        conn = await asyncpg.connect(
            'postgresql://postgres:postgres@localhost:5432/crypto_prices',
            timeout=5
        )
        print('Подключение OK!')
        await conn.close()
    except Exception as e:
        print(f'Ошибка: {e}')

asyncio.run(test())


try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        database='crypto_prices',
        user='postgres',
        password='postgres',
        connect_timeout=5
    )
    print('OK!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')


async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@127.0.0.1:5432/crypto_prices', timeout=10)
        print('OK!')
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')
asyncio.run(test())
