# This pyfile for scripts
# This scripts is parts of any big projects


#function of choice parcer by name (Weather project)
def parser_choice(site_name_):
    if site_name_ == 'Yandex.ru':
        return parse_yandex(html)
    elif site_name_ == 'Gismeteo':
        return  parse_gismeteo(html)
    elif site_name_ == 'mail.ru':
        return parse_mailru(html)
    else: 
        print('Ошибка! %s нет в списке' %site_name)
        break



#function of  convert list to string
def list_to_str(temps, symb):
    symb = str(symb)
    temp_str = str()
    for temp_ in temps: # превращаем список в строку '1,2,3,'
        temp_str += str(temp_ + symb)
    return temp_str[:-1]



# Write to bd result of web-parsing (Weather project)
def Rewrite_DB():    
    
    id_edit = list() # создаю список с измененными ИД в таблице Temps

    # в списке лежат все id и имена городов из таблицы с городами
    cities_all = list(Cities.objects.values_list('id', 'City_name_short'))

    # В спискележат все id и названия сайтов
    sites_all = list(Sites.objects.values_list('id','Site_name'))

    #Для каждого города
    for city in cities_all:
        city_id = city[0]
        city_name = city[1]

        #Для каждого сайта
        for site in sites_all:
            site_id = site[0]
            site_name = site[1]

            #Выдергиваем из базы html
            html = Sites_links.objects.filter(Site_id = site_id, Cities_id = city_id).values_list('Refer')[0][0]

            #узнаем какой парсер применять
            parses = parser_choice(site_name)

            #цикл обработки парса
            n = 0 # счетчик для определения глубины дня (0 - сегодня, 1 - завтра...)
            for parse in parses:

                date = parse['datetime']

                # создание списка, который вставится в температуру
                def list_for_temp (n_, parse_, *temporal_):
                    
                    if temporal_:   #если запись в бд есть, то используется она
                        temp = temporal_[0].split(',')
                    else:           #если записи в бд нет, то создается новая
                        temp = list('' for c in range(10)) 
                    
                    temp.pop(n_) # удаляем заменяемое значение
                    temp.insert(n_, parse_) # вставляем новое значение получаем список вида ('1','2','3')


                    # превращение списка в строку
                    return list_for_temp(temp, ',')


                id_temp_ = list(Temps.objects.filter(Date = date, City_id = city_id, Site_id = site_id).values('id','temp_day','temp_night'))
                #проверка наличия в таблице с температурами даты города и сайта, если есть то дописываем
                if id_temp_:
                    day_temp = list_for_temp(n, parse['day_temp'], id_temp_[0]['temp_day'])
                    night_temp = list_for_temp(n, parse['night_temp'], id_temp_[0]['temp_night'])
                    save = Temps.objects.filter(id = id_temp_[0]['id'])
                    save.update(temp_day = day_temp, temp_night = night_temp)


                ## если нет, то содаем новую запись
                else:
                    day_temp = list_for_temp(n, parse['day_temp'])
                    night_temp = list_for_temp(n, parse['night_temp'])
                    city_id_db = Cities.objects.get(id= city_id)
                    site_id_db = Sites.objects.get(id= site_id)
                    save = Temps(Date = date, City_id= city_id_db, Site_id= site_id_db, temp_day = day_temp, temp_night = night_temp )
                    save.save()

                n +=1 #переходим на завтра


