# https://github.com/langchain-ai/langchain/discussions/19782
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, Field


class SearchAPIWrapperBase(BaseModel, ABC):
    """Abstract base class for search API wrappers.
    e.g. GoogleSearchAPIWrapper, DuckDuckGoSearchAPIWrapper..."""

    class Config:
        extra = Extra.forbid

    search_engine_name: str = Field(..., description="Search engine name")

    @abstractmethod
    def run(self, query: str) -> str:
        """Run query through the search engine and return concatenated results."""
        pass

    @abstractmethod
    def results(self, query: str, max_results: int, **search_params: Any) -> List[Dict[Any, Any]]:
        """Run query through the search engine and return metadata.

        Args:
            query: The query to search for.
            max_results: The maximum number of results to return.
            **search_params: Additional search arguments specific to each implementation.

        Returns:
            A list of dictionaries with metadata about each result.
        """
        pass