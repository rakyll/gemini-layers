from google.genai import types



class Text():
  def __init__(self, text: str, role: str = 'user'):
    self.text = text
    self.role = role

  async def __aiter__(self):
    yield types.Content(
        role=self.role,
        parts=[types.Part.from_text(text=self.text)]
    )


class Bytes():
  def __init__(self, data: bytes, mime_type: str = 'application/octet-stream', role: str = 'user'):
    self.data = data
    self.mime_type = mime_type
    self.role = role

  async def __aiter__(self):
    yield types.Content(
        role=self.role,
        parts=[types.Part.from_bytes(data=self.data, mime_type=self.mime_type)]
    )
