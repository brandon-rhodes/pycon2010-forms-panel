import random

from restish import resource, http, templating
import formish, schemaish, validatish

questions = random.sample(['where?','when?','why?','what?','who?','how?'],3)

def get_questions(request):
    return questions

def save_answer(request, question_text, answer_text):
    print '%s: %s'%(question_text, answer_text)

def get_form(request):
    schema = schemaish.Structure()
    schema.add( 'username', schemaish.String() )
    schema.add( 'password', schemaish.String() )
    for q in get_questions(request):
        schema.add( q, schemaish.String( validator=validatish.Required() ))
    form = formish.Form(schema)
    form['password'].widget = formish.CheckedPassword()
    return form



class Root(resource.Resource):


    @resource.GET()
    def get(self, request):
        return self.html(request)

    @templating.page('home.html')
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

    
    @resource.child('styles.css')
    def styles(self, request, segments):
        css = open('pycon/public/styles.css').read()
        return http.ok([('Content-Type', 'text/css')], css )

class Thanks(resource.Resource):

    @resource.GET()
    @templating.page('thanks.html')
    def get(self, request):
        return {}


