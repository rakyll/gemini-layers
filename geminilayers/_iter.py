import copy
from typing import AsyncIterator, List
from google.genai import types

class _CopyAsyncIterator:
  def __init__(self, buffer: List[types.Content]):
    self._buffer = copy.deepcopy(buffer)

  async def __anext__(self) -> types.Content:
    if self._buffer:
      return self._buffer.pop(0)
    else:
      raise StopAsyncIteration

  def __aiter__(self) -> AsyncIterator[types.Content]:
    return self

async def copy_iter(
    source: AsyncIterator[types.Content], n: int
) -> List[AsyncIterator[types.Content]]:
  """
  Takes an AsyncIterator and returns N independent AsyncIterator copies
  that will yield the same sequence of items.

  Args:
      source_iterator: The original AsyncIterator to copy.
      n: The number of copies to create.

  Returns:
      A list of N AsyncIterator objects.
  """
  if n <= 0:
      return []

  buffered = []
  async for item in source:
    buffered.append(item)

  return [_CopyAsyncIterator(buffered) for _ in range(n)]
