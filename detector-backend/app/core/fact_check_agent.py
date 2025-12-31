from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.schemas import FactCheckResponse, TextRequest
from app.core.config import Settings

settings = Settings()


class FactCheckAgent:
    """
    Orchestrates the LLM-based fact-checking process.
    This agent uses structural prompting via Pydantic-AI to ensure that
    a structured FactCheckResponse is returned.
    """

    def __init__(self):
        # The model is determined at runtime based on the environment config.
        self.model = self.load_model()
        self.agent = Agent(
            model=self.model,
            output_type=FactCheckResponse,
            instructions=FactCheckAgent.load_instructions(),
        )

    def load_model(self) -> Model:
        """
        Determines the LLM backend based on available credentials.
        Returns a TestModel if the API key is missing or invalid
        """
        api_key = settings.OPENAI_API_KEY

        # Heuristic to check for a valid OpenAI key format
        if not api_key or len(api_key) < 30:
            return TestModel()

        return OpenAIResponsesModel(
            model_name="gpt-5-nano",
            provider=OpenAIProvider(api_key=api_key),
        )

    @staticmethod
    def load_instructions() -> str:
        """
        Reads the system prompt from a markdown file.
        """
        with open(settings.BASE_DIR / "core" / "fact_check_instructions.md", "r") as f:
            return f.read()

    async def run_fact_check(self, request: TextRequest) -> FactCheckResponse:
        """
        Analyzes a given text for factual accuracy using an LLM agent.
        This method triggers an asynchronous call to OpenAI.
        """
        result = await self.agent.run(request.text)

        return result.output
