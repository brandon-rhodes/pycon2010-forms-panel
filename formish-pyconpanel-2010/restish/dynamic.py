from restish import app
from restish import templating
from restish.contrib.makorenderer import MakoRenderer

from restish import resource
from restish import http

import formish
import schemaish
import validatish

questions = [
    'Where did you hear about this site?',
    'What college did you attend?',
    'What year did you graduate?',
    ]

def get_questions(request):
    return questions

def save_answer(request, question_text, answer_text):
    pass

class Registration(schemaish.Structure):
    username = schemaish.String(validator=validatish.Required())
    password = schemaish.String(validator=validatish.Required())

def get_form(request):
    schema = Registration()
    for q in get_questions(request):
        schema.add(q, schemaish.String(validator=validatish.Required()))
    form = formish.Form(schema)
    form['password'].widget = formish.CheckedPassword()
    return form

class Root(resource.Resource):
    @resource.GET()
    def get(self, request):
        return self.html(request)

    @templating.page('register.mak')
    def html(self, request, form=None):
        if form is None:
            form = get_form(request)
        return {'form': form}

    @resource.POST()
    def post(self, request):
        form = get_form(request)
        try:
            data = form.validate(request)
        except formish.FormError:
            return self.html(request, form)

        data.pop('username')
        data.pop('password')
        for k,v in data.items():
            save_answer(request, k, v)
        return http.see_other('/thanks')

    @resource.child('thanks')
    def thanks(self, request, segments):
        return Thanks()

class Thanks(resource.Resource):

    @resource.GET()
    @templating.page('thanks.mak')
    def get(self, request):
        return {}

def make_renderer():
    return MakoRenderer(
            directories=['.'],
            input_encoding='utf-8', output_encoding='utf-8',
            default_filters=['unicode', 'h']
            )

def application(environ, start_response):
    renderer = make_renderer()
    environ['restish.templating'] = templating.Templating(renderer)
    return app.RestishApp(Root())(environ, start_response)

if __name__ == '__main__':
    from paste.httpserver import serve
    serve(application)

