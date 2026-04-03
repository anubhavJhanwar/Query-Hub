# LLM answer generation + follow-up question suggestions
from rag.config import (
    LLM_PROVIDER,
    GROQ_API_KEY, GROQ_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
)

PROMPT_TEMPLATE = """You are a customer support assistant.

RULES:
- Answer ONLY from the provided context below.
- Do NOT assume or add information not present in the context.
- If the answer is not found in the context, say exactly: "I don't know."

Context:
{context}

Question: {question}

Answer:"""

FOLLOWUP_PROMPT = """Based on this customer support question and answer, suggest exactly 3 short follow-up questions the user might ask next.
Return ONLY a JSON array of 3 strings. No explanation. Example: ["Question 1?", "Question 2?", "Question 3?"]

Question: {question}
Answer: {answer}

JSON array:"""


def _call_llm(prompt: str) -> str:
    """Call the configured LLM and return raw text."""
    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    else:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return resp.text.strip()


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Generate a grounded answer from context."""
    if not context_chunks:
        return "I don't know. No relevant documents were found in the knowledge base."
    context = "\n\n".join(context_chunks)
    return _call_llm(PROMPT_TEMPLATE.format(context=context, question=question))


def generate_followups(question: str, answer: str) -> list[str]:
    """Generate 3 suggested follow-up questions."""
    import json
    try:
        raw = _call_llm(FOLLOWUP_PROMPT.format(question=question, answer=answer))
        # Extract JSON array from response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return []
