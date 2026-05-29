from typing import Generic, TypeVar

from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class StandardResponse(GenericModel, Generic[DataT]):
    status: str = "success"
    data: DataT
