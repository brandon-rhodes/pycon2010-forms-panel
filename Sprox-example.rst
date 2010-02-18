Sprox
=================================

First off, you must note that Sprox works by introspecting your database schema to build forms.
However, it is still customizable, and you can therefore override or add fields to your form as
necessary

Example Schema
---------------

Since Sprox utilizes sqlalchemy mappings to determine the form, consider this schema::

    class User(DeclarativeBase):
        __tablename__ = 'users'

        user_name = Column(Unicode(16), unique=True, primary_key=True)
        password = Column('password', Unicode(40))


The Simplest Form
--------------------
Sprox has a simple but powerful way to generate forms.
Here is the simplest way to create a form based on a "User" class.::

    from sprox.formbase import EditableForm

    class UserForm(EditableForm):
        __model__ = User

    user_form = UserForm(DBSession)

That form can then be passed into a template, just like if it were a regular ToscaWidgets form.  But
you ask, "Why do you need to pass in the DBSession?"  Well, in fact the session is not required to be passed in,
but if you want Sprox to pick up the data for the drop-down menus, and multiple select fields, it needs a way
to connect to the database in order to get the appropriate data.

Add in that password check
----------------------------

You might say, "Ok, but that form gives me a lot of junk I don't want, and the password field is going to have to be verified
if we wanted to say, make a registration form."  Well, remember Sprox is fully customizable.  Here is an example registration
form based on Sprox, complete with password validation.::

    from sprox.formbase import EditableForm
    from formencode import Schema
    from formencode.validators import FieldsMatch
    from tw.forms import PasswordField, TextField

    form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                             'verify_password',
                                                             messages={'invalidNoMatch':
                                                             'Passwords do not match'}),))
    class UserForm(EditableForm):
        __model__ = User
        __field_order__        = ['user_name', 'password', 'repeat_password']
        __require_fields__     = ['password', 'user_name']
        __base_validator__     = form_validator
        repeat_password        = PasswordField('repeat_password')

    user_form = RegistrationForm(DBSession)

Notice first that we have made three fields required set the order, and omitted the fields that
we do not want in the form.  Also, we overrode the widget type for email_address and display_name (The default
was a text area).  Lastly we add a repeat_password field that is not in the current schema.  Also keep in mind that
if you were to alter the schema for your database, any fields you added to your User model would also be added to this form.
There are many other __modifiers__ for FormBase in Sprox, you can use them to generate the forms you desire in
any number of combinations.  For more information see :mod:`sprox.formbase` and :mod:`sprox.fillerbase`.

Keep in mind that Sprox allows you to override an field in the form without any special method calls.  Rather
it uses declarative definition to change the behavior of the form, including the validators.  To override the
username form, you might do something like::

    class MyTextField(TextField):
       """special case here"""

    class UserForm(EditableForm):
        __model__ = User
        user_name = MyTextField

You can pass in a widget instance, or a type, Sprox will do the right thing.  The same kind of modification is
available for validation, but keep in mind that Sprox will determine proper validators for your forms based on the
attributes of the column schemas.


Table Generation
-----------------------
Most people look for things that render forms, but fail to realize that generating tabular formed data provides
almost the same challenge.  After all, in an editable form, you must retrieve the data from the database in order
to fill in the form entries.  Well, Sprox makes this easy too.  Here is some code to list out the users and their
email addresses::

    from sprox.tablebase import TableBase
    from sprox.fillerbase import TableFiller

    class UserTable(TableBase):
        __model__ = User

    user_table = UserTable(DBSession)

    class UserTableFiller(TableFiller):
        __model__ = User

    user_table_value = UserTableFiller(DBSession).get_value()


And your template code would look like this::

    ${user_table_form(value=user_table_value)}

Dynamic Forms
--------------

You may decide that the form fields you are generating need to be added to the form dynamically.  To do this, you want
to override the _do_get_fields method in your Sprox class.  Here is the given example::

    Now, someone from Marketing comes along and announces that the
    developers must add some additional questions to the form - and the
    number of extra questions is not determined until runtime!  They
    give you a get_questions(request) function that looks up a profile
    they cook up for each person browsing the site, and returns a list
    of strings like one of these:

      ['Where did you hear about this site?']
      ['What college did you attend?', 'What year did you graduate?']
      ['What is the velocity of a swallow?', 'African or European?']

    They explain that they cannot limit how many questions might be
    returned; for simple users who are bumpkins, it might just be one
    or two, but could be many if the user sounds like a very
    interesting one.  Your form will, then, look something like this
    (in the case of the third datum above):

      New username:    __________
      Password:        __________
      Repeat password: __________
      What is the velocity of a swallow? _________
      African or European?               _________
          [Submit]

The answer here is to let sprox build the form fields the way it normally does, and then add your fields (with
validators afterwords::

    from tg import request
    from formencode.validators import String

    class UserForm(EditableForm):
        __model__ = User
        __field_order__        = ['user_name', 'password', 'repeat_password']
        __require_fields__     = ['password', 'user_name']
        __base_validator__     = form_validator
        repeat_password        = PasswordField('repeat_password')

        def _do_get_fields(self):
            fields = super(UserForm, self)._do_get_fields()
            questions = get_questions(request)
            for i, question in enumerate(questions):
                fields.append(TextField('extra_field_%s'%i, text_label=question, validator=String(not_empty=True)))
            return fields


The question then becomes, how do we go about saving the data in this form?  Here is the example provided::

    When you get the answers, you can save each one of them simply by
    calling:

      save_answer(request, question_text, answer_text)

    But each question must be answered; if the user fails to fill in
    one of the questions, then the form should be re-displayed with all
    of the data in place but with a note next to each un-answered
    question noting that it is a required field.  (Yes: you can assume
    that get_questions(request) for a particular session returns the
    same list of questions over and over again, so that's not a value
    you have to stash away to make the form appear consistent from one
    page load to the next!)


If you were using TurboGears2 2 for instance, your Controller code might look something like this::

    # sprox import and form omitted (See above)
    from myapp.lib.base import BaseController
    from tg import expose, validate, tmpl_context, request

    class UserController(BaseController):

        @expose('myapp.templates.index')
        def index(self, **kw):
            tmpl_context = UserForm(DBSession)
            return dict(value=kw)

        @expose()
        @validate(user_form, error_handler=index)
        def create(self, **kw):

            #create a new user from the form
            u = User(kw)
            DBSession.add(u)

            #save the extra fields
            for key, value in kw.iteritems():
                if key.startswith('extra_field'):
                    save_answer(request, getattr(user_field, key).label_text, value)

            return 'success!'

The nice thing about using Sprox is that it handles all the form validation for you, so you just tell it
what validators to use and it will re-display the form until it passes validation.  Sprox can be used in this
capacity with: Pylons, TurboGears, TurboGears2, BFG, Grok, and even Django if you load ToscaWidgets into the wsgi stack.

