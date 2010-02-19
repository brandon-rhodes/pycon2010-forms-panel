.. include:: <s5defs.txt>

PyCon 2010 Forms Panel
----------------------

| Jonathan Ellis — FormAlchemy
| Jacob Kaplan-Moss — Django
| Chris McDonough — formish
| Christopher Perkins — Sprox

:Moderator: Brandon Craig Rhodes
:Occasion: PyCon 2010

A Quick Example
---------------

| We are familiar
| with account creation forms

untitled
--------

.. raw:: html

   <form>
     Username: <input type="text" size=16 /><br/>
     Secret password: <input type="password" size=16 /><br/>
     Repeat password: <input type="password" size=16 /><br/>
     <input type="submit" name="Create Account" />
   </form>

untitled
--------

| This form contains
| a static series of fields

| What if we needed to add
| some dynamic ones?

untitled
--------

>>> get_questions(request1)
'How long have you been a lawyer?'
'Do you play one on TV?'

>>> get_questions(request2)
'Have you used our products before?'

>>> get_questions(request3)
'Is this your first PyCon?'
'Are you signed up for the Hallway Track?'
'Where are the couches?'

untitled
--------

.. raw:: html

   <form>
     Username: <input type="text" size=16 /><br/>
     Secret password: <input type="password" size=16 /><br/>
     Repeat password: <input type="password" size=16 /><br/>
     How long have you been a lawyer? <input type="text" size=3 /><br/>
     Do you play one on TV? <input type="text" size=3 /><br/>
     <input type="submit" name="Create Account" />
   </form>


A SqlA base class for FA and Sprox
----------------------------------

untitled
--------

::

    class User(DeclarativeBase):
        __tablename__ = 'users'

        user_name = Column(Unicode(16), unique=True,
                           primary_key=True)
        password = Column('password', Unicode(40))

FormAlchemy
-----------

untitled
--------

| First, we start with the User class
| and append a second password field

untitled
--------

::

    fs = FieldSet(User)
    fs.append(Field('password2').label('Repeat password'))

    def validate_password(value, field):
	if value != field.parent.password.value:
	    raise ValidationError('Passwords do not match')

    fs.email.set(validate=validate_password) 

untitled
--------

| To add the dynamic fields,
| we override simply use append again

untitled
--------

::

    fs = FieldSet(User)
    fs.append(Field('password2'))
    for i, question in enumerate(get_questions(request)):
	fs.append(Field('custom_%s' % i).label(question))

    def validate_password(value, field):
	if value != field.parent.password.value:
	    raise ValidationError('Passwords do not match')

    fs.email.set(validate=validate_password) 

Django
------

untitled
--------

| First, we build the static
| part of the form

untitled
--------

::

    class UserCreationForm(forms.Form):
        username = forms.CharField(max_length=30)
        password1 = forms.CharField(widget=forms.PasswordInput)
        password2 = forms.CharField(widget=forms.PasswordInput)

        def clean_password2(self):
            password1 = self.cleaned_data.get("password1", "")
            password2 = self.cleaned_data["password2"]
            if password1 != password2:
                raise forms.ValidationError(
                    "The password fields don't match."
                    )
            return password2


untitled
--------

| To add the dynamic fields,
| we override __init__() and add those
| fields to every instance

untitled
--------

::

    class UserCreationForm(forms.Form):
        username = forms.CharField(max_length=30)
        password1 = forms.CharField(widget=forms.PasswordInput)
        password2 = forms.CharField(widget=forms.PasswordInput)

        def __init__(self, *args, **kwargs):
            extra = kwargs.pop('extra')
            super(UserCreationForm, self).__init__(
                *args, **kwargs)
            
            for i, question in enumerate(extra):
                self.fields['custom_%s' % i] = \
                    forms.CharField(label=question)

untitled
--------

(Need to add more here after reading the example more carefully
after my tutorial)

formish
-------

untitled
--------

::

    class Registration(schemaish.Structure):
        username = schemaish.String(
            validator=validatish.Required())
        password = schemaish.String(
            validator=validatish.Required())
    
    def get_form(request):
        schema = Registration()
        for q in get_questions(request):
            schema.add(q, schemaish.String(
                validator=validatish.Required()))
        form = formish.Form(schema)
        form['password'].widget = formish.CheckedPassword()
        return form


Sprox
-----

untitled
--------

::

    from sprox.formbase import EditableForm
    from formencode import Schema
    from formencode.validators import FieldsMatch
    from tw.forms import PasswordField, TextField

    form_validator =  Schema(chained_validators=(FieldsMatch(
            'password',
            'verify_password',
            messages={'invalidNoMatch':
            'Passwords do not match'}),
        ))
    class UserForm(EditableForm):
        __model__ = User
        __field_order__ = ['user_name', 'password', 'repeat_pw']
        __require_fields__ = ['password', 'user_name']
        __base_validator__ = form_validator
        repeat_password = PasswordField('repeat_password')

    user_form = RegistrationForm(DBSession)

untitled
--------

::

    from tg import request
    from formencode.validators import String

    class UserForm(EditableForm):
        __model__ = User
        __field_order__        = ['user_name', 'password',
                                  'repeat_password']
        __require_fields__     = ['password', 'user_name']
        __base_validator__     = form_validator
        repeat_password        = PasswordField('repeat_password')

        def _do_get_fields(self):
            fields = super(UserForm, self)._do_get_fields()
            questions = get_questions(request)
            for i, question in enumerate(questions):
                fields.append(TextField('extra_field_%s'%i,
                    text_label=question,
                    validator=String(not_empty=True)))
            return fields

untitled
--------

Time for questions from the floor!

| Jonathan Ellis — FormAlchemy
| Jacob Kaplan-Moss — Django
| Chris McDonough — formish
| Christopher Perkins — Sprox
