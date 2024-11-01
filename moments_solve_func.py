import pandas as pd
from math import pi
import re

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

def clean_empty_in_list(list):
    list_new = []
    for i in list:
        if i != '':
            list_new.append(i)
    return list_new

def string_area_to_list(string):
    string = clean_reinf_string(string)
    list_from_string = re.split(';|,| |\t', string)
    list_from_string = clean_empty_in_list(list_from_string)
    return list_from_string


#Импорт и чтение данных для бетона и арматуры
def read_data_for_concrete_and_reinf (ctype, rtype):
    #чтение файлов
    table_concretes_data = pd.read_excel('RC_data.xlsx', sheet_name="Concretes_SP63", header=[0])
    table_reinf_data = pd.read_excel('RC_data.xlsx', sheet_name="Reinforcement_SP63", header=[0])
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
    

def solve_Mult (b:float, h:float, Rb:float, ast:float, asc:float, Rst:float, Rsc:float, Ast:float, Asc:float, xiR:float):
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




 
def solve_Mcrc ():
    pass
    



def solve_all_Mult (data, A_main, Ast, Asc):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    eps_s_el = rdata['Rs']/rdata['Es'] #Упругая деформация арматуры
    xiR = 0.8/(1+eps_s_el/cdata['eb2']) #Граничная относительная высота сжатой зоны бетона
    Multt_short = [['' for j in range(len(Asc)+2)] for i in range(len(Ast)+2)]
    Multc_short = [['' for j in range(len(Ast)+2)] for i in range(len(Asc)+2)]
    for i in range(len(Ast)):
        for j in range(len(Asc)):
            Multt_short[i+2][j+2] = round(solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast[i], Asc=Asc[j], xiR=xiR)*0.1019716,2)
    for i in range(len(Asc)):
        for j in range(len(Ast)):    
            Multc_short[i+2][j+2] = round(-solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc[i], Asc=Ast[j], xiR=xiR)*0.1019716,2)
    return Multt_short, Multc_short



def solve_all_Mult (data, Ast_main, Asc_main, Ast, Asc):
    b = data['b'] #Ширина сечения, см
    h = data['h'] #Высота сечения, см
    ast = data['ast'] #Привязка нижней арматуры
    asc = data['asc'] #Привязка верхней арматуры
    cdata, rdata = read_data_for_concrete_and_reinf (data['ctype'], data['rtype'])
    eps_s_el = rdata['Rs']/rdata['Es'] #Упругая деформация арматуры
    xiR = 0.8/(1+eps_s_el/cdata['eb2']) #Граничная относительная высота сжатой зоны бетона
    Mult_short = ['' for i in range(len(Asc)+len(Ast)+2)]
    for i in range(len(Asc)):
        Mult_short[i] = round(-solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc[i], Asc=Ast_main, xiR=xiR)*0.1019716,2)
    Mult_short[len(Asc)] = round(-solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc_main, Asc=Ast_main, xiR=xiR)*0.1019716,2)
    Mult_short[len(Asc)+1] = round(solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast_main, Asc=Asc_main, xiR=xiR)*0.1019716,2)
    for i in range(len(Ast)):
        Mult_short[len(Asc)+2+i] = round(solve_Mult(b=b, h=h, Rb=cdata['Rb']/10*data["gammab"], ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast[i], Asc=Asc_main, xiR=xiR)*0.1019716,2)
    return Mult_short




def test():
    #Выбор класса бетона и арматуры
    ctype = 'B20' #Класс бетона
    rtype = 'A500' #Класс арматуры
    dst = 16 #Диаметр нижней арматуры, мм
    nst = 5 #Число стержней нижней арматуры, шт
    dsc = 12 #Диаметр верхней арматуры, мм
    nsc = 5 #Число стержней верхней арматур, шт
    Ast = pi*(dst/10*dst/10)*nst/4 #Площадь нижней арматуры, см2
    Asc = pi*(dsc/10*dsc/10)*nsc/4 #Площадь верхней арматуры, см2
    Ast = 3
    Asc = 12
    b = 30 #Ширина сечения, см
    h = 40 #Высота сечения, см
    ast = 5 #Привязка нижней арматуры
    asc = 5 #Привязка верхней арматуры
    #Получение данных по характеристикам для выбранных материалов
    cdata, rdata = read_data_for_concrete_and_reinf (ctype, rtype)
    eps_s_el = rdata['Rs']/rdata['Es'] #Упругая деформация
    xiR = 0.8/(1+eps_s_el/cdata['eb2']) #Граничная относительная высота сжатой зоны бетона
    Multt = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10, ast=ast, asc=asc, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Ast, Asc=Asc, xiR=xiR)
    Multc = solve_Mult(b=b, h=h, Rb=cdata['Rb']/10, ast=asc, asc=ast, Rst=rdata['Rs']/10, Rsc=rdata['Rsc']/10, Ast=Asc, Asc=Ast, xiR=xiR)
    print(Multt, Multc)
test()
    
    
    
