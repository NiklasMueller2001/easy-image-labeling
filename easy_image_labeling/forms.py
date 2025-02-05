from typing import Any
from flask_wtf import FlaskForm
from wtforms import (
    FieldList,
    FormField,
    Form,
    ValidationError,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, Length


class DuplicateValidator:
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


class LabelNameForm(FlaskForm):
    label_name = StringField(
        "Label", validators=[InputRequired(), Length(min=1, max=25)]
    )


class LabelNameFormContainer(FlaskForm):
    label_names = FieldList(
        FormField(LabelNameForm),
        "All Labels",
        validators=[DuplicateValidator("label_name")],
        min_entries=0,
    )
    submit = SubmitField()
