import socket
import time
import threading
import functools
import json
import asyncio
from cube.social_platform.unity_api.unity_queue_manager import UnityQueueManager

# 全局变量来控制运行
running = True

# 异步消息队列
send_queue = asyncio.Queue()


async def send_message_to_unity(message):
    server_address = ('127.0.0.1', 8003)
    try:
        reader, writer = await asyncio.open_connection(*server_address)
        writer.write(json.dumps(message).encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"Error sending message to Unity: {e}")


async def send_position_to_unity(agent_name, x, y, z):
    message = {
        "agent_name": agent_name,
        "message": f"{x},{y},{z}"
    }
    await send_queue.put(message)


async def send_stop_to_unity(agent_name):
    message = {
        "agent_name": agent_name,
        "message": "STOP"
    }
    await send_queue.put(message)


from functools import partial

async def handle_connection(unity_queue_manager, reader, writer):
    global running
    while running:
        try:
            data = await reader.read(1024)
            if not data:
                break
            message = json.loads(data.decode('utf-8'))
            agent_id = message.get('agent_name')
            await unity_queue_manager.put_message(agent_id, message)  # 注意这里改为异步调用
            print(f"Received message: {message}")
        except Exception as e:
            print(f"Error handling connection: {e}")
            break
    writer.close()
    await writer.wait_closed()

async def receive_from_unity(unity_queue_manager: UnityQueueManager):
    global running
    server_address = ('127.0.0.1', 8004)
    
    # 使用 partial 创建一个新的函数，该函数包含 unity_queue_manager 参数
    handler = partial(handle_connection, unity_queue_manager)
    
    server = await asyncio.start_server(handler, *server_address)
    print("Waiting for connections from Unity...")
    async with server:
        await server.serve_forever()

async def message_sender():
    global running
    while running:
        try:
            message = await asyncio.wait_for(send_queue.get(), timeout=1.0)
            await send_message_to_unity(message)
            send_queue.task_done()
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Error sending message: {e}")


async def start_server(unity_queue_manager: UnityQueueManager):
    global running
    running = True

    # 启动接收任务
    receive_task = asyncio.create_task(receive_from_unity(unity_queue_manager))

    # 启动消息发送任务
    sender_task = asyncio.create_task(message_sender())

    print("Server started.")
    return receive_task, sender_task


async def stop_server(receive_task, sender_task):
    global running
    running = False
    receive_task.cancel()
    sender_task.cancel()
    try:
        await receive_task
    except asyncio.CancelledError:
        pass
    try:
        await sender_task
    except asyncio.CancelledError:
        pass
    print("Server stopped.")

'''async def get_received_message(queue_id: str):
    try:
        if queue_id == '1':
            receive_result = await asyncio.wait_for(receive_queue_1.get(), timeout=0.1)
            print('\n\nget_received_message:', receive_result)
            return receive_result
        elif queue_id == '2':
            receive_result = await asyncio.wait_for(receive_queue_2.get(), timeout=0.1)
            print('\n\nget_received_message:', receive_result)
            return receive_result
        elif queue_id == '3':
            receive_result = await asyncio.wait_for(receive_queue_3.get(), timeout=0.1)
            print('\n\nget_received_message:', receive_result)
            return receive_result
    except asyncio.TimeoutError:
        return None'''


async def main():
    tasks = await start_server()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the server...")
        await stop_server(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
