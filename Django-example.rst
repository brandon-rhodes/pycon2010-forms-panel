Round 1
=======

Before we start, let's talk -- real briefly -- about the parts you need to
display and process a form in Django. You'll need:

    * A form class. This'll be a subclass of ``django.forms.Form``, and will
      contain all the display and validation logic for the form.
      
    * A view function. This'll be responsible for connecting the form to the
      submitted data, rendering the form into a template, etc.
      
    * (Usually) a template used to render the form and the rest of the page.

Part 1
------

The first part of this assignment -- username / password / repeat password -- is
very easily solved: just install James Bennett's `django-registration`__ and go
out for beer.

__ http://docs.b-list.org/django-registration/0.8/

Snark aside, this illustrates one of the best aspects of Django: there's an
incredibly active community producing reusable apps, so when you're faced with a
problem in Django there's a good chance that "there's an app for that." In the
real world, in fact, I'd use django-registration for this entire round.

However, to keep things simple, I'll stick to what's built into Django.

The form
~~~~~~~~

Very simple::

    from django.contrib.auth.forms import UserCreationForm
    
That's right: Django ships with a form that handles this common
user/password/confirm task perfectly. For pedagogical purposes, though, I'll
show how you'd actually define this form by hand if you cared to::

    from django import forms

    class UserCreationForm(forms.Form):
        username = forms.CharField(max_length=30)
        password1 = forms.CharField(widget=forms.PasswordInput)
        password2 = forms.CharField(widget=forms.PasswordInput)

        def clean_password2(self):
            password1 = self.cleaned_data.get("password1", "")
            password2 = self.cleaned_data["password2"]
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match."))
            return password2

The salient features here:

    * The form is a subclass of ``forms.Form``.
    
    * A form includes a number of fields. Django's got a bunch of `built-in
      fields`__ for common types (characters, dates/times, file uploads, etc.),
      and it's easy to `create custom field types`__.

    * Each field has an associated "widget" which defines how to render the form
      field. Django's HTML-focused, and as such ships with `built-in widgets`__
      for all the HTML input types. Again, it's easy to write your own widgets,
      and since there's nothing HTML-specific until you reach the widget layer
      it'd be easy to use the forms framework on top of something else like
      XForms.

    * Here, all the fields use ``CharField``, but the password fields get
      rendered as ``<input type=password>`` by using a ``PasswordInput``.
      
    * Fields generally know how to validate and clean (convert from strings to
      proper types) themselves. So an ``IntegerField`` will automatically
      coerece strings on the wire into integers.
      
    * Here, we need some extra validation -- we want to check that ``password2``
      matches ``password1``. For the purpose, we can define a custom clean
      method. We provide a clean method by defining a method on the form called
      ``clean_<fieldname>``.
      
    * By the time our ``clean_password`` method gets called, the fields' clean
      methods have already been called, which has put cleaned and validated data
      into ``self.cleaned_data``. 
      
      However, we need to guard against ``password1`` not having been provided:
      fields are required by default, but ``cleaned_data`` only contains data
      that's passed validation, so if ``password1`` wasn't given, it won't
      be in ``cleaned_data``. For similar reasons, ``clean_password2`` will only
      be called if something's been entered in the field.
      
    * Clean functions do two things: 
        
        * Validate data, raising ``forms.ValidationError`` if the data's not
          valid.
        
        * Clean -- coerce, modify, or otherwise munge -- the data.
        
      They'll pull the old data out of ``self.cleaned_data``, and return
      the new, cleaned and validated data.
      
    * There are also various hooks for form-wide validation which aren't needed
      here.

__ http://docs.djangoproject.com/en/dev/ref/forms/fields/
__ http://docs.djangoproject.com/en/dev/ref/forms/fields/#creating-custom-fields
__ http://docs.djangoproject.com/en/dev/ref/forms/widgets/

The view
~~~~~~~~

Now that we've got a form, we need a view function to present that form. Views
and how they're wired up are out of scope for this discussion, so I won't cover
them in detail. Instead, I'll just look at how they apply to form processing.

So here's our view::

    from django.shortcuts import redirect, render_to_response
    from myapp.forms import UserCreationForm

    def create_user(request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                do_something_with(form.cleaned_data)
                return redirect("create_user_success")
        else:
            form = UserCreationForm()
            
        return render_to_response("signup/form.html", {'form': form})

Salient details:

    * To be a good HTTP citizen, we only process the form if the request was
      submitted with ``POST``.
      
    * If the request was a ``POST``, we'll create a *bound form* -- a form
      *bound* to some associated data -- by passing in ``request.POST``.
      
    * ``request.POST`` is essentially a ``dict``, and forms will operate
      on any ``dict``-like structure. I mention this to point out that
      though forms are usually used with HTML/HTTP, they can also be used
      with lots of other data sources.
      
      For example, Piston__, a REST API framework, uses Django's forms to
      validate data submitted via an API in JSON, YAML, XML, etc.
      
    * Calling ``form.is_valid()`` kicks off all the data cleaning and
      validation.
      
    * If it returns ``True`` then all the validation succeeded. At this
      point we can do something with our submitted data -- usually by
      reading ``form.cleaned_data``.
      
    * Again, to be a good Web citizen, we'll follow the common
      `Post/Redirect/Get`__ pattern upon success.
      
    * If the form *wasn't* valid, we'll fall through returning a response. The
      form instance, however, will have an ``errors`` attribute containing all
      the errors that prevented it from being valid.
      
    * If the request wasn't a ``POST``, we'll construct an *unbound form*. This
      form will have no associated data, and hence will have no errors.

    * Finally, we'll render a template -- ``signup/form.html`` -- and pass in
      the form instance to be rendered.
    
__ http://bitbucket.org/jespern/django-piston/wiki/Home
__ http://en.wikipedia.org/wiki/Post/Redirect/Get

For advanced users, there's a slightly shorter and more idiomatic way to write
this view::

    def create_user(request):
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            do_something_with(form.cleaned_data)
            return redirect("create_user_success")
            
        return render_to_response("signup/form.html", {'form': form})

Exactly how and why this works is left as an exercise to the reader. Hint:
recall that ``request.POST`` will only have ``POST``-ed data in it...

The template
~~~~~~~~~~~~

Again, templates are out of scope, so I'll just look at how they'd touch on form
rendering.

At its simplest, a the ``signup/form.html`` template would be very simple
indeed::

    <form method="POST" action=".">
      {{ form }}
      <input type=submit>
    </form>

Forms know how to render themselves into HTML with relatively simple markup.
This does quite a lot, though: it'll render the form, filling in any
pre-existing data if the form was bound, and will also render associated error
messages.

Notice that the form *doesn't* render the surrounding ``<form>`` tag, nor does
it render the ``<ipnut type=submit>``. This is by design: you could, for
example, compose multiple forms into a single ``<form>``, or you could be
rendering this form into something that's not HTML.

There are a couple of other shortcuts to rendering forms in a few common ways:
``{{ form.as_p }}``, ``{{ form.as_table }}``, ``{{ form.as_ul }}``. For maximum
control, you can render each field separately, or even write the form completely
by hand. For details, consult the `form documentation`__

__ http://docs.djangoproject.com/en/dev/topics/forms/#displaying-a-form-using-a-template

Part 2
------

Okay, let's kick it up a notch. The second part of this problem involves adding
custom registration questions for each person. We'll need to integrate these
custom question into the form.

Note that the template wouldn't need to be changed at all, so we'll skip it
entirely in this section.

The view
~~~~~~~~

We'll actually start by looking at the view, since it'll need a couple of
minor tweaks to handle the new form:

.. parsed-literal::

    def create_user(request):
        **extra_questions = get_questions(request)
        form = UserCreationForm(request.POST or None, extra=extra_questions)**
        if form.is_valid():
            **for (question, answer) in form.extra_answers():
                save_answer(request, question, answer)**
            return redirect("create_user_success")
            
        return render_to_response("signup/form.html", {'form': form})

You'll notice that the general structure of the form processing is intact. This
is typical: form views almost always follow this idiomatic style. So what's
different here?

    * We're gathering a list of extra questions from this hypothetical
      ``get_questions(request)`` function, and then feeding them into the form
      class.
      
    * If the form is valid, we're calling ``form.extra_answers()`` and using the
      returned data to save those answers.

I'll look at how to make the associated changes to the form in a second, but
first a brief philosophical digression. In essence, we've pushed the handling of
the questions and the validation of their answers down into the form class
itself, but we've left the parts of the problem that deal with the request
object in the view. This is the idiomatic way of tackling the problem: if we handed
the request object to the form directly we'd be cutting against the grain of Django's
form library, which doesn't want to be tied to HTTP directly.

The form
~~~~~~~~

After writing the view, it's clear we need to modify our form in a couple of ways:

    * We'll need to change the ``__init__`` signature to accept this list of
      extra questions, and we'll need to modify the form's fields accordingly.
      
    * We'll need to add an extra ``extra_answers()`` function that returns
      ``(question, answer)`` pairs.
      
Let's look at ``__init__`` first:

.. parsed-literal::

    class UserCreationForm(forms.Form):
        username = forms.CharField(max_length=30)
        password1 = forms.CharField(widget=forms.PasswordInput)
        password2 = forms.CharField(widget=forms.PasswordInput)

        **def __init__(self, *args, **kwargs):
            extra = kwargs.pop('extra')
            super(UserCreationForm, self).__init__(*args, **kwargs)
            
            for i, question in enumerate(extra):
                self.fields['custom_%s' % i] = forms.CharField(label=question)**
            
So what'd we do here?

    * We pulled the ``extra`` keyword argument out of ``**kwargs`` and then
      called the superclass initializer. In practice, we'd probably want
      some error checking to make sure ``extra`` was given.
      
    * We then looped over the extra questions and added them to ``self.fields``.
    
    * ``self.fields`` is a dict mapping field identifiers -- input names,
      essentially -- to ``Field`` instances. Normally, we define these
      declaratively (as we still do for ``username``, ``password1``, and
      ``password2``). Since we're dealing with dynamic data here, though we
      can't define them declaratively, so we can simple add new fields to
      ``self.fields``.
      
    * We're arbitrarily naming the fields ``custom_0``, ``custom_1``, etc. since
      we've been informed that ``get_questions`` is stable. If it wasn't, we
      might need to do something like hash the question text.
      
    * By default, the label for the field will be the same as the field's
      identifier. Since "Custom 1: _____" doesn't make for very good UX, we've
      passed the question text itself in as the field's ``label`` argument,
      which will render by default as an associated ``<label>`` tag.
      
    * Fields are required by default, so we fulfill that part of the assignment
      without any custom validation. If they were to be optional we could pass
      ``required=False`` in to the field's constructor.
      
That was the tricky part; the ``extra_answers()`` function is easy:

.. parsed-literal::

    class UserCreationForm(forms.Form):
        ...
        
        **def extra_answers(self):
            for name, value in self.cleaned_data.items():
                if name.startswith('custom_'):
                    yield (self.fields[name].label, value)**

We simply loop over ``self.cleaned_data``, yielding any pairs for fields
starting with ``custom_``. The only slightly tricky bit is that we need to pull
the original question back out of the ``label`` value by accessing
``self.fields[name].label``.