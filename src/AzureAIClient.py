import os
import logging
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)

class AzureAIClientError(Exception):
    pass

class AzureAIClient:
    def __init__(self):
        endpoint = os.getenv("AZURE_ENDPOINT")
        api_key  = os.getenv("AZURE_API_KEY")
        if not endpoint or not api_key:
            raise AzureAIClientError("Missing AZURE_ENDPOINT or AZURE_API_KEY")
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        self.model = os.getenv("AZURE_MODEL", "DeepSeek-V3-0324")

    def analyze_diff(self, diff: str, max_tokens: int = 2048) -> str:
        try:
            from azure.ai.inference.models import SystemMessage, UserMessage
            response = self.client.complete(
                messages=[
                    SystemMessage(content="You are a senior software engineer reviewing code changes."),
                    UserMessage(content=f"Code diff:\n{diff}")
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure AI inference error: {e}")
            raise AzureAIClientError("AI analysis failed") from e
