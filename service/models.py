from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    message: str


class SortParam(BaseModel):
    column: str
    sort: bool = False


class CharacterRecord(BaseModel):
    page_id: int | None = None
    name: str | None = None
    urlslug: str | None = None
    id: str | None = None
    align: str | None = None
    eye: str | None = None
    hair: str | None = None
    sex: str | None = None
    gsm: str | None = None
    alive: str | None = None
    appearances: int | None = None
    first_appearance: str | None = None
    year: int | None = None


_TF_TEXT = "No default value is required, presence equates to true"


class CharacterSearchBody(BaseModel):
    """Request body for POST endpoints."""

    characters: list[str] | str | None = Field(None, description="Character(s) to search for. Either a string or Array of strings.")
    format: str | None = Field(None, description="Output format (currently only JSON)")
    h: list[str] | str | None = Field(None, description="Headers to display. Either a string or Array of strings")
    help: bool | None = Field(None, description=f"List available options. {_TF_TEXT}")
    limit: int | None = Field(None, description="Limit result set. '0' for no limit")
    nulls: Literal["first", "last"] | None = Field(
        None,
        description='Sort null values either "first" or "last" in the order.',
    )
    pretty: bool | str | None = Field(None, description=f"Pretty print the result set. {_TF_TEXT}")
    prune: bool | str | None = Field(None, description=f"Remove keys with null values. {_TF_TEXT}")
    random: bool | str | None = Field(None, description=f"Returns array of random superheroes based on limit. {_TF_TEXT}")
    s: list[SortParam | dict[str, Any]] | str | None = Field(None, description="Columns to sort on. Either a string or Array of sort objects")
    seed: bool | str | None = Field(None, description=f"Keep the same random characters on multiple requests. {_TF_TEXT}")
    universe: str | None = None
