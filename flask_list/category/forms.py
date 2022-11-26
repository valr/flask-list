from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from flask_list.models import Category


class CreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    submit = SubmitField("Create")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def __init__(self, list_id, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.list_id = list_id

    def validate_name(self, name):
        category = Category.query.filter(
            Category.list_id == self.list_id, Category.name == name.data
        ).first()

        if category is not None:
            raise ValidationError("The category name already exists.")


class UpdateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    version_id = HiddenField("Version")
    submit = SubmitField("Update")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def __init__(self, list_id, original_name, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.list_id = list_id
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            category = Category.query.filter(
                Category.list_id == self.list_id, Category.name == name.data
            ).first()

            if category is not None:
                raise ValidationError("The category name already exists.")


class DeleteForm(FlaskForm):
    name = StringField("Name", render_kw={"readonly": True})
    version_id = HiddenField("Version")
    submit = SubmitField("Delete")
    cancel = SubmitField("Cancel", render_kw={"type": "button", "autofocus": True})
