from django.shortcuts import render, redirect
from .models import Apostila, Tags, ViewApostila
from django.contrib.messages import constants
from django.contrib import messages

def adicionar_apostilas(request):
    if request.method == 'GET':
        apostilas = Apostila.objects.filter(user=request.user)
        views_totais = ViewApostila.objects.filter(apostila__user = request.user).count()
        return render(request, 'adicionar_apostilas.html', {'apostilas': apostilas, 'views_totais': views_totais})
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.FILES['arquivo']

        apostila = Apostila(user=request.user, titulo=titulo, arquivo=arquivo)
        apostila.save()
        
        tags = request.POST.get('tags')
        list_tags = tags.split(',')
        
        for tag in list_tags:
            nova_tag = Tags(name=tag)
            nova_tag.save()
            apostila.tags.add(nova_tag)
        
        apostila.save()
        
        messages.add_message(
            request, constants.SUCCESS, 'Apostila adicionada com sucesso.'
        )
        return redirect('/apostilas/adicionar_apostilas/')

def apostila(request, id):
    apostila = Apostila.objects.get(id=id)
    view = ViewApostila(
        ip=request.META['REMOTE_ADDR'],
        apostila=apostila
    )
    view.save()
    views_unicas = ViewApostila.objects.filter(apostila=apostila).values('ip').distinct().count()
    views_totais = ViewApostila.objects.filter(apostila=apostila).count()
    return render(request, 'apostila.html', {'apostila': apostila, 'views_unicas': views_unicas, 'views_totais': views_totais})    