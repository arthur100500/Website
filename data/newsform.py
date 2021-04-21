from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок')
    content = TextAreaField("Содержание", validators=[DataRequired()])
    submit = SubmitField('Применить')
