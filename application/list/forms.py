from application.models import List
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class CreateForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=256)],
        render_kw={'autofocus': True})

    submit = SubmitField('Create')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})

    def validate_name(self, name):
        lst = List.query.filter_by(name=name.data).first()
        if lst is not None:
            raise ValidationError('The list already exists.')


class UpdateForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=256)],
        render_kw={'autofocus': True})

    version_id = HiddenField('Version', render_kw={'readonly': True})
    submit = SubmitField('Update')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})

    def __init__(self, original_name, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            lst = List.query.filter_by(name=name.data).first()
            if lst is not None:
                raise ValidationError('The list already exists.')


class DeleteForm(FlaskForm):
    name = StringField('Name', render_kw={'readonly': True})
    version_id = HiddenField('Version', render_kw={'readonly': True})
    submit = SubmitField('Delete')
    cancel = SubmitField(
        'Cancel', render_kw={'type': 'button', 'autofocus': True})
