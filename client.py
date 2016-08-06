import aiohttp
import asyncio

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

jar = aiohttp.CookieJar(unsafe=True)

async def blah():
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        async with session.get('http://localhost:8080/') as resp:
            #print(resp.status)
            print(await resp.text())
            #print(session.cookies)
            #cookie = session.cookies
            #print(jar._cookies)

        async with session.ws_connect('http://localhost:8080/ws') as ws:

            for i in range(2):
                for i in range(10):
                    ws.send_str('blah blah blah...')

                    #async for msg in ws:
                    msg = await ws.receive()
                    if msg.tp == aiohttp.MsgType.text:
                        if msg.data == 'close':
                            await ws.close()
                            break
                        else:
                            print(msg.data)
                            #ws.send_str(msg.data + '/answer')
                    elif msg.tp == aiohttp.MsgType.closed:
                        break
                    elif msg.tp == aiohttp.MsgType.error:
                        break

                #await asyncio.sleep(5)
                print(session.cookies)
                #print(session.cookies['AIOHTTP_SESSION'])
                #last_visit = session.cookies['AIOHTTP_SESSION'].get(
                #        'last_visit', 'Never')
                #print(last_visit)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(blah())

