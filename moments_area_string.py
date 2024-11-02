pi = 3.1415927

def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False

def replace_in_string(string: str):
    string = string.replace(' ', '')
    string = string.replace('д', 'd')
    string = string.replace('Д', 'd')
    string = string.replace('в', 'd')
    string = string.replace('В', 'd')
    string = string.replace('ы', 's')
    string = string.replace('Ы', 's')    
    string = string.replace('ф', 'd')
    string = string.replace('Ф', 'd')
    string = string.replace('D', 'd')
    string = string.replace('ш', 's')
    string = string.replace('Ш', 's')
    string = string.replace('S', 's')
    string = string.replace('/', 's')
    string = string.replace('-', 's')
    return string

def clear_and_sep_string(string: str):
    string = replace_in_string(string)
    string = string.replace(',', '.')
    string = string.replace('++', '+')
    string = string.replace('--', '+-')
    string = string.replace('-', '+-')
    string = string.replace('-+', '+')
    return string.split(sep="+", maxsplit=-1)

def reinf_area(d: float, n: float, s: float, b:float):
    area = 's'
    if int(d) in [3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40]:
        d = d / 10.0
        if n == None:
            n = 1
            if s == None:
                s = 1000
        area = pi*d*d/4 * b/s * n
        return area
    return area


def reinf_string_split(string: str, b:float):
    string = clear_and_sep_string(string)
    out = []
    for i in string:
        if is_number(i):
            out.append([20.0,float(i)/(pi),b])
        if is_number(i)==False and i!='':
            q = []
            znak = 1
            if len(i.split(sep = '-'))==2:
                znak=-1
                i = i.split(sep = '-')[1]
            string2 = i.split(sep="d", maxsplit=-1)
            if len(string2)==1:
                q.append('')
                q.append(string2[0])
            else:
                q = string2
            temp = []
            for j in q:
                string3 = j.split(sep="s", maxsplit=-1)
                temp.append(string3)
            rez = [temp[1][0]]
            if len(temp[0])==1:
                rez.append(temp[0][0])
                if len(temp[1])==1:
                    rez.append(b)
                else:
                    rez.append(temp[1][1])
            else:
                rez.append(1)
                rez.append(temp[0][1])
            if rez[1] == '':
                rez[1] = '1'
            out.append([float(rez[0]),float(rez[1])*znak,float(rez[2])])
    return out

def reinf_area_array(ar: list, b:float):
    area_sum = 0
    for i in ar:
        if reinf_area(i[0],i[1],i[2],b)=='s':
            return 's'
        area_sum = area_sum + reinf_area(i[0],i[1],i[2],b)
    return area_sum

def calc_string_area(string: str, b:float):
    rez1 = []
    try: q = reinf_string_split(string, b)
    except: q = [[0.0, 0.0, 1000.0]]
    rez1.append(q)
    rez = reinf_area_array(q, b)
    if rez == 's': rez = 0.0
    return rez, rez1

