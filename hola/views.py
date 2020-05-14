from django.http import HttpResponse
from django.template import Template, Context, loader
from django.shortcuts import render

def saludo(request):

    #doc = open("/web/templates/miplantilla.html")
    #plt = Template(doc.read())
    #doc.close()

    miloader = loader.get_template('miplantilla.html')

    #ctx = Context({"lista": ['hola','caracola']})
    render = miloader.render({"lista": ['hola','caracola']})
    return HttpResponse(render)

def saludo2(request):

    return render(request, 'miplantilla.html',{"lista": ['hola','saludo2']})
