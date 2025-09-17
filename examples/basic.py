import asyncio
from geminilayers import Serial, Parallel
from geminilayers import Echo, Reverse, Text, ReplaceText, Judge, AudioGenerator


async def main():
   serial_branch = Serial([
         Echo(),
         Reverse(),
   ]).run(Text('Hello, World!'))

   # Developers can wait until serial_branch is done.
   await serial_branch

   # Parallel branch will copy the input to both branches.
   # Each branch will replace "World" with a different word.
   # Branches run concurrently.
   parallel_branch = Parallel([
         ReplaceText("World", "Universe"),
         ReplaceText("World", "Planet"),
   ]).run(serial_branch)

   # Generate audio from the text from the previous branch.
   audio_branch = AudioGenerator(
         model="gemini-2.5-pro",
   ).run(parallel_branch)

   # Layers can be called one by one.
   judge_branch = Judge(
         model="gemini-2.5-pro",
         instructions="Judge whether the audio contains 'Universe'. If it does, keep it; otherwise, discard it.",
   ).run(audio_branch)
   async for content in judge_branch:
     print(content)


if __name__ == "__main__":
    asyncio.run(main())
