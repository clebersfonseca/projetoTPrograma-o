from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers
import pandas as pd
import os
from dadosServidores import settings

dt = pd.read_csv(os.path.join(settings.BASE_DIR, 'dados/20171231_Remuneracao.csv'), encoding='ISO-8859-1', delimiter="\t")
dp = pd.read_csv(os.path.join(settings.BASE_DIR, 'dados/20171231_Cadastro.csv'), encoding='ISO-8859-1', delimiter="\t")

dt = dt.rename(columns={"REMUNERAÇÃO BÁSICA BRUTA (R$)":"bruta"})
dt.bruta = dt.bruta.str.replace(',', '.')
dt.bruta = dt.bruta.astype(float)

dp.drop_duplicates('Id_SERVIDOR_PORTAL', 'last')

dados = dt.set_index('ID_SERVIDOR_PORTAL').join(dp.set_index('Id_SERVIDOR_PORTAL'), lsuffix='_sal', rsuffix='_serv')
dados = dados.groupby(['DESCRICAO_CARGO']).mean().reset_index()

desc = dados['DESCRICAO_CARGO'].values
sal = dados['bruta'].values


def home(request):



    return render(request, 'index.html')


@csrf_exempt
def busca(request):

    s = request.POST.get('salario')
    s = float(s)
    print(s)
    p = request.POST.get('profissao')
    print(type(p))
    i = 0
    lista = {}
    count = 0
    while i < len(desc):
        if (s == "" or s == 0) and p != "":
            if (desc[i] == p.upper()):
                lista[count] = {}
                lista[count]["cargo"] = desc[i].lower()
                lista[count]["salario"] = sal[i]
                count += 1
                print("Profissão")
        elif p == "" and (s != "" and s != 0):
            if ((sal[i] < (float(s) + 500)) and (sal[i] > (float(s) - 500))):
                lista[count] = {}
                lista[count]["cargo"] = desc[i].lower()
                lista[count]["salario"] = sal[i]
                count += 1
                print("Salario")
        elif p != "" and s != "" and s != 0:
            if (desc[i] == p.upper()) or ((sal[i] < (float(s) + 500)) and (sal[i] > (float(s) - 500))):
                lista[count] = {}
                lista[count]["cargo"] = desc[i].lower()
                lista[count]["salario"] = sal[i]
                count += 1
                print("Os dois")

        if count == 10:
            break
        i += 1

    re = {"data": lista, "length": count}

    re = json.dumps(re, sort_keys=False, separators=(',', ':'))

    return JsonResponse(re, safe=False)

@csrf_exempt
def buscaprofissao(request):
    prof = request.POST.get('profissao')
    list = []
    for a in desc:
        if a.startswith(str(prof).upper()):
            list.append(a.lower())
    re = json.dumps(list, sort_keys=True, separators=(',', ':'))
    return JsonResponse(re, safe=False)