import asyncio

class Chanel:
    def __init__(self, name):
        self.name = name
        self.flags = {}
        self.input_queues = {}
        self.output_queues = {}

    def connect(self, chanel):
        self.input_queues[chanel.name] = asyncio.Queue()
        chanel.input_queues[self.name] = asyncio.Queue()
        self.output_queues[chanel.name] = chanel.input_queues[self.name]
        chanel.output_queues[self.name] = self.input_queues[chanel.name]

    async def receive_from(self, name):
        return await self.input_queues[name].get()
    
    async def send_to(self, name, message):
        await self.output_queues[name].put(message)
    
    def empty(self, name):
        return self.input_queues[name].empty()
    

class Communication:
    def __init__(self):
        self.tasks = []
        self.chanels = {}

    def get_chanel(self, name):

        if name not in self.chanels:
            chanel = Chanel(name)
            self.chanels[name] = chanel
            for n in self.chanels:
                if n != name:
                    chanel.connect(self.chanels[n])
        else:
            chanel = self.chanels[name]
        
        return chanel

    def regester(self, func, **params):
        self.tasks.append(func(**params))

    async def run(self):
        await asyncio.gather(*self.tasks)



class A:
    def __init__(self, name):
        self.count = 0
        self.name = name

    async def task(self, chanel):
         while True:
            self.count += 1
            await chanel.send_to("B", f"{self.name} says hello {self.count}")
            message = await chanel.receive_from("B")
            print(f"A received: {message}")

    async def task2(self, chanel):
        while True:
            self.count += 1
            await chanel.send_to("C", f"{self.name} says hello {self.count}")
            message = await chanel.receive_from("C")
            print(f"A received: {message}")
            

class B:
    def __init__(self, name):
        self.count = 0
        self.name = name

    async def task(self, chanel):
        while True:
            message = await chanel.receive_from("A")
            print(f"B received: {message}")
            self.count += 1
            await chanel.send_to("A", f"{self.name} says hello {self.count}")
        

class C:
    def __init__(self, name):
        self.count = 0
        self.name = name

    async def task(self, chanel):
        while True:
            message = await chanel.receive_from("A")
            print(f"C received: {message}")
            self.count += 1
            await chanel.send_to("A", f"{self.name} says hello {self.count}")


async def main():
    comm = Communication()
    a = A("A")
    b = B("B")
    c = C("C")
    chanel_a = comm.get_chanel(a.name)
    chanel_b = comm.get_chanel(b.name)
    chanel_c = comm.get_chanel(c.name)
    comm.regester(a.task, chanel=chanel_a)
    comm.regester(a.task2, chanel=chanel_a)
    comm.regester(b.task, chanel=chanel_b)
    comm.regester(c.task, chanel=chanel_c)
    await comm.run()

if __name__ == "__main__":
    asyncio.run(main())