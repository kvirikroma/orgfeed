from . import create_id_field, ModelCreator


class AttachmentModel(ModelCreator):
    image_id = create_id_field(
            required=True,
            description="Image ID in database",
        )
    author = create_id_field(
            required=True,
            description="Uploader`s ID in database"
        )
    post = create_id_field(
        required=True,
        description="ID of Post that contains this attachment"
    )
