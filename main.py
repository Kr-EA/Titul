import json
import re
import os
import sys
import ast
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

runpath = os.path.dirname(os.path.abspath(__file__))
template_path = runpath + ("/template.docx")
config_path = runpath + ("/config.json")
teachers_path = runpath + ("/teachers.txt")
extra_path = runpath + ("/faculties_cafedrals_shortcuts.json")
pattern = r'^[^\d]+'

teachers = {}
with open(teachers_path, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        arr = line.split(' ')
        inits = ''.join([s[0] for s in arr])
        if inits not in teachers.keys():
            teachers[inits] = [f'{arr[0]} {arr[1][0]}.{arr[2][0]}.']
        else:
            teachers[inits].append(f'{arr[0]} {arr[1][0]}.{arr[2][0]}.')

modules_list = os.popen("python3 -m pip list").read()
if ("docxtpl" not in modules_list):
    os.system("python3 -m pip install -qqq docxtpl")

from docxtpl import DocxTemplate

data = dict()

with open(config_path, 'r', encoding='utf-8') as f:
    default_data = json.load(f)

_c = 0 if int(datetime.now().month) < 9 else 1 
default = {
        'author': default_data['me'],
        'group': default_data['my_caf']+f'-{str((int(datetime.now().year)-int(default_data['year_of_arrive']) - default_data['AH_count'])*2 + _c)}{default_data['group_num']}{default_data['degree'][0]}',
        'year': str(datetime.now().year),
        }

with open(extra_path, 'r', encoding='utf-8') as f:
    all_data = json.load(f)
    faculties = all_data['faculties']
    cafedrals = all_data['cafedrals']
    titles_shortcuts = all_data['titles_shortcuts']

def fill_template(data):
    doc = DocxTemplate(template_path)
    doc.render(data)

    subject_abb = ''.join(el[0] for el in data['subject'].split(' ')).upper() if len(data['subject'].split(' ')) != 1 else data['subject']
    work_title_abb = ''.join(el[0] for el in data['w_title'].replace('№', '').split(' ')).upper() if len(data['w_title'].split(' ')) >= 1 else data['w_title']
    title = f"{data['author'].replace(' ', '_')}_{data['group']}_{subject_abb}_{work_title_abb}_{data['year']}г.docx"
    output_file = title if data['output_file'] == '' else data['output_file']
    if (len(sys.argv) in [2, 3]):
        output_path = os.path.join(sys.argv[1], output_file)
    else:
        print("...")
        output_path = os.path.join(os.getcwd(), output_file)
    doc.save(output_path)
    print(f"Файл сохранён: {output_path}")

data_titles = {
        'faculty': "Факультет",
        'caf': "Кафедра",
        'group': f'Группа (Enter для значения по умолчанию - {default['group']})',
        'w_title': "Имя работы (с номером или без)",
        'theme':"Тема работы",
        'subject':"Дисциплина",
        'author':f"Ваша Фамилия И.О. (Enter для значения по умолчанию - {default['author']})",
        'tutor':"Фамилия И.О. препода",
        'year':f"Год обучения (Enter для значения по умолчанию - {default['year']})",
        'output_file':"Название выходного файла (Enter для наименования по стандарту)"
    }

data = {
        'faculty': "",
        'caf': "",
        'w_title': "",
        'theme':"",
        'subject':"",
        'group': "",
        'author':"",
        'tutor':"",
        'year':"",
        'output_file':""
}

isCalled = False
if len(sys.argv) < 3:
    for key in data.keys():
        if key != 'faculty':
            data[key] = input(f'Введите значение для {data_titles[key]} \n->')

else:
    isCalled = True
    arg = sys.argv[2]
    raw_data = ast.literal_eval(arg)
    raw_data: dict
    for key, val in raw_data.items():
        for main_key, main_value in data_titles.items():
            if key in main_value:
                data[main_key] = val

   
for key in data.keys():
    if data[key] == '':
        if key in default.keys():
            data[key] = default[key]
        else:
            if isCalled:
                sys.exit()
    if key == 'theme':
        data[key] = f'«{data[key]}»' if data[key] != '' else ''
    if key == 'tutor':
        if len(data[key]) == 3:
            data[key] = data[key].upper()
            try:
                teacher = teachers[data[key]]
                if len(teacher) != 1:
                    print(f"    С аббревиатурой {data[key]} ассоциированы следующие преподаватели:")
                    for i in range(len(teacher)):
                        print (f'   {i+1}. {teacher[i]}')
                    choice = int(input("   Введите индекс нужного преподавателя -> "))
                    choice-=1
                    while choice >= len(teacher) or choice < 0:
                        choice = int(input("    Ошибка ввода. Введите индекс нужного преподавателя заново -> "))
                        choice -= 1
                    teacher = teacher[choice]
                else:
                    teacher = teacher[0]
                data[key] = teacher
            except:
                pass
    if key == 'caf':
        faculty = re.match(pattern, data[key]).group().upper()
        data['faculty'] = faculty + f' "{faculties[faculty]}"' 
        data[key] = data[key].upper() + f' "{cafedrals[data[key].upper()]}"'
    if key == 'w_title' and data['w_title'] != '':
        if data[key][0:2:].upper() in titles_shortcuts.keys():
            data[key] = titles_shortcuts[data[key][0:2:].upper()] + f'{' №' if len(data[key]) > 2 else ''}' + data[key][2::].replace('№', '')



fill_template(data)
