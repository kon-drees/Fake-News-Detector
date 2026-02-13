from ddgs.exceptions import DDGSException
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider


from app.schemas import FactCheckResponse
from app.core.config import Settings
from app.core.logging_config import get_logger

settings = Settings()

logger = get_logger(__name__)

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
            tools=[duckduckgo_search_tool(max_results=12)],
            instructions=FactCheckAgent.load_instructions(),
            retries=3
        )

    def load_model(self) -> Model:
        """
        Determines the LLM backend based on available credentials.
        Returns a TestModel if the API key is missing or invalid
        """
        api_key = settings.OPENAI_API_KEY

        if not api_key or len(api_key) < 30:
            logger.warning("No Key found")
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

    async def run_fact_check(self, text: str) -> FactCheckResponse:
        """
        Analyzes a given text for factual accuracy using an LLM agent.
        This method triggers an asynchronous call to OpenAI.
        """

        try:
            result = await self.agent.run(text)
            return result.output
        except DDGSException as e:
            raise ModelRetry(
                f"The search engine is temporarily unavailable (Error: {e}). "
                "Please try one more time with a refined query or proceed with your internal knowledge."
            )
