class ModelConverter:

    @staticmethod
    def convert_entity_to_dict(entity):
        print(entity)
        return {
            column.name: getattr(entity, column.name)
            for column in entity.__table__.columns
        }

    @staticmethod
    def entity_to_model(entity, pydantic_model):
        entity_dict = ModelConverter.convert_entity_to_dict(entity)
        return pydantic_model(**entity_dict)
