import streamlit as st
import pandas as pd
import os
import sys


add_dir = ''
##add_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
##+ '/pages/mtable/')
##sys.path.append(add_dir)

from moments_area_string import calc_string_area

table_concretes_data = pd.read_excel(add_dir + 'RC_data.xlsx', sheet_name="Concretes_SP63", header=[0])
table_reinf_data = pd.read_excel(add_dir + 'RC_data.xlsx', sheet_name="Reinforcement_SP63", header=[0])
available_concretes = table_concretes_data['Class'].to_list()
available_reinf = table_reinf_data['Class'].to_list()



from moments_solve_func import *

gz = 10
#gz = 9.8066
#gz = 1
datax = {}
Ast_main_init = '12/200'
Asс_main_init = '10/200'
Ast_string_init = '12/200 12/100 12/200+16/200'
Asc_string_init = '10/200 10/100 10/200+16/200 16/100 20/100'

with st.expander('Пояснения'):
    st.write('$b$ - ширина сечения, см;')
    st.write('$h$ - высота сечения, см;')
    st.write("$a_x$ - привязка нижней арматуры от низа плиты в направлении оси $x$, см;")
    st.write("$a'_x$ - привязка верхней арматуры от верха плиты в направлении оси $x$, см;")
    st.write("$a_y$ - привязка нижней арматуры от низа плиты в направлении оси $y$, см;")
    st.write("$a'_y$ - привязка верхней арматуры от верха плиты в направлении оси $y$, см;")
    st.write("$\\gamma_b$ - коэффициент, вводимый к расчетному сопротивлению бетона на сжатие $R_b$ и $R_{b,n}$ во всех расчетах;")
    st.write("$\\gamma_{bt}$ - коэффициент, вводимый к расчетному сопротивлению бетона на растяжение $R_{bt}$ и $R_{bt,ser}$ во всех расчетах;")
    st.write("$t$ - время огневого воздействия (для расчета на огнестойкость), мин;")
    st.write("$\\gamma_l$ - соотношение между длительными и кратковременными нагрузками (для расчета раскрытия трещин).")

if True: #¬вод исходных данных
    cols = st.columns([0.5, 0.5, 0.5, 0.8, 0.45, 0.6, 0.5, 0.45, 0.5])
    c = 0
    b = cols[c].number_input(label='$b$, см', step=5.0, format="%.1f", value=100.0, min_value=1.0, max_value=500.0)
    b = round(b,2); datax.update({'b': b})

    h = cols[c].number_input(label='$h$, см', step=1.0, format="%.1f", value=20.0, min_value=1.0, max_value=500.0)
    h = round(h,2); datax.update({'h': h})
    
    c += 1
    astx = cols[c].number_input(label='$a_x$, см', step=0.5, format="%.1f", value=4.5, min_value=1.0, max_value=200.0)
    astx = round(astx,2); datax.update({'ast': astx})
    ascx = cols[c].number_input(label="$a'_x$, см", step=0.5, format="%.1f", value=5.5, min_value=1.0, max_value=200.0)
    ascx = round(ascx,2); datax.update({'asc': ascx})
    
    c +=1
    asty = cols[c].number_input(label='$a_y$, см', step=0.5, format="%.1f", value=5.5, min_value=1.0, max_value=200.0)
    asty = round(asty,2)
    ascy = cols[c].number_input(label="$a'_y$, см", step=0.5, format="%.1f", value=4.5, min_value=1.0, max_value=200.0)
    ascy = round(ascy,2)

    c += 1
    ctype = cols[c].selectbox(label='Бетон', options=available_concretes, index=5, label_visibility="visible")
    datax.update({'ctype': ctype})
    selected_concrete_data = table_concretes_data.loc[table_concretes_data['Class'] == ctype]
    selected_concrete_data = selected_concrete_data.to_dict('records')[0]

    rtype = cols[c].selectbox(label='Арматура', options=['A500', 'A400'], index=0, label_visibility="visible")
    datax.update({'rtype': rtype})
    selected_reinf_data = table_reinf_data.loc[table_reinf_data['Class'] == rtype]
    selected_reinf_data = selected_reinf_data.to_dict('records')[0]

    c += 1
    gammab = cols[c].number_input(label='$\\gamma_{b}$', step=0.05, format="%.2f", value=1.0, min_value=0.1, max_value=1.0, label_visibility="visible")
    datax.update({'gammab': gammab})
    gammabt = cols[c].number_input(label='$\\gamma_{bt}$', step=0.05, format="%.2f", value=1.0, min_value=0.1, max_value=1.0, label_visibility="visible")
    datax.update({'gammabt': gammabt})

    c += 1
    Ast_main_string = cols[c].text_input('Фон низ', value = Ast_main_init)
    if Ast_main_string == '': Ast_main_string = '0'
    Ast_main_string = string_area_to_list(Ast_main_string)[0]
    rez = calc_string_area(Ast_main_string, b*10)
    Ast_main_val = round(rez[0],3)
    dst_main = 0
    for i in rez[1]:
        for j in i:
            if j[0]>dst_main: dst_main=j[0]

    Asc_main_string = cols[c].text_input('Фон верх', value = Asс_main_init)
    if Asc_main_string == '': Asc_main_string = '0'
    rez = string_area_to_list(Asc_main_string)
    Asc_main_string = string_area_to_list(Asc_main_string)[0]
    rez = calc_string_area(Asc_main_string, b*10)
    Asc_main_val = round(rez[0],3)
    dsc_main = 0
    for i in rez[1]:
        for j in i:
            if j[0]>dsc_main: dsc_main=j[0]

    c += 1
    cols[c].text_input('$Aн, см^2$', value = Ast_main_val)
    cols[c].text_input('$Aв, см^2$', value = Asc_main_val)

    c += 1
    fire_t = cols[c].number_input(label="$t$, мин", step=30, format="%i", value=120, min_value=30, max_value=240)
    datax.update({'fire_t': fire_t})
    gammal = cols[c].number_input(label="$\\gamma_l$", step=0.01, format="%.2f", value=0.87, min_value=0.00, max_value=1.0)
    datax.update({'dl': gammal})

    c += 1
    akr = cols[c].number_input(label="$a_{crc,t}$, мм", step=0.01, format="%.2f", value=0.4, min_value=0.00, max_value=1.0)
    datax.update({'akr': akr})
    adl = cols[c].number_input(label="$a_{crc,l}$, мм", step=0.01, format="%.2f", value=0.3, min_value=0.00, max_value=1.0)
    datax.update({'adl': adl})


    datay = datax.copy()
    datay.update({'ast': asty})
    datay.update({'asc': ascy})

    Ast_string = st.text_input('Нижнее дополнительное армирование. Разделители запятая или пробел', value = Ast_string_init)
    Asc_string = st.text_input('Верхнее дополнительное армирование. Разделители запятая или пробел', value = Asc_string_init)


if True: #Подготовка массивов с площадью арматуры
    Ast_string, Asc_string = string_area_to_list(Ast_string), string_area_to_list(Asc_string)
    #if Ast_string == []: Ast_string = ['0']
    #if Asc_string == []: Asc_string = ['0']
    #Сортируем по возрастанию площади
    Ast_string = sorted(Ast_string, key=lambda x: calc_string_area(x, b*10)[0], reverse=False)
    Asc_string = sorted(Asc_string, key=lambda x: calc_string_area(x, b*10)[0], reverse=True)
    #st.write(pd.DataFrame(Ast_string))
    #st.write(pd.DataFrame(Asc_string))
    Ast_val = []
    Asc_val = []
    dst = []
    dsc = []
    for i in Ast_string:
        rez = calc_string_area(i + '+' + Ast_main_string, b*10)
        Ast_val.append(round(rez[0],3))
        dmax = 0
        for i in rez[1]:
            for j in i:
                if j[0]>dmax: dmax=j[0]
        dst.append(dmax)
    
    
    for i in Asc_string:
        rez = calc_string_area(i + '+' + Asc_main_string, b*10)
        Asc_val.append(round(rez[0],3))
        dmax = 0
        for i in rez[1]:
            for j in i:
                if j[0]>dmax: dmax=j[0]
        dsc.append(dmax)
    
    Ast = [] 
    Asc = []
    Ast_main_s =[]
    Asc_main_s =[]
    Ast_s =[]
    ds = []
    
    for i in range(len(Asc_val)):
        Ast.append(Asc_val[i])
        ds.append(dsc[i])
        Ast_s.append(Asc_string[i])
        Ast_main_s.append(Asc_main_string)
        Asc_main_s.append(Ast_main_string)
    
    Ast.append(Asc_main_val)
    Ast_main_s.append(Asc_main_string)
    Asc_main_s.append(Ast_main_string)
    Ast_s.append('')
    ds.append(dsc_main)

    Ast.append(Ast_main_val)
    Ast_main_s.append(Ast_main_string)
    Asc_main_s.append(Asc_main_string)
    Ast_s.append('')
    ds.append(dst_main)
    
    for i in range(len(Ast_val)):
        Ast.append(Ast_val[i])
        ds.append(dst[i])
        Ast_s.append(Ast_string[i])
        Ast_main_s.append(Ast_main_string)
        Asc_main_s.append(Asc_main_string)

    for i in range(len(Ast_s)):
        if Ast_s[i] != '':
            Ast_s[i] = Ast_main_s[i] + '+' + Ast_s[i]
        else: Ast_s[i] = Ast_main_s[i]

    
    for i in Asc_val: Asc.append(Ast_main_val)
    Asc.append(Ast_main_val)
    Asc.append(Asc_main_val)
    for i in Ast_val: Asc.append(Asc_main_val)


#Расчет предельных моментов
Multx_short, Multx_long = solve_all_Mult(datax, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
Multy_short, Multy_long = solve_all_Mult(datay, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
#Расчет моментов образования трещин
Mcrcx = solve_all_Mcrc(datax, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
Mcrcy = solve_all_Mcrc(datay, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
#Расчет предельных моментов по огнестойкости
MultTx =solve_all_MultT(datax, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
MultTy =solve_all_MultT(datay, Ast_main_val, Asc_main_val, Ast_val, Asc_val)

Mcrckx, Mcrclx = solve_all_Mcrc_a(datax, Ast_main_val, Asc_main_val, Ast_val, Asc_val, ds)
Mcrcky, Mcrcly = solve_all_Mcrc_a(datax, Ast_main_val, Asc_main_val, Ast_val, Asc_val, ds)


result = pd.DataFrame()
result['Asc'] = Asc_main_s
result['Asc, см2'] = Asc
#result['Фон As'] = Ast_main_s
result['As'] = Ast_s
result['As, см2'] = Ast
#result['ds'] = ds
result['%'] = round(result['As, см2']/b/h*100,3)

result['Multx'] = Multx_short
result['Multx'] = round(result['Multx']/gz, 2)
result['Multy'] = Multy_short
result['Multy'] = round(result['Multy']/gz, 2)
#result['Multxl'] = Multx_long
#result['Multyl'] = Multy_long

result['Mcrcx'] = Mcrcx
result['Mcrcx'] = round(result['Mcrcx']/gz, 2)
result['Mcrcy'] = Mcrcy
result['Mcrcy'] = round(result['Mcrcy']/gz,2)

#result['kMx'] = round(result['Multx']/result['Mcrcx'], 3)
#result['kMy'] = round(result['Multy']/result['Mcrcy'], 3)

result['MultTx'] = MultTx
result['MultTx'] = round(result['MultTx']/gz, 2)
result['MultTy'] = MultTy
result['MultTy'] = round(result['MultTy']/gz, 2)

result['Mcrckx'] = Mcrckx
result['Mcrckx'] = round(result['Mcrckx']/gz, 2)

result['Mcrclx'] = Mcrclx
result['Mcrclx'] = round(result['Mcrclx']/gz, 2)

result['Mcrcky'] = Mcrcky
result['Mcrcky'] = round(result['Mcrcky']/gz, 2)

result['Mcrcly'] = Mcrclx
result['Mcrcly'] = round(result['Mcrcly']/gz, 2)

st.dataframe(result, hide_index=True)
    
    