from typing import Any, Dict, Type

from pydantic import BaseModel, create_model


class ModelConverter:

    @staticmethod
    def convert_entity_to_dict(entity):
        """entity to dictionary"""
        return {
            column.name: getattr(entity, column.name)
            for column in entity.__table__.columns
        }

    @staticmethod
    def entity_to_model(entity, pydantic_model):
        """entity to pydantic model"""
        entity_dict = ModelConverter.convert_entity_to_dict(entity)
        return pydantic_model(**entity_dict)

    @staticmethod
    def model_to_entity(pydantic_model: BaseModel, entity_class):
        """pydantic model to entity"""
        entity_dict = pydantic_model.model_dump()
        return entity_class(**entity_dict)

    @staticmethod
    def model_to_model(
        from_model: BaseModel, to_model_class: Type[BaseModel]
    ) -> BaseModel:
        fields = {
            k: (v, ...)
            for k, v in to_model_class.__annotations__.items()
            if k in from_model.__dict__
        }
        to_model = create_model(
            to_model_class.__name__, **fields
        )  # pyright: ignore [reportArgumentType, reportCallIssue]
        return to_model(**from_model.model_dump())

    @staticmethod
    def model_to_dict(model: BaseModel):
        return model.model_dump()

    @staticmethod
    def dict_to_model(model_class: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
        return model_class(**data)
