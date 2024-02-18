from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, FlashcardDesafio, Desafio
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages

def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards= Flashcard.objects.filter(user=request.user)
        
        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')
        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)
        return render(request, 'novo_flashcard.html', {'categorias': categorias, 'dificuldades': dificuldades, 'flashcards': flashcards})

    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')
        
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(
                request,
                constants.ERROR,
                'Preencha os campos de pergunta e resposta',
            )
            return redirect('/flashcard/novo_flashcard')
        
        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        )
        
        flashcard.save()
        
        messages.add_message(request, constants.SUCCESS, 'Flashcard criado com sucesso')
        return redirect('/flashcard/novo_flashcard')

def deletar_flashcard(request, id):
    flashcard = Flashcard.objects.get(id=id)
    if flashcard.user != request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para excluir este flashcard.')
        return redirect('/flashcard/novo_flashcard')
    
    flashcard.delete()
    messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso!')
    return redirect('/flashcard/novo_flashcard')

def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(
            request,
            'iniciar_desafio.html',
            {'categorias': categorias, 'dificuldades': dificuldades},
        )
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')
        
        # Verificar se a quantidade de perguntas é maior do que a quantidade disponível
        flashcards_disponiveis = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria__id__in=categorias)
        )
        quantidade_existente = flashcards_disponiveis.count()
        if quantidade_existente < int(qtd_perguntas):
            mensagem = (
                f'A quantidade máxima para a categoria e dificuldade escolhidas é de {quantidade_existente} '
                'por favor, escolha uma quantidade igual ou inferior a essa quantidade.'
            )
            messages.add_message(request, messages.ERROR, mensagem)
            return redirect('/flashcard/iniciar_desafio/')
        
        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade,
        )
        desafio.save()
        
        desafio.categoria.add(*categorias)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio/')

        flashcards = flashcards[: int(qtd_perguntas)]
        
        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/desafio/{desafio.id}')

def listar_desafio(request):
    if request.method == 'GET':
        desafios = Desafio.objects.filter(user=request.user)
        categorias = Categoria.objects.filter(desafio__in=desafios).distinct()
        dificuldades = Flashcard.DIFICULDADE_CHOICES

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')
        if categoria_filtrar:
            desafios = desafios.filter(categoria__id=categoria_filtrar)
            
        if dificuldade_filtrar:
            desafios = desafios.filter(dificuldade=dificuldade_filtrar)
        return render(request,'listar_desafio.html',{'desafios': desafios,'categorias': categorias,'dificuldades': dificuldades},)
    
def desafio(request, id):
    desafio = Desafio.objects.get(id=id)
    if not desafio.user == request.user:
        raise Http404

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        
        categorias = desafio.flashcards.all().values_list('flashcard__categoria__nome', flat=True).distinct()
        
        return render(
            request,
            'desafio.html',
            {
                'acertos': acertos,
                'erros': erros,
                'faltantes': faltantes,
                'desafio': desafio,
                'categorias': categorias,
            },
        )

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)
    flashcards_desafio = desafio.flashcards.all().values_list('flashcard__categoria', flat=True)
    categorias = Categoria.objects.filter(id__in=flashcards_desafio).distinct()

    acertos = desafio.flashcards.filter(respondido=True, acertou=True).count()
    erros = desafio.flashcards.filter(respondido=True, acertou=False).count()

    dados = [acertos, erros]

    name_categoria = [i.nome for i in categorias]

    dados2 = []
    dados3 = []
    for categoria in categorias:
        acertos_categoria = desafio.flashcards.filter(flashcard__categoria=categoria, acertou=True).count()
        erros_categoria = desafio.flashcards.filter(flashcard__categoria=categoria, respondido=True, acertou=False).count()
        dados2.append(acertos_categoria)
        dados3.append(erros_categoria)

    dados_categorias = list(zip(name_categoria, dados2, dados3))

    melhores_categorias = []
    piores_categorias = []
    for categoria, acertos, erros in dados_categorias:
        if acertos > erros:
            melhores_categorias.append((categoria, acertos, erros))
        elif erros >= acertos:
            piores_categorias.append((categoria, acertos, erros))

    return render(request, 'relatorio.html', {
        'desafio': desafio,
        'dados': dados,
        'categorias': name_categoria,
        'dados2': dados2,
        'dados3': dados3,
        'dados_categorias': dados_categorias,
        'melhores_categorias': melhores_categorias,
        'piores_categorias': piores_categorias,
    })