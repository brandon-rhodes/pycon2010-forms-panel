def page(request):
    fs = FieldSet(Basic)
    questions = [(normalize_name(q), q) in get_questions(request)]
    for name, label in questions :
        fs.append(Field(name, label=label))

    fs = fs.bind(data=request.POST or None)
    if request.POST and fs.validate():
        fs.sync()
        for name, label in questions:
            field = fs[name]
            save_question(request, label, field.value)
        redirect('/')
    return '<form>%s<input type="submit" /></form>' % fs.render()
