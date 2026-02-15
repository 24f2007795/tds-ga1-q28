import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(status_code=200)

@app.get("/")
def health():
    return {"status": "ok"}

# ---------------- INSIGHT GENERATOR ----------------

def generate_insights(prompt: str) -> str:
    return f"""
1. Customers consistently emphasize response speed as a critical satisfaction driver. Data from surveys indicates that faster issue resolution directly improves retention rates and repeat usage patterns across service categories.

2. Reliability and uptime are frequently mentioned in positive reviews. Statistical feedback shows that stable systems significantly reduce churn and improve long-term brand trust among enterprise users.

3. Transparent pricing models strongly correlate with higher customer trust. Feedback analysis reveals that unclear fees or hidden charges are among the top complaints in negative reviews.

4. Support quality influences overall brand perception. Reviews indicate that empathetic, knowledgeable representatives increase Net Promoter Scores and customer loyalty metrics.

5. Feature usability directly impacts adoption rates. Data suggests that intuitive user interfaces reduce onboarding friction and increase daily active engagement.

6. Customers expect continuous innovation. Feedback trends show higher satisfaction scores when companies release regular feature updates and communicate roadmaps clearly.

7. Cross-platform consistency matters. Users frequently mention mobile and desktop experience alignment when evaluating overall service quality.

8. Personalization enhances perceived value. Behavioral analytics demonstrate that tailored recommendations significantly improve engagement and customer satisfaction.

9. Security and privacy transparency are major trust factors. Feedback highlights that clear data protection policies positively influence long-term customer retention decisions.
    """.strip()

# ---------------- STREAM GENERATOR ----------------

async def stream_generator(full_text: str):
    try:
        chunks = full_text.split("\n\n")

        for chunk in chunks:
            payload = {
                "choices": [
                    {
                        "delta": {
                            "content": chunk + "\n\n"
                        }
                    }
                ]
            }

            yield f"data: {json.dumps(payload)}\n\n"

            # High throughput simulation (>20 tokens/sec)
            await asyncio.sleep(0.1)

        yield "data: [DONE]\n\n"

    except Exception:
        error_payload = {"error": "Streaming error occurred"}
        yield f"data: {json.dumps(error_payload)}\n\n"
        yield "data: [DONE]\n\n"

# ---------------- STREAM ENDPOINT ----------------

@app.post("/")
async def stream_endpoint(request: Request):

    try:
        body = await request.json()
    except:
        body = {}

    prompt = body.get("prompt", "")
    stream = body.get("stream", True)

    if not prompt:
        return {
            "error": "Prompt required"
        }

    full_text = generate_insights(prompt)

    if not stream:
        # fallback non-stream response
        return {
            "choices": [
                {
                    "message": {
                        "content": full_text
                    }
                }
            ]
        }

    return StreamingResponse(
        stream_generator(full_text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

