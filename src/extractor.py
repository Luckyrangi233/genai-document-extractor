"""Vision-language extraction: document image → strict Pydantic JSON."""
import os, base64, io, json
from PIL import Image
from .schemas import Invoice

SCHEMA_HINT = Invoice.model_json_schema()

PROMPT = f"""Extract the invoice/receipt in this image into JSON matching EXACTLY
this JSON Schema (dates as ISO YYYY-MM-DD, numbers as plain floats):
{json.dumps(SCHEMA_HINT)}
Return ONLY the JSON object, no markdown."""

def _b64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def extract_invoice(image: Image.Image) -> Invoice:
    provider = os.getenv("LLM_PROVIDER", "openai")
    if provider == "anthropic":
        from anthropic import Anthropic
        client = Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-5", max_tokens=2048,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                             "data": _b64(image)}},
                {"type": "text", "text": PROMPT}]}])
        raw = msg.content[0].text
    else:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o", temperature=0, max_tokens=2048,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{_b64(image)}"}}]}])
        raw = resp.choices[0].message.content
    return Invoice.model_validate_json(raw)
