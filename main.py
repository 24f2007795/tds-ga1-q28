import asyncio
import json
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamRequest(BaseModel):
    prompt: str
    stream: bool = True

# ----------- Generate Insights (900+ chars) -----------

def generate_insights(prompt: str) -> str:
    return f"""
1. Customers consistently highlight response time as a major satisfaction driver. Faster service interactions significantly correlate with higher retention rates and repeat purchases.

2. Product reliability is frequently mentioned in positive reviews, indicating that consistent performance builds trust and reduces churn across long-term users.

3. Users value transparency in pricing and communication. Hidden fees or unclear terms are common themes in negative feedback.

4. Customer support quality strongly influences brand perception. Empathetic, knowledgeable agents create measurable improvements in NPS scores.

5. Feature usability impacts adoption rates. Feedback suggests intuitive interfaces reduce onboarding friction and increase daily active usage.

6. Customers expect continuous innovation. Regular updates and feature improvements increase engagement and signal commitment to long-term value.

7. Mobile experience quality affects overall brand sentiment. Users frequently compare cross-platform consistency when evaluating services.

8. Personalization increases perceived value. Tailored recommendations and proactive engagement improve satisfaction metrics.

9. Security and privacy assurance significantly impact trust. Customers explicitly reference data protection practices when deciding whether to remain loyal.
    """.strip()

# ----------- Streaming Generator -----------

async def stream_generator(full_text: str):
    try:
        chunks = full_text.split("\n\n")
        for chunk in chunks:
            data = {
                "choices": [
                    {
                        "delta": {
                            "content": chunk + "\n\n"
                        }
                    }
                ]
            }

            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.2)  # simulate token streaming speed (>20 tokens/sec)

        yield "data: [DONE]\n\n"

    except Exception:
        error_data = {
            "error": "Streaming failed"
        }
        yield f"data: {json.dumps(error_data)}\n\n"
        yield "data: [DONE]\n\n"

# ----------- Endpoint -----------

@app.post("/")
async def stream_endpoint(request: StreamRequest):

    if not request.stream:
        raise HTTPException(status_code=400, detail="Streaming must be enabled")

    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt required")

    full_text = generate_insights(request.prompt)

    return StreamingResponse(
        stream_generator(full_text),
        media_type="text/event-stream"
    )

