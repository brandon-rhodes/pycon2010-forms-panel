Formish
=======

Formish is a form generation library written by Tim Parkin and Matt
Goodall (a.k.a. "the 'ish' guys").

It relies on:

- `WebOb <http://pythonpaste.org>`_, a WSGI library which implements
  request and response objects.

- `schemaish <http://ish.io/projects/show/schemaish>`_, a Python
  package to define data schemas.

- `validatish <http://ish.io/projects/show/validatish>`_, a standalone
  validation package with functional validators and configurable class
  based validators.

- `convertish <http://ish.io/projects/show/convertish>`_, a conversion
  library to cast different types using adaption. Implementation has
  schemaish examples and most examples are for string conversion. Used
  in formish.

- The `Mako <http://makotemplates.org>`_ templating library.

In Tim's words:

   The main reason for writing formish was to properly separate
   schema from presentation. Too many form libraries at the time had
   the two combined together, so you would just have a type system
   where TextArea and Input were two different types. We wanted a
   simple separate of schema and interface so that a data structure
   could be created as a schema which could be displayed with default
   widgets but where each widget could then be customised without
   having to worry about data changing.

Formish supplies a good number of `prechewed widget implementations
<http://ish.io:8891/>`_ out of the box, including widgets for core
data types like integer, boolean, float, etc. as well as file uploads,
checked passwords, multiselect widgets, and so on.  Sequences of
widgets can be treated as independent entities, which makes it
possible to create highly complex nested forms.

Here are some of Formish's features:

- Formish is really just a library; its only effective requirement is
  that it be fed a request object which implements the WebOb request
  interface.  This means that it is useful out of the box under
  multiple web frameworks such as Pylons, restish, and repoze.bfg
  (each of which uses WebOb).  This makes your knowledge about formish
  potentially more "portable" than your knowledge about other form
  generation systems.

- Reasonable factoring.  The boundaries between form generation,
  schema construction and validation are very clear (maybe
  too-forcibly clear): ``formish`` handles form generation,
  ``schemaish`` handles schema construction, ``validatish`` contains
  helpers for validation purposes.  The benefit of these boundaries
  isn't universal; most application developers are happy to import
  stuff from wherever they're told to by the authors of a web
  framework.  But the explicit separation tends to be a bonus for
  *framework* authors who wish to integrate formish, because it makes
  each part of the system more approachable and transparent.

- Formish widgets don't conflate serialization and deserialization
  with type conversion.  Formish widgets do largely symmetric
  ``from_request_data`` and ``to_request_data`` conversions as a step
  separate from schema type coercion.

- Formish doesn't conflate type conversion with data validation.
  Schema attributes may use validators which are usable against more
  than one data type.

- Formish doesn't concern itself with representing *data* schemas,
  just *form* schemas.  The schemas you create when using formish are
  unrelated to your model data.  This is both a weakness and a
  strength.  It's a weakness if each of your model's attributes maps
  one-to-one field-wise to a form element and your persistence
  mechanism never changes between projects.  It's a strength if you
  use different persistence mechanisms per project, or if your form
  elements don't map naturally to your model data.

- Schemas can created declaratively::

    class MySchema(schemaish.Structure):
        name = schemaish.String()
        age = schemaish.Integer()

  Or imperatively::

    myschema = schemaish.Structure()
    myschema.add('name', schemaish.String())
    myschema.add('age', schemaish.Integer())

- Custom widgets are reasonably easy to create.

- Hooks exist to replace the templating language used for widgets;
  Mako is the default language.  I've reimplemented all the core
  widgets using `Chameleon <http://chameleon.repoze.org>`_ as well for
  my own purposes in a project called ``repoze.bfg.formish``.

Example 1: Static Schema Under Restish
--------------------------------------

Here's the code that implements the requirement for a registration
form which contains only "static" schema data (username and password)
using the Restish web framework:

.. literalinclude:: retish/static.py

Here's the ``register.mak`` template that renders the form:

.. literalinclude:: retish/register.mak

Points of note:

- A *schema definition* is defined declaratively as the
  ``Registration`` class.  It contains a username and a password.

- A *schema instance* and a *form* are created for each request (via
  ``get_form``).

- A *widget* is associated with one of the form's fields
  (``password``) imperatively.  As a result, when the form is
  rendererd, the password widget will now be a widget which contains
  two text inputs: one which asks for a password and one which asks
  for a password confirmation.

- We only process the form if the request was submitted with ``POST``.

- Calling ``form.validate`` either succeeds or raises a
  ``formish.FormError`` exception.  If it succeeds, the data submitted
  by the user is valid.  If it raises the exception, as a result of
  validation, the form object now contains enough information to
  display useful error messages (such as missing elements) and the
  form is redisplayed.

- The ``register.mak`` template used to render the form is extremely
  simple: it calls the ``__call__`` of the ``form`` object.
      
Example 2: Dynamic Schema Under Restish
---------------------------------------

Here's the code that implements the requirement for a registration
form which contains dynamic schema data (marketing questions).  It's
an extension of the application which asked for static data.

.. literalinclude:: retish/dynamic.py

Points of note:

- The ``register.mak`` template that renders the form is unchanged.

- We can dynamically add schema items to a schema instance via
  the ``schema.add`` method.

- Everything else is about the same.

Example 3: Dynamic Schema Under BFG
-----------------------------------

Here's the code that implements the requirement for a registration
form which contains dynamic schema data (marketing questions).  It's
an extension of the application which asked for static data.

.. literalinclude:: bfg/dynamic.py

Here's the ``register.pt`` template that renders the form:

.. literalinclude:: bfg/register.pt

Notable points:

- We've used an entirely different web framework, but the patterns
  remain the same.


