import os
import logging
from openai import OpenAI, APIError
from typing import List, Dict

logger = logging.getLogger(__name__)

class OpenAIClientError(Exception):
    """Base exception for OpenAI errors"""

class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("INPUT_OPENAI_API_KEY")
        if not api_key:
            raise OpenAIClientError("Missing OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    def analyze_diff(self, diff: str, max_tokens: int = 8000) -> str:
        """
        Analyze code diff with contextual awareness
        Returns: Analysis text or raises OpenAIClientError
        """
        try:
            system_prompt = """You are a senior software engineer reviewing code changes.
Analyze this diff considering:
1. Security vulnerabilities
2. Logic errors
3. Code smells
4. Architectural consistency
5. Best practices

Format findings as:
- [Critical/High/Medium/Low] [Category]: Brief description
  - Impact: 
  - Suggested fix:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Code diff:\n{diff}"}
                ],
                temperature=0.2,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIClientError("AI analysis failed") from e
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {str(e)}")
            raise OpenAIClientError("AI processing failed") from e