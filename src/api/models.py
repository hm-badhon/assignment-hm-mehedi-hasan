# mypy: disable-error-code="call-overload"
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BaseCamel(BaseModel):
    """
    Base model with camelCase aliasing for API responses.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={"by_alias": True},
    )


class StandardApiResponse(BaseCamel, Generic[T]):
    """
    Standard API success response format with statusCode and success boolean.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={"by_alias": True},
    )
    success: bool = Field(..., description="Indicates if the request was successful", example=True)  # type: ignore[call-overload]
    status_code: int = Field(..., alias="statusCode", description="HTTP status code", example=200)  # type: ignore[call-overload]
    message: str = Field(..., description="User-friendly message for UI display", example="Request processed successfully")  # type: ignore[call-overload]
    response: Optional[T] = Field(
        None, description="The actual response data payload, present on success"
    )


class ErrorApiResponse(BaseCamel):
    """
    Standard API error response format.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={"by_alias": True},
    )
    success: bool = Field(False, description="Indicates the request failed", example=False)  # type: ignore[call-overload]
    status_code: int = Field(..., alias="statusCode", description="HTTP status code", example=422)  # type: ignore[call-overload]
    message: str = Field(..., description="User-friendly error message", example="Request validation error")  # type: ignore[call-overload]
    error: Any = Field(
        ..., description="Detailed error information for debugging or logging"
    )


class ChatRequest(BaseCamel):
    """
    Request model for chat API.
    """

    user_input: str = Field(..., description="User input for the chat")


class ChatResponse(BaseCamel):
    """
    Response model for chat API.
    """

    response: str = Field(..., description="Response from the chat")


StandardApiResponse[Any].model_rebuild()
ErrorApiResponse.model_rebuild()
