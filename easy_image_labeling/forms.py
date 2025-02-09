from typing import Any
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import (
    FieldList,
    FormField,
    Form,
    MultipleFileField,
    ValidationError,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, Length


class DuplicateStringInputValidator:
    """
    Custom validator to ensure no duplicate values were entered for
    forms that contain field lists.
    """

    def __init__(self, field_name: str) -> None:
        """
        Parameters
        ----------
        field_name: str
            Set name of fields inside field list.
        """
        self.field_name = field_name

    def __call__(self, form: Form, field_list: FieldList) -> Any:
        unique_fields = set()
        raw_fields = list()
        for data_dict in field_list.data:
            unique_fields.add(data_dict[self.field_name])
            raw_fields.append(data_dict[self.field_name])
        if not len(unique_fields) == len(raw_fields):
            raise ValidationError("Fields must not contain duplicate data.")


class NoSpecialCharactersValidator:
    """
    Custom validator to ensure the entered text in the input field does
    not contain any of the specified characters.
    """

    def __init__(self, excluded_characters: list[str] | None = None) -> None:
        """
        Parameters
        ----------
        field_name: str
            Set name of fields inside field list.
        """
        if excluded_characters is None:
            self.excluded_characters = [
                " ",
                "/",
                "\\",
                "*",
                "~",
                "+",
                "&",
                "%",
                "$",
                "§",
            ]
        else:
            self.excluded_characters = excluded_characters

    def __call__(self, form: Form, field: StringField) -> Any:
        input = field.data
        if input is None:
            raise ValidationError("Invalid input.")
        for excluded_character in self.excluded_characters:
            if " " in input:
                raise ValidationError(
                    f"Input must not contain any '{excluded_character}' characters"
                )


class PictureFolderValidator:
    """
    Checks if selected folder in upload form contains at least one file
    and checks if all files inside folder have supported extensions.
    """

    def __init__(self, allowed_extensions: tuple[str] | None = None) -> None:
        if allowed_extensions is None:
            self.allowed_extensions = ("jpg", "png", "pdf")
        else:
            self.allowed_extensions = allowed_extensions

    def __call__(self, form: Form, field: MultipleFileField) -> Any:
        if not form.files.data:  # type: ignore
            raise ValidationError("No files were selected.")

        for file in form.files.data:  # type: ignore
            if not file.filename:  # Ensures the file has a valid name
                raise ValidationError("Empty file detected.")
            if not (
                "." in file.filename
                and file.filename.rsplit(".", 1)[1] in self.allowed_extensions
            ):
                raise ValidationError(
                    f"Invalid file type: {file.filename}.\nAllowed filetypes are {self.allowed_extensions}"
                )


class LabelNameForm(FlaskForm):
    label_name = StringField(
        "Label",
        validators=[
            InputRequired(),
            Length(min=1, max=20),
            NoSpecialCharactersValidator(),
        ],
    )


class LabelNameFormContainer(FlaskForm):
    label_names = FieldList(
        FormField(LabelNameForm),
        "All Labels",
        validators=[DuplicateStringInputValidator("label_name")],
        min_entries=0,
    )
    submit = SubmitField()


class UploadFolderForm(FlaskForm):
    files = MultipleFileField(
        "Upload Files",
        validators=[
            PictureFolderValidator(),
            FileAllowed(
                ["pdf", "jpg", "png"], "Only .png, .pdf or .jpg file types allowed!"
            ),
        ],
    )
    dataset_name = StringField(
        "Dataset name",
        validators=[
            InputRequired(),
            Length(min=1, max=20),
            NoSpecialCharactersValidator(),
        ],
    )
    submit = SubmitField("Upload Files")
