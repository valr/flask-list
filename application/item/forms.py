from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from application.models import Item


class CreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )

    category_id = SelectField("Category", validators=[DataRequired()], coerce=int)

    submit = SubmitField("Create")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def validate_name(self, name):
        item = Item.query.filter(
            Item.name == name.data, Item.category_id == self.category_id.data
        ).first()

        if item is not None:
            raise ValidationError("The item already exists.")


class UpdateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )

    category_id = SelectField("Category", validators=[DataRequired()], coerce=int)

    version_id = HiddenField("Version", render_kw={"readonly": True})
    submit = SubmitField("Update")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def __init__(self, original_name, original_category_id, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
        self.original_category_id = original_category_id

    def validate_name(self, name):
        if (
            name.data != self.original_name
            or self.category_id.data != self.original_category_id
        ):
            item = Item.query.filter(
                Item.name == name.data, Item.category_id == self.category_id.data
            ).first()

            if item is not None:
                raise ValidationError("The item already exists.")


class DeleteForm(FlaskForm):
    name = StringField("Name", render_kw={"readonly": True})

    category_id = SelectField("Category", coerce=int, render_kw={"readonly": True})

    version_id = HiddenField("Version", render_kw={"readonly": True})
    submit = SubmitField("Delete")
    cancel = SubmitField("Cancel", render_kw={"type": "button", "autofocus": True})
