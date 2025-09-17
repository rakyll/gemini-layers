import asyncio
from geminilayers import Serial, Parallel
from geminilayers import Echo, Reverse, Text, ReplaceText


async def main():
   serial_branch = Serial([
         Echo(),
         Reverse(),
   ]).run(Text('Hello, World!'))

   # Optionally, wait until serial_branch is done.
   await serial_branch

   parallel_branch = Parallel([
         ReplaceText("World", "Universe"),
         ReplaceText("World", "Planet"),
   ]).run(serial_branch)

   async for content in parallel_branch:
       print(content)

   await parallel_branch


if __name__ == "__main__":
    asyncio.run(main())
