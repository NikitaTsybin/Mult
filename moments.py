import streamlit as st
import pandas as pd
from Area_from_string import calc_string_area

add_dir = ''
##
##add_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
##+ '/pages/moments/')
##sys.path.append(add_dir)

table_concretes_data = pd.read_excel(add_dir + 'RC_data.xlsx', sheet_name="Concretes_SP63", header=[0])
table_reinf_data = pd.read_excel(add_dir + 'RC_data.xlsx', sheet_name="Reinforcement_SP63", header=[0])
available_concretes = table_concretes_data['Class'].to_list()
available_reinf = table_reinf_data['Class'].to_list()



from moments_solve_func import *

data = {}
Ast_main_init = '12/200'
Asс_main_init = '10/200'
Ast_string_init = '12/200 12/100 12/200+16/200'
Asc_string_init = '10/200 10/100 10/200+16/200 16/100 20/100'

if True: #¬вод исходных данных
    cols = st.columns([0.7, 0.7, 0.7, 0.7, 1, 0.7, 1, 0.7])
    c = 0
    b = cols[c].number_input(label='$b$, см', step=5.0, format="%.1f", value=100.0, min_value=1.0, max_value=500.0)
    b = round(b,2); data.update({'b': b})
    c += 1
    h = cols[c].number_input(label='$h$, см', step=1.0, format="%.1f", value=20.0, min_value=1.0, max_value=500.0)
    h = round(h,2); data.update({'h': h})
    c += 1
    ast = cols[c].number_input(label='$a$, см', step=0.5, format="%.1f", value=5.0, min_value=1.0, max_value=200.0)
    ast = round(ast,2); data.update({'ast': ast})
    c += 1
    asc = cols[c].number_input(label="$a'$, см", step=0.5, format="%.1f", value=5.0, min_value=1.0, max_value=200.0)
    asc = round(asc,2); data.update({'asc': asc})
    c += 1
    ctype = cols[c].selectbox(label='Бетон', options=available_concretes, index=5, label_visibility="visible")
    data.update({'ctype': ctype})
    selected_concrete_data = table_concretes_data.loc[table_concretes_data['Class'] == ctype]
    selected_concrete_data = selected_concrete_data.to_dict('records')[0]
    c += 1
    gammab = cols[c].number_input(label='$\\gamma_{b}$', step=0.05, format="%.2f", value=1.0, min_value=0.1, max_value=1.0, label_visibility="visible")
    data.update({'gammab': gammab})
    c += 1
    rtype = cols[c].selectbox(label='Арматура', options=['A500', 'A400', 'A240'], index=0, label_visibility="visible")
    data.update({'rtype': rtype})
    selected_reinf_data = table_reinf_data.loc[table_reinf_data['Class'] == rtype]
    selected_reinf_data = selected_reinf_data.to_dict('records')[0]
    c += 1
    fire_t = cols[c].number_input(label="$t$, мин", step=30, format="%i", value=120, min_value=30, max_value=240)
    data.update({'fire_t': fire_t})
    cols = st.columns([1,1])
    Ast_main_string = cols[0].text_input('Фоновое нижнее армирование', value = Ast_main_init)
    if Ast_main_string == '': Ast_main_string = '0'
    Ast_main_string = string_area_to_list(Ast_main_string)[0]
    Ast_main_val = round(calc_string_area(Ast_main_string, b*10)[0],3)

    Asc_main_string = cols[1].text_input('Фоновое верхнее армирование', value = Asс_main_init)
    if Asc_main_string == '': Asc_main_string = '0'
    Asc_main_string = string_area_to_list(Asc_main_string)[0]
    Asc_main_val = round(calc_string_area(Asc_main_string, b*10)[0],3)

    cols[0].write('Площадь нижнего фонового ' + str(Ast_main_val) + ' $см^2$')
    cols[1].write('Площадь верхнего фонового ' + str(Asc_main_val) + ' $см^2$')

    Ast_string = st.text_input('Нижнее дополнительное армирование. Разделители запятая или пробел', value = Ast_string_init)
    Asc_string = st.text_input('Верхнее дополнительное армирование. Разделители запятая или пробел', value = Asc_string_init)
    #

if True: #Подготовка массивов с площадью арматуры
    Ast_string, Asc_string = string_area_to_list(Ast_string), string_area_to_list(Asc_string)
    if Ast_string == []: Ast_string = ['0']
    if Asc_string == []: Asc_string = ['0']
    #Сортируем по возрастанию площади
    Ast_string = sorted(Ast_string, key=lambda x: calc_string_area(x, b*10)[0], reverse=False)
    Asc_string = sorted(Asc_string, key=lambda x: calc_string_area(x, b*10)[0], reverse=True)
    #st.write(pd.DataFrame(Ast_string))
    #st.write(pd.DataFrame(Asc_string))
    Ast_val = []
    Asc_val = []
    for i in Ast_string:
        rez = calc_string_area(i + '+' + Ast_main_string, b*10)
        Ast_val.append(round(rez[0],3))

    for i in Asc_string:
        rez = calc_string_area(i + '+' + Asc_main_string, b*10)
        Asc_val.append(round(rez[0],3))

    Ast = [] 
    Asc = []
    Ast_main_s =[]
    Asc_main_s =[]
    Ast_s =[]
    
    for i in range(len(Asc_val)):
        Ast.append(Asc_val[i])
        Ast_s.append(Asc_string[i])
        Ast_main_s.append(Asc_main_string)
        Asc_main_s.append(Ast_main_string)
    
    Ast.append(Asc_main_val)
    Ast_main_s.append(Asc_main_string)
    Asc_main_s.append(Ast_main_string)
    Ast_s.append('')
    
    Ast.append(Ast_main_val)
    Ast_main_s.append(Ast_main_string)
    Asc_main_s.append(Asc_main_string)
    Ast_s.append('')
    
    for i in range(len(Ast_val)):
        Ast.append(Ast_val[i])
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



#st.write(Ast_val)
#st.write(Asc_val)
#st.write(data)
Multx_short= solve_all_Mult(data, Ast_main_val, Asc_main_val, Ast_val, Asc_val)
#st.write(Mult_short)

#


#for i in range(len(Ast_string)):
#    Multt_short[i+2][0] = Ast_string[i]
#    Multt_short[i+2][1] = Ast_val[i]
#    Multc_short[0][i+2] = Ast_string[i]
#    Multc_short[1][i+2] = Ast_val[i]

#for i in range(len(Asc_string)):
#    Multc_short[i+2][0] = Asc_string[i]
#    Multc_short[i+2][1] = Asc_val[i]
#    Multt_short[0][i+2] = Asc_string[i]
#    Multt_short[1][i+2] = Asc_val[i]

result = pd.DataFrame()
result['Asc'] = Asc_main_s
result['Asc, см2'] = Asc
#result['Фон As'] = Ast_main_s
result['As'] = Ast_s
result['As, см2'] = Ast

result['Multx, тсм'] = Multx_short

st.dataframe(result, hide_index=True)
#st.dataframe(pd.DataFrame(Multc_short), hide_index=True)
    
    