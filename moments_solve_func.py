from xml.dom import xmlbuilder
import pandas as pd
import numpy as np
from math import pi
import re
import os
import sys


add_dir = ''
##add_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '/mtable/')
##sys.path.append(add_dir)



#Очистка строк с армированием
def clean_reinf_string (string):
    #Убираем двойные пробелы
    while '  ' in string:
        string = string.replace('  ', ' ')
    #Убираем пробелы между плюсами
    while ' +' in string:
        string = string.replace(' +', '+')
    #Убираем пробелы между плюсами
    while '+ ' in string:
        string = string.replace('+ ', '+')
    while ':' in string:
        string = string.replace(':', ' ')
    return string

#Удаление пустых строк из листа
def clean_empty_in_list(list):
    list_new = []
    for i in list:
        if i != '':
            list_new.append(i)
    return list_new

#Преобразование строки с армированием в лист
def string_area_to_list(string):
    string = clean_reinf_string(string)
    list_from_string = re.split(';|,| |\t', string)
    list_from_string = clean_empty_in_list(list_from_string)
    return list_from_string


#Линейная интерполяция по точкам
def linear_dia (x, dia_points):
    '''Линейная интерполяция по точкам.
    x - уровень деформации;
    dia_point - матрица диаграммы в формате (матрица из n строк и 2 столбцов) [[e1, s1], [ei, si], ... , [en, sn]],
    где si - напряжение, ei соответствующая данному напряжению деформация.
    Точки диаграммы должны быть отсортированы от минимальной (сжатие) до максимальной (растяжение) деформации'''
    def l_interp1(x1, y1, x2, y2, x):
        '''Функция линейной интерполяции в точке x между точками 1 и 2.
        x1, y1 = точка 1; x2, y2 = точка 2'''
        if (x2 - x1) != 0.0:
            return y1 + (x - x1) * ((y2 - y1)/(x2 - x1))
        else: return y1
    #Определяем максимальную и минимальную деформацию
    min_e, max_e = dia_points[0,0], dia_points[-1,0]
    #Создаем в памяти переменную для напряжения
    s = 0.0
    #Если деформации превышают предельные значения, возвращаем нулевое напряжение и секущий модуль
    if x<min_e or x>max_e: return 0.0
    #Иначе ищем ближайшую точку диаграммы, превышающую заданную деформацию
    else:
        idx = 1
        #Увеличиваем счетчик пока не дойдем до нужной точки
        while dia_points[idx, 0] < x: idx = idx + 1
        #После нахождения выводим линейную интерполяцию
        s = l_interp1(dia_points[idx-1, 0], dia_points[idx-1, 1], dia_points[idx, 0], dia_points[idx, 1], x)
    return s


#Импорт и чтение данных для бетона и арматуры
def read_data_for_concrete_and_reinf (ctype, rtype):
    #чтение файлов
    table_concretes_data = pd.read_excel(add_dir+'RC_data.xlsx', sheet_name="Concretes_SP63", header=[0])
    table_reinf_data = pd.read_excel(add_dir+'RC_data.xlsx', sheet_name="Reinforcement_SP63", header=[0])
    #Доступные классы бетона и арматуры
    available_concretes = table_concretes_data['Class'].to_list()
    available_reinf = table_reinf_data['Class'].to_list()
    #Данные для конктетного бетона
    selected_concrete_data = table_concretes_data.loc[table_concretes_data['Class'] == ctype]
    selected_concrete_data = selected_concrete_data.to_dict('records')[0]
    #Данные для конктетной арматуры
    selected_reinf_data =  table_reinf_data.loc[ table_reinf_data['Class'] == rtype]
    selected_reinf_data = selected_reinf_data.to_dict('records')[0]
    return selected_concrete_data, selected_reinf_data

#Данные по огнестойкости
def temperature_data(t):
    #Импорт данных из Excel
    table_temperatures_data = pd.read_excel(add_dir+'RC_data.xlsx', sheet_name="Temperatures_SP468", header=[0])
    fire_gammabt_data = np.array(table_temperatures_data.loc[:,['T','gammabt']].loc[table_temperatures_data['gammabt'].notna()].values.tolist())
    fire_gammabtt_data = np.array(table_temperatures_data.loc[:,['T','gammabtt']].loc[table_temperatures_data['gammabtt'].notna()].values.tolist())
    fire_bettab_data = np.array(table_temperatures_data.loc[:,['T','bettab']].loc[table_temperatures_data['bettab'].notna()].values.tolist())
    fire_eb0_data = np.array(table_temperatures_data.loc[:,['T','eb0']].loc[table_temperatures_data['eb0'].notna()].values.tolist())
    fire_eb2_data = np.array(table_temperatures_data.loc[:,['T','eb2']].loc[table_temperatures_data['eb2'].notna()].values.tolist())
    fire_eb1red_data = np.array(table_temperatures_data.loc[:,['T','eb1red']].loc[table_temperatures_data['eb1red'].notna()].values.tolist())
    fire_gammast1_data = np.array(table_temperatures_data.loc[:,['T','gammast1']].loc[table_temperatures_data['gammast1'].notna()].values.tolist())
    fire_gammast2_data = np.array(table_temperatures_data.loc[:,['T','gammast2']].loc[table_temperatures_data['gammast2'].notna()].values.tolist())
    fire_bettas1_data = np.array(table_temperatures_data.loc[:,['T','bettas1']].loc[table_temperatures_data['bettas1'].notna()].values.tolist())
    fire_bettas2_data = np.array(table_temperatures_data.loc[:,['T','bettas2']].loc[table_temperatures_data['bettas2'].notna()].values.tolist())
    fire_alphab_data = np.array(table_temperatures_data.loc[:,['T','alphab']].loc[table_temperatures_data['alphab'].notna()].values.tolist())
    fire_alphas_data = np.array(table_temperatures_data.loc[:,['T','alphas']].loc[table_temperatures_data['alphas'].notna()].values.tolist())

    #Линейная аппроксимация
    gammabt = linear_dia(t, fire_gammabt_data)
    gammabtt = linear_dia(t, fire_gammabtt_data)
    bettab = linear_dia(t, fire_bettab_data)
    eb0 = linear_dia(t, fire_eb0_data)
    eb2 = linear_dia(t, fire_eb2_data)
    eb1red = linear_dia(t, fire_eb1red_data)
    gammast1 = linear_dia(t, fire_gammast1_data)
    gammast2 = linear_dia(t, fire_gammast2_data)
    bettas1 = linear_dia(t, fire_bettas1_data)
    bettas2 = linear_dia(t, fire_bettas2_data)
    alphab = linear_dia(t, fire_alphab_data)*10**(-6)
    alphas = linear_dia(t, fire_alphas_data)*10**(-6)
    return {'gammabt': gammabt, 'gammabtt': gammabtt, 'gammast1': gammast1, 'gammast2': gammast2,
            'bettab': bettab, 'bettas1': bettas1, 'bettas2': bettas2,
            'alphab': alphab, 'alphas': alphas,
            'eb0': eb0, 'eb2': eb2, 'eb1red': eb1red}

def solve_temperature(t, x, Tmax, d):
    '''Вывод температуры бетона и арматуры в точке x и глубины прогрева до критической Tmax
    '''
    d = d/1000 #Перевод диаметра из мм в м
    rh0 = 2350 #Плотность бетона кг/м3
    W = 2.5 #Эксплуатационная влажность бетона %
    fi1 = 0.62 #Коэффициент φ1
    fi2 = 0.5 #Коэффициент φ2
    Tsol = 450 #Температура для расчета средних характеристик
    lmbd = (1.2 - 0.00035*Tsol) #Расчетный средний коэффициент теплопроводности бетона при 450
    C = (0.71 + 0.00083*Tsol) #Расчетный средный коэффициент теплоемкости бетона при 450
    ared = 3.6*lmbd/((C+ 0.05*W)*rh0) #Приведенный коэффициент температуропроводности
    l_pr = (0.2*ared*t)**0.5 #Глубина прогрева. t - минуты; результат - метры
    
    #Глубина прогрева до критической температуры Tmax. t - минуты; результат - метры
    r1 = 1 - ((Tmax-20)/1200)**0.5
    at = r1*l_pr - fi1*ared**0.5
    
    #Температура в бетоне, t - минуты; x - метры; результат - градусы
    rb = (x + fi1*ared**0.5)/l_pr
    Tb = 20
    if rb<1: Tb = 20 + 1200*(1 - rb)**2

    #Температура в арматуре, t - минуты; x - метры; результат - градусы
    ra = (x - d/2 + fi1*ared**0.5 + fi2*d)/l_pr
    Ta = 20
    if ra<1: Ta = 20 + 1200*(1 - ra)**2
    
    return {'at': at, 'Tb': Tb, 'Ta': Ta}


    

def solve_MultT_bot (b, h, dst, dsc, Ast, Asc, ast, asc, Rsn, Rsc, Rbn, Tmax, t, xiR):
    #Предельный момент при прогреве снизу
    Tst = solve_temperature(t, ast/100, Tmax, dst)['Ta'] #Температура нижней арматуры
    gst = temperature_data(Tst)['gammast1'] #Коэффициент к прочности нижней арматуры
    Tsc = solve_temperature(t, (h - asc)/100, Tmax, dsc)['Ta']  #Температура верхней арматуры
    gsc = temperature_data(Tsc)['gammast1'] #Коэффициент к прочности верхней арматуры
    Rsnt = Rsn*gst #Прочность нижней арматуры
    Rsct = Rsc*gsc #Прочность верхней арматуры
    Rbnt = Rbn*1 #Прочность бетона. При упрощенном расчете принимаем равным единице
    at = solve_temperature(t, 0, Tmax, 0)['at']*100 #Глубина прогрева до критической температуры
    h0 = h - ast #Рабочая высота сечения
    #xt = (Rsnt*Ast - Rsct*Asc)/(Rbnt*b) #Требуемая высота сжатой зоны бетона
    xt = (Rsnt*Ast)/(Rbnt*b) #Требуемая высота сжатой зоны бетона, без учета сжатой арматуры
    xit = xt/h0
    if xit <= xiR: #Если относительная высота не превышает граничную
        MultT = Rsnt*Ast*(h0 - 0.5*xt) #Предельный момент без учета сжатой арматуры
    if xit >= xiR: #Если относительная высота не превышает граничную
        MultT = Rbnt*b*xiR*h0*(h0 - 0.5*xiR*h0) 
    return MultT/100

def solve_MultT_top (b, h, dst, dsc, Ast, Asc, ast, asc, Rsn, Rsc, Rbn, Tmax, t, xiR):
    #Предельный момент при прогреве снизу
    Tst = solve_temperature(t, (h - ast)/100, Tmax, dst)['Ta'] #Температура нижней арматуры
    gst = temperature_data(Tst)['gammast1'] #Коэффициент к прочности нижней арматуры
    Tsc = solve_temperature(t, asc/100, Tmax, dsc)['Ta']  #Температура верхней арматуры
    gsc = temperature_data(Tsc)['gammast1'] #Коэффициент к прочности верхней арматуры
    Rsnt = Rsn*gst #Прочность нижней арматуры
    Rsct = Rsc*gsc #Прочность верхней арматуры
    Rbnt = Rbn*1 #Прочность бетона. При упрощенном расчете принимаем равным единице
    at = solve_temperature(t, 0, Tmax, 0)['at']*100 #Глубина прогрева до критической температуры
    h0 = h - ast - at #Рабочая высота сечения
    #xt = (Rsnt*Ast - Rsct*Asc)/(Rbnt*b) #Требуемая высота сжатой зоны бетона
    xt = (Rsnt*Ast)/(Rbnt*b) #Требуемая высота сжатой зоны бетона, без учета сжатой арматуры
    xit = xt/h0
    if xit <= xiR: #Если относительная высота не превышает граничную
        MultT = Rsnt*Ast*(h0 - 0.5*xt) #Предельный момент без учета сжатой арматуры
    if xit >= xiR: #Если относительная высота не превышает граничную
        MultT = Rbnt*b*xiR*h0*(h0 - 0.5*xiR*h0) 
    return MultT/100
    
def solve_Mult (b, h, Rb, ast, asc, Rst, Rsc, Ast, Asc, xiR):
    '''b и h - ширина и высота поперечного сечения, см;
    ac и at - привязка растянутой и сжатой арматуры, см;
    Rb - расчетное сопротивление бетона сжатию, кН/см2;
    Rst и Rsc - расчетное сопротивление арматуры растяжени и сжатию, кН/см2;
    Ast и Asc - площадь растянутой и сжатой арматуры, см2;
    xiR - граничная относительная высота сжатой зоны бетона'''
    Nb = Rb*b
    Nst = Rst*Ast
    Nsc = Rsc*Asc
    x = (Rst*Ast - Rsc*Asc)/(Rb*b) #Вычисляем требуемую высоту сжатой зоны бетона
    #x0 = (Rst*Ast)/(Rb*b) #Высота сжатой зоны бетона без учета сжатой арматуры
    h0 = h - ast #Рабочая высота сечения
    #x1 = h0 - ((Nb*h0**2 + 2*(Nsc-Nst)*(h0-asc))*Nb)**0.5/Nb
    #Mult0 = Rst*Ast*(h0-asc)
    #print(x1)
    xi = x/h0 #Относительная высота сжатой зоны бетона
    if xi <= xiR: #Если относительная высота не превышает граничную
        Mult = Rb*b*x*(h0-0.5*x) + Rsc*Asc*(h0 - asc)
    if xi > xiR: #Если относительная высота превышает граничную
        Mult = Rb*b*xiR*h0*(h0-0.5*xiR*h0) + Rsc*Asc*(h0 - asc)
    if Rst*Ast < Rsc*Asc: #Если высота сжатой зоны отрицательная, т.е. Rs*As<Rsc*Asc
        #if x0 < 2*asc: asc = x0/2
        Mult = Rst*Ast*(h0-asc)
    Mult = Mult/100 #перевод см в м
    return Mult

def solve_Mcrc (b, h, Eb, Es, Ast, ast, Asc, asc, Rbtn):
    alpha = Es/Eb
    Ab = b*h #Площадь бетона
    Ared = Ab + Ast*alpha + Asc*alpha
    Sred = Ab*0.5*h + Ast*ast*alpha + Asc*(h-asc)*alpha
    yt = Sred/Ared
    Ib = b*h**3/12 + Ab*(h/2-yt)**2
    Ired = Ib + alpha*Ast*(yt-ast)**2 + alpha*Asc*(h-yt-asc)**2 #Момент инерции приведенного сечения
    Wred = Ired/yt #Упруго-пластический момент сопротивления приведенного сечения
    Wpl = 1.3*Wred #Упруго-пластический момент сопротивления крайнего растянутого волокна бетона
    Mcrc = Wpl*Rbtn/100 #перевод см в м
    return Mcrc
    
def solve_Mcrc_a (b, h, Ast, ast, Asc, asc, Eb, Es, Rbtn, Rbn, epb1red, dl, ds, akr, adl):
    Mcrc = solve_Mcrc (b, h, Eb, Es, Ast, ast, Asc, asc, Rbtn)
    Ebred = Rbn/epb1red
    alphas1 = Es/Ebred
    alphas2 = alphas1
    h0 = h - ast
    must = Ast/(b*h0)
    musc = Asc/(b*h0)
    xm = h0*(
        ((must*alphas2 + musc*alphas1)**2 + 2*(must*alphas2 + musc*alphas1*asc/h0))**0.5
        -(must*alphas2 + musc*alphas1)
        )
    yc = xm
    Ist = Ast*(h0 - yc)**2
    Isc = Asc*(yc - asc)**2
    Ib = b*yc**3/12 + yc*b*(yc/2)**2
    Ired = Ib + Ist*alphas2 + Isc*alphas1
    xt0 = h - xm
    xt = min(0.5*h, max(2*ast, xt0))
    At = xt*b
    ls0 = 0.5*ds*At/Asc
    ls = min(40*ds, 40, max(ls0, 10*ds, 10))
    phi11 = 1.4; phi12 = 1.0; phi13 = 1.0
    phi2 = 0.5; phi3 = 1.0
    Mkrk = ( (4*Mcrc*(h0-yc)*ls*phi2*phi3*phi11/Ired + 5*Ebred*akr)/
             (5*(h0-yc)*ls/Ired*(phi2*phi3*(dl*(phi11-phi12)+phi12)))
            )       
    Mkrl = 8*Mcrc/(10*dl) + Ebred*adl/((h0-yc)*ls/Ired*phi11*phi2*phi3*dl)
    Mdlk, Mdll = Mkrk*dl, Mkrl*dl
    return Mdlk/100, Mdll/100


def solve_all_MultT (data, Ast_main, Asc_main, Ast, Asc):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    eps_s_el = rdata['Rs']/rdata['Es'] #Упругая деформация арматуры
    xiR = 0.8/(1+eps_s_el/cdata['eb2']) #Граничная относительная высота сжатой зоны бетона
    MultT_arr = ['' for i in range(len(Asc)+len(Ast)+2)]
    for i in range(len(Asc)):
        MultT_arr[i] = -solve_MultT_top(b=b, h=h, dst=12, dsc=12,
                                                  Ast=Asc[i], ast=asc, Asc=Ast_main, asc=ast,
                                                  Rbn=cdata['Rbn']/10*data["gammab"], Rsc=rdata['Rsc']/10, Rsn=rdata['Rsn']/10,
                                                  Tmax=500, t=data['fire_t'], xiR=xiR)
    MultT_arr[len(Asc)] = -solve_MultT_top(b=b, h=h, dst=12, dsc=12,
                                                  Ast=Asc_main, ast=asc, Asc=Ast_main, asc=ast,
                                                  Rbn=cdata['Rbn']/10*data["gammab"], Rsc=rdata['Rsc']/10, Rsn=rdata['Rsn']/10,
                                                  Tmax=500, t=data['fire_t'], xiR=xiR)
    MultT_arr[len(Asc)+1] = solve_MultT_bot(b=b, h=h, dst=12, dsc=12,
                                                  Ast=Ast_main, ast=ast, Asc=Asc_main, asc=asc,
                                                  Rbn=cdata['Rbn']/10*data["gammab"], Rsc=rdata['Rsc']/10, Rsn=rdata['Rsn']/10,
                                                  Tmax=500, t=data['fire_t'], xiR=xiR)
    for i in range(len(Ast)):
        MultT_arr[len(Asc)+2+i] = solve_MultT_bot(b=b, h=h, dst=12, dsc=12,
                                                  Ast=Ast[i], ast=ast, Asc=Asc_main, asc=asc,
                                                  Rbn=cdata['Rbn']/10*data["gammabt"], Rsc=rdata['Rsc']/10, Rsn=rdata['Rsn']/10,
                                                  Tmax=500, t=data['fire_t'], xiR=xiR)
    return MultT_arr


def solve_all_Mcrc_a (data, Ast_main, Asc_main, Ast, Asc, ds):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    dl = data['dl']
    akr = data['akr']/10
    adl = data['adl']/10
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    Mcrck = [0.0 for i in range(len(Asc)+len(Ast)+2)]
    Mcrcl = [0.0 for i in range(len(Asc)+len(Ast)+2)]
    for i in range(len(Asc)):
        rez = solve_Mcrc_a(b=b, h=h, Ast=Asc[i], ast=asc, Asc=Ast_main, asc=ast,
                                          Eb=cdata['Eb']/10, Es=rdata['Es']/10, Rbtn=cdata['Rbtn']*data["gammabt"]/10,
                                          Rbn=cdata['Rbn']*data["gammab"]/10, epb1red=cdata['eb1red'], dl=dl, ds=ds[i], akr=akr, adl=adl)
        Mcrck[i], Mcrcl[i] = -1*rez[0], -1*rez[1]
    rez = solve_Mcrc_a(b=b, h=h, Ast=Asc_main, ast=asc, Asc=Ast_main, asc=ast,
                                          Eb=cdata['Eb']/10, Es=rdata['Es']/10, Rbtn=cdata['Rbtn']*data["gammabt"]/10,
                                          Rbn=cdata['Rbn']*data["gammab"]/10, epb1red=cdata['eb1red'], dl=dl, ds=ds[i], akr=akr, adl=adl)
    Mcrck[len(Asc)], Mcrcl[len(Asc)] = -1*rez[0], -1*rez[1]
    rez = solve_Mcrc_a(b=b, h=h, Ast=Ast_main, ast=ast, Asc=Asc_main, asc=asc,
                                          Eb=cdata['Eb']/10, Es=rdata['Es']/10, Rbtn=cdata['Rbtn']*data["gammabt"]/10,
                                          Rbn=cdata['Rbn']*data["gammab"]/10, epb1red=cdata['eb1red'], dl=dl, ds=ds[i], akr=akr, adl=adl)
    Mcrck[len(Asc)+1], Mcrcl[len(Asc)+1] = rez[0], rez[1]
    for i in range(len(Ast)):
        rez = solve_Mcrc_a(b=b, h=h, Ast=Ast[i], ast=ast, Asc=Asc_main, asc=asc,
                                          Eb=cdata['Eb']/10, Es=rdata['Es']/10, Rbtn=cdata['Rbtn']*data["gammabt"]/10,
                                          Rbn=cdata['Rbn']*data["gammab"]/10, epb1red=cdata['eb1red'], dl=dl, ds=ds[i], akr=akr, adl=adl)
        Mcrck[len(Asc)+2+i], Mcrcl[len(Asc)+2+i] = rez[0], rez[1]
    return Mcrck, Mcrcl


def solve_all_Mcrc (data, Ast_main, Asc_main, Ast, Asc):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    Mcrc_arr = ['' for i in range(len(Asc)+len(Ast)+2)]
    for i in range(len(Asc)):
        Mcrc_arr[i] = -solve_Mcrc(b=b, h=h, Eb=cdata['Eb']/10, Es=rdata['Es']/10, Ast=Asc[i], ast=asc, Asc=Ast_main, asc=ast, Rbtn=cdata['Rbtn']/10*data["gammabt"])
    Mcrc_arr[len(Asc)] = -solve_Mcrc(b=b, h=h, Eb=cdata['Eb']/10, Es=rdata['Es']/10, Ast=Asc_main, ast=asc, Asc=Ast_main, asc=ast, Rbtn=cdata['Rbtn']/10*data["gammabt"])
    Mcrc_arr[len(Asc)+1] = solve_Mcrc(b=b, h=h, Eb=cdata['Eb']/10, Es=rdata['Es']/10, Ast=Ast_main, ast=ast, Asc=Asc_main, asc=asc, Rbtn=cdata['Rbtn']/10*data["gammabt"])
    for i in range(len(Ast)):
        Mcrc_arr[len(Asc)+2+i] = solve_Mcrc(b=b, h=h, Eb=cdata['Eb']/10, Es=rdata['Es']/10, Ast=Ast[i], ast=ast, Asc=Asc_main, asc=asc, Rbtn=cdata['Rbtn']/10*data["gammabt"])
    return Mcrc_arr



def solve_all_Mult (data, Ast_main, Asc_main, Ast, Asc):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    eps_s_el = rdata['Rs']/rdata['Es'] #Упругая деформация арматуры
    xiR = 0.8/(1+eps_s_el/cdata['eb2']) #Граничная относительная высота сжатой зоны бетона
    Mult_short = ['' for i in range(len(Asc)+len(Ast)+2)]
    Mult_long = ['' for i in range(len(Asc)+len(Ast)+2)]
    for i in range(len(Asc)):
        Mult_short[i] = -solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc[i], Asc=Ast_main, xiR=xiR)
        Mult_long[i] = -solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*0.9*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rs']/10, Ast=Asc[i], Asc=Ast_main, xiR=xiR)
    Mult_short[len(Asc)] = -solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc_main, Asc=Ast_main, xiR=xiR)
    Mult_short[len(Asc)+1] = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast_main, Asc=Asc_main, xiR=xiR)
    Mult_long[len(Asc)] = -solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*0.9*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rs']/10, Ast=Asc_main, Asc=Ast_main, xiR=xiR)
    Mult_long[len(Asc)+1] = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*0.9*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rs']/10, Ast=Ast_main, Asc=Asc_main, xiR=xiR)
    for i in range(len(Ast)):
        Mult_short[len(Asc)+2+i] = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast[i], Asc=Asc_main, xiR=xiR)
        Mult_long[len(Asc)+2+i] = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*0.9*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rs']/10, Ast=Ast[i], Asc=Asc_main, xiR=xiR)
    return Mult_short, Mult_long



    
    
    
