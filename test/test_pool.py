import asyncio
import random
import time
from testing import Client
from testing import Series
from testing import default_test_setup
from testing import gen_points
from testing import gen_series
from testing import gen_data
from testing import InsertError
from testing import PoolError
from testing import run_test
from testing import Server
from testing import ServerError
from testing import SiriDB
from testing import TestBase
from testing import UserAuthError

class TestPool(TestBase):
    title = 'Test pool object'

    async def insert(self, series, n, timeout=10):
        for _ in range(n):
            while timeout:
                try:
                    await self.client0.insert_some_series(series)
                except PoolError:
                    timeout -= 1
                else:
                    break
                finally:
                    await asyncio.sleep(1.0)


    @default_test_setup(2)
    async def run(self):

        series = gen_series()

        await self.client0.connect()

        task = asyncio.ensure_future(self.insert(series, 60))

        await asyncio.sleep(5)

        await self.db.add_pool(self.server1, sleep=4)

        # task = asyncio.ensure_future(self.insert(series, 60))

        await self.client1.connect()

        await asyncio.sleep(5)

        await self.assertSeries(self.client0, series)
        await self.assertSeries(self.client1, series)

        await self.assertIsRunning(self.db, self.client0, timeout=900)

        await self.assertSeries(self.client0, series)
        await self.assertSeries(self.client1, series)

        await asyncio.wait_for(task, None)

        await self.assertSeries(self.client0, series)
        await self.assertSeries(self.client1, series)

        self.client0.close()
        self.client1.close()

        return False

if __name__ == '__main__':
    SiriDB.HOLD_TERM = False
    Server.HOLD_TERM = False
    run_test(TestPool())
