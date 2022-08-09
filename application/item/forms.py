from flask_wtf import FlaskForm
from wtforms import (HiddenField, RadioField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, InputRequired, Length, Optional,
                                ValidationError)

from application.models import Item


class CreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    category_id = SelectField("Category", validators=[DataRequired()], coerce=int)
    # don't use DataRequired for type_ as it does validation post-coercion and
    # validation can fail due to falsy value
    type_ = RadioField("Type", validators=[InputRequired()], coerce=int)
    submit = SubmitField("Create")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def validate_name(self, name):
        item = Item.query.filter(
            Item.category_id == self.category_id.data, Item.name == name.data
        ).first()

        if item is not None:
            raise ValidationError("The item name already exists.")


class UpdateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    category_id = SelectField("Category", validators=[DataRequired()], coerce=int)
    type_ = RadioField("Type", validators=[InputRequired()], coerce=int)
    version_id = HiddenField("Version")
    submit = SubmitField("Update")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def __init__(self, original_category_id, original_name, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.original_category_id = original_category_id
        self.original_name = original_name

    def validate_name(self, name):
        if (
            self.category_id.data != self.original_category_id
            or name.data != self.original_name
        ):
            item = Item.query.filter(
                Item.category_id == self.category_id.data, Item.name == name.data
            ).first()

            if item is not None:
                raise ValidationError("The item name already exists.")


class DeleteForm(FlaskForm):
    name = StringField("Name", render_kw={"readonly": True})
    category_name = StringField("Category", render_kw={"readonly": True})
    # readonly doesn't seem to work, so using disable instead
    # however disable makes the validation fail
    # so stopping the validation using the Optional validator
    type_ = RadioField(
        "Type", validators=[Optional()], coerce=int, render_kw={"disabled": True}
    )
    version_id = HiddenField("Version")
    submit = SubmitField("Delete")
    cancel = SubmitField("Cancel", render_kw={"type": "button", "autofocus": True})
