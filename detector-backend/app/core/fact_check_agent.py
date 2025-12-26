from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.schemas import FactCheckResponse, TextRequest
from app.core.config import Settings

settings = Settings()


class FactCheckAgent:
    def __init__(self):
        self.model = self.load_model()
        self.agent = Agent(
            model=self.model,
            output_type=FactCheckResponse,
            instructions=FactCheckAgent.load_instructions(),
        )

    def load_model(self) -> Model:
        api_key = settings.OPENAI_API_KEY

        # Return a test model if no .env is present or a placeholder is set
        if not api_key or len(api_key) < 30:
            return TestModel()

        return OpenAIResponsesModel(
            model_name="gpt-5-nano",
            provider=OpenAIProvider(api_key=api_key),
        )

    @staticmethod
    def load_instructions() -> str:
        with open(settings.BASE_DIR / "core" / "fact_check_instructions.md", "r") as f:
            return f.read()

    async def run_fact_check(self, request: TextRequest) -> FactCheckResponse:
        result = await self.agent.run(request.text)

        return result.output
