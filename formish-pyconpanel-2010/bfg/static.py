from repoze.bfg.configuration import Configurator

from webob.exc import HTTPFound

import schemaish
import formish
import validatish

class Registration(schemaish.Structure):
    username = schemaish.String(validator=validatish.Required())
    password = schemaish.String(validator=validatish.Required())

def get_form(request):
    schema = Registration()
    form = formish.Form(schema)
    form['password'].widget = formish.CheckedPassword()
    return form

def display_form(request):
    form = get_form(request)
    return {'form':form}

def validate_form(request):
    form = get_form(request)
    try:
        data = form.validate(request)
    except formish.FormError:
        return {'form':form}
    username, password = data['username'], data['password']
    return HTTPFound(location='thanks')

if __name__ == '__main__':
    from paste.httpserver import serve
    config = Configurator()
    config.begin()
    config.add_view(display_form, request_method='GET', renderer='register.pt')
    config.add_view(validate_form, request_method='POST',renderer='register.pt')
    config.add_view(name='thanks', renderer='thanks.pt')
    config.end()
    app = config.make_wsgi_app()
    serve(app)
    
