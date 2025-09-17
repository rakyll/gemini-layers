
from geminilayers._branch import Layer, Output
from geminilayers import types
import asyncio
from typing import AsyncIterator, List
from abc import ABC, abstractmethod
from google.genai import types


class Echo(Layer):
  """A simple branch that echoes the input contents."""
  def run(
      self,
      iter: AsyncIterator[types.Content] = None,
  ) -> Output:
    if iter is None:
      raise ValueError("Echo branch requires an input iterator.")

    output = Output()
    async def _echo():
      async for content in iter:
        await output._put_content(content)
      output.done()

    tasks = asyncio.create_task(_echo())
    output._tasks.append(tasks)
    return output


class Reverse(Layer):
  """A simple branch that reverses the text in each content part."""
  def run(
      self,
      iter: AsyncIterator[types.Content] = None,
  ) -> Output:
    if iter is None:
      raise ValueError("Reverse branch requires an input iterator.")

    output = Output()
    async def _reverse():
      all_contents = []
      async for content in iter:
        all_contents.append(content)
      for content in reversed(all_contents):
        await output._put_content(content)
      output.done()

    tasks = asyncio.create_task(_reverse())
    output._tasks.append(tasks)
    return output


class ReplaceText(Layer):
  """A branch that replaces occurrences of a substring in text parts."""
  _old: str
  _new: str

  def __init__(self, old: str, new: str):
    self._old = old
    self._new = new

  def run(
      self,
      iter: AsyncIterator[types.Content] = None,
  ) -> Output:
    if iter is None:
      raise ValueError("ReplaceText requires an input iterator.")

    output = Output()
    async def _replace():
      async for content in iter:
        new_parts = []
        for part in content.parts:
          if part.text is not None:
            new_parts.append(types.Part.from_text(text=part.text.replace(self._old, self._new)))
          else:
            new_parts.append(part)
        await output._put_content(types.Content(
            role=content.role,
            parts=new_parts
        ))
      output.done()

    task = asyncio.create_task(_replace())
    output._tasks.append(task)
    return output
