from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from application.models import List


class CreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    submit = SubmitField("Create")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def validate_name(self, name):
        list_ = List.query.filter_by(name=name.data).first()
        if list_ is not None:
            raise ValidationError("The list already exists.")


class UpdateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"autofocus": True},
    )
    version_id = HiddenField("Version")
    submit = SubmitField("Update")
    cancel = SubmitField("Cancel", render_kw={"type": "button"})

    def __init__(self, original_name, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            list_ = List.query.filter_by(name=name.data).first()
            if list_ is not None:
                raise ValidationError("The list already exists.")


class DeleteForm(FlaskForm):
    name = StringField("Name", render_kw={"readonly": True})
    version_id = HiddenField("Version")
    submit = SubmitField("Delete")
    cancel = SubmitField("Cancel", render_kw={"type": "button", "autofocus": True})
