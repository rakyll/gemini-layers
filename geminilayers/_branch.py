import asyncio
from typing import Iterator
from abc import ABC, abstractmethod
from typing import AsyncIterator
from typing import List
from ._iter import copy_iter
from asyncio import Queue
from google.genai import types

Content = types.Content


class Output():
  _queue: Queue
  _tasks: List[asyncio.Task]
  _refs: int

  def __init__(self, refs: int = 1):
    self._queue = Queue()
    self._tasks = []
    self._refs = refs

  def status(self):
    # TODO: Implement status reporting.
    pass

  def __aiter__(self):
    return self

  async def __anext__(self):
    content = await self._queue.get()
    if content is StopAsyncIteration:
      raise StopAsyncIteration
    return content

  async def _put_content(self, content: types.Content):
    await self._queue.put(content)

  def done(self):
    self._refs -= 1
    if self._refs == 0:
      self._queue.put_nowait(StopAsyncIteration)

  def __await__(self):
    return asyncio.gather(*self._tasks).__await__()


class Layer(ABC):

  @abstractmethod
  def run(
      self,
      iter: AsyncIterator[types.Content] = None,
  ) -> Output:
    pass



class Serial(Layer):
  """Runs branches in serial, passing the output of one as the input to the next."""
  _branches: List[Layer]

  def __init__(self, branches: List[Layer] | None = None):
    self._branches = branches

  def run(
      self,
      iter: AsyncIterator[types.Content] = None,
  ) -> Output:
    if self._branches is None or len(self._branches) == 0:
      raise ValueError("No branches to run in Serial.")

    output = Output()
    async def _run():
      current_iter = iter

      for i, branch in enumerate(self._branches):
        out = branch.run(iter=current_iter)
        current_iter = out

        if i == len(self._branches) - 1:
          async for content in out:
            await output._put_content(content)
      output.done()

    task = asyncio.create_task(_run())
    output._tasks.append(task)
    return output



class Parallel(Layer):
  """Runs branches in parallel, merging their outputs."""
  _branches: List[Layer]

  def __init__(self, branches: List[Layer] | None = None):
    self._branches = branches

  def run(
      self,
      iter: AsyncIterator[types.Content]= None,
  ) -> Output:
    if self._branches is None or len(self._branches) == 0:
      raise ValueError("No branches to run in Parallel.")

    n = len(self._branches)
    output = Output(refs=n)
    async def _run():
      copies = await copy_iter(iter, n)
      for branch in self._branches:
        input = copies.pop(0)
        task = asyncio.create_task(self._drain_branch(
          branch.run(iter=input), output),
        )
        output._tasks.append(task)
    task = asyncio.create_task(_run())
    output._tasks.append(task)
    return output

  async def _drain_branch(self, branch_output: Output, output: Output):
    async for content in branch_output:
      await output._put_content(content)
    output.done()