from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import json
import random
import time
from threading import Timer


class GodBot:
    def __init__(self, token):
        self.vk_session = vk_api.VkApi(token=token)
        self.admin = False
        self.ids = []
        self.reminder = {}
        self.session_api = self.vk_session.get_api()
        self.flag_dungeon = False
        self.flag_description = False
        self.cringe_locator = False
        self.longpoll = VkBotLongPoll(self.vk_session, '194508521')
        self.deleting = False
        self.flag_dungeon_on = False
        self.levels = {1: 100, 2: 300, 3: 900, 4: 2700, 5: 8100, 6: 10000}
        with open('heroes.json', 'r') as readfile:
            self.heroes = json.load(readfile)

    def message(self, event, text):
        self.session_api.messages.send(
            random_id=random.getrandbits(32),
            peer_id=event.obj.peer_id,
            message=text)

    def getusers(self, link_id):
        return self.vk_session.method('users.get', {'user_ids': link_id})

    def delete(self, event):
        return self.vk_session.method('messages.delete',
                                      {'message_ids': event.obj.peer_id, 'spam': 0, 'delete_for_all': 1})

    def getmembers(self, event):
        return self.vk_session.method('messages.getConversationMembers', {'peer_id': event.obj.peer_id})

    def remind(self, event, action):
        self.message(event, action)

    def rander(self, event, rng, mes=''):
        self.session_api.messages.send(
            random_id=random.getrandbits(32),
            peer_id=event.obj.peer_id,
            message=str(rng) + '. ' + mes)

    def commands(self, event):
        self.message(event, 'Вероятно, ты очень мало со мной знаком и не знаешь, на что я способен!\n'
                            'Я могу:\n'
                            'Кидать кубики. Напиши "/Рандом n", где n -  целое неотрицательное число.\n'
                            'Исключать участников беседы. /кик [упоминание] - исключение упомянутого участника. Для корректной работы боту нужна админка.\n'
                            'Генерировать игровые ситуации. Напиши "/сгенерируй встречу", и я смоделирую случайную. \n'
                            'Могу делать персонажей для миниигр. Создай персонажа по образцу:\n /новый перс \n [Имя]\n [Класс]\n'
                            "Вы можете узнать его характеристики по команде '/стата перса'\n"
                            'Если у вас уже есть персонаж, можете написать "/фарм", чтобы порезать парочку крыс.\n'
                            'Могу имитировать русскую рулетку. Просто напиши "/Русская рулетка" и наслаждайся. Для корректной работы боту нужна админка.\n'
                            'Могу устраивать общий сбор. Напиши "/позови всех", чтобы бот упомянул всех участников чата. Команда для админов конфы.\n'
                            '/запомнить [время в минутах] [действие] - напоминает вам сделать действие через некоторое время.\n'
                            'Список игровых команд можно узнать по команде /игра\n'
                            '/техподдержка [текст сообщения] - обращение к администратору по особо важным вопросам, касающихся бота: уведомление о багах, ошибках и т.д.. За злоупотребление и использование не по назначению можно легко получить бан.'
                     )

    def kicking(self, event, id):
        self.vk_session.method('messages.removeChatUser', {"user_id": id,
                                                           'member_id': id,
                                                           'chat_id': (event.obj.peer_id - 2000000000)})

    def main(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        e = self.getmembers(event)
                        ids = [ch[key] for ch in e['items'] for key in ch if (key == 'member_id' and int(ch[key]) > 0)]

                        admins = [ch[key] for ch in e['items'] for key in ch if
                                  (key == 'member_id' and 'is_admin' in ch and
                                   ch['is_admin'] is True)]
                        if event.obj.from_id in admins:
                            self.admin = True
                        text = event.obj.text.lower()
                        if text.startswith('/рандом'):
                            heralt = random.randint(1, int(text.split()[1]))
                            if heralt == 2:
                                self.rander(event, heralt, mes="Зачем тебе два меча, Ведьмак?")
                            else:
                                self.rander(event, heralt)

                        elif text == "/помощь":
                            self.commands(event)

                        elif text == '/игра':
                            self.message(event, '/сгенерируй встречу - случайно генерирует игровую ситуацию\n'
                                                '/болото событие - генерирует игровую ситуацию в болотной местности\n'
                                                '/атрибут [id пользователя] [название] [значение] [на что влияет] - присваивает игроку навык\n'
                                                '/снарядить [название предмета из инвентаря] - снаряжает персонажа предметом\n'
                                                '/каст [название навыка] [цель] - использует навык\n'
                                                '/побег - сбегает из битвы с монстром и полностью восстанавливает здоровье\n'
                                                '/очисти инвентарь - очищает инвентарь\n'
                                                '/дроп [название] [характеристики] [слот] - присваивает вашему персонажу предмет\n'
                                                'разделителями для всех команд являются переносы строки. Таким образом примером запроса будет:\n'
                                                '/дроп\n'
                                                'Меч рыцаря\n'
                                                '+100 к урону\n'
                                                'weapon')

                        elif text.startswith('/техподдержка'):
                            helper = text[13:]
                            admin_id = 219400207
                            user_info = self.getusers(event.obj.from_id)
                            self.session_api.messages.send(
                                random_id=random.getrandbits(32),
                                peer_id=admin_id,
                                message="Запрос отправил: [id{}|{} {}]\n"
                                        "Текст сообщения: \n{}".format(event.obj.from_id, user_info[0]['first_name'],
                                                                     user_info[0]['last_name'], helper))

                        elif text.startswith('/запомнить'):
                            time = int(text.split()[1])
                            action = 'Напоминаю ' + text[13:] + '!'
                            action = '[id{}|{}]'.format(event.obj.from_id, action)
                            self.reminder[str(event.obj.from_id)] = Timer(time * 60, self.remind, args=[event, action])
                            self.reminder[str(event.obj.from_id)].start()
                            self.message(event, "Напомню через {} минут".format(str(time)))

                        elif text == '/кикни всех':
                            if self.admin:
                                for ch in ids:
                                    if ch not in admins:
                                        self.kicking(event, ch)

                        elif text.startswith('/кик'):
                            self.kicking(event, text.split()[1][3:12])
                            self.message(event, 'Пока!')


                        elif text == '/позови всех':
                            if self.admin or event.obj.from_id in admins:
                                mes = ''
                                for ch in ids:
                                    mes += '[id' + str(ch) + '|.]' + ' '
                                self.message(event, mes)

                        elif text == '/русская рулетка':
                            bullets = [False, False, True, False, False, False]
                            if random.choice(bullets) is True:
                                try:
                                    self.kicking(event, event.obj.from_id)
                                except:
                                    self.message(event, 'Тебе пока везет.')
                            else:
                                self.message(event, 'Тебе пока везет.')

                        elif text == '/сгенерируй встречу':
                            if self.admin is True or self.admin is False:
                                first = random.randint(1, 100)
                                second = random.randint(1, 100)
                                extra = random.randint(1, 100)
                                specnumber = random.randint(1, 20)
                                third = str(random.randint(1, 4))
                                fourth = str(random.randint(1, 6))
                                fifth = str(random.randint(1, 10))
                                with open('meet.json', 'r') as readfile:
                                    meets = json.load(readfile)
                                with open('npcmoves.json', 'r') as readfile2:
                                    char = json.load(readfile2)
                                with open('npcs1.json') as readfile3:
                                    workers = json.load(readfile3)
                                with open('specs.json') as readfile4:
                                    specs = json.load(readfile4)
                                if first in [1, 2]:
                                    mess = workers[str(second)] + ": " + char[str(extra)]
                                    self.message(event, mess)
                                elif first in [3, 4]:
                                    mess = specs[str(specnumber)] + ': ' + char[str(extra)]
                                    self.message(event, mess)
                                else:
                                    mess = meets[str(first)] + ": " + char[str(second)]
                                    if '1d4' in mess:
                                        mess = mess.replace('1d4', third)
                                    if '1d6' in mess:
                                        mess = mess.replace('1d6', fourth)
                                    if '1d10' in mess:
                                        mess = mess.replace('1d10', fifth)
                                    self.message(event, mess)

                        elif text == '/болото событие':
                            if True:
                                first = random.randint(1, 100)
                                with open('swamp.json', 'r') as readfile:
                                    npc = json.load(readfile)
                                mess = npc[str(first)]
                                if '1d4' in mess:
                                    mess = mess.replace('1d4', random.randint(1, 4))
                                if '1d6' in mess:
                                    mess = mess.replace('1d6', random.randint(1, 6))
                                if '1d10' in mess:
                                    mess = mess.replace('1d10', random.randint(1, 10))
                                self.message(event, mess)

                        elif text == '/позови всех':
                            if self.admin or event.obj.from_id in admins:
                                mes = ''
                                for ch in ids:
                                    mes += '[id' + str(ch) + '|.]' + ' '
                                self.message(event, mes)

                        elif text.startswith('/рассылка'):
                            if event.obj.from_id == 219400207:
                                textt = event.obj.text.split('\n')
                                mess = textt[1]
                                for i in range(2000000000, 2000000099):
                                    try:
                                        self.session_api.messages.send(
                                            random_id=random.getrandbits(32),
                                            peer_id=i,
                                            message=mess)
                                    except:
                                        continue
                                self.message(event, 'Рассылка завершена')

                        elif text == '/фарм':
                            if True:
                                with open('heroes.json', 'r') as readfile5:
                                    hero = json.load(readfile5)[str(event.object.from_id)]
                                with open('enemies.json', 'r') as readfile6:
                                    if hero['fighting'] is None:
                                        enemies = json.load(readfile6)
                                        i = [value for [key, value] in enemies.items() if
                                             enemies[key]['level'] == hero['level']]
                                        enemy = random.choice(i)
                                        hero['fighting'] = enemy
                                    else:
                                        enemy = hero['fighting']
                                hero['health'] -= enemy['attack']
                                enemy['health'] -= hero['attack']
                                if hero['base_exp'] >= self.levels[hero['level']]:
                                    hero['level'] += 1
                                    hero['base_exp'] += 5
                                    hero['attack'] += 10 * hero['level']
                                    hero['max_mana'] += 20 * hero['level']
                                    hero['max_health'] += 40 * hero['level']
                                    hero['health'], hero['mana'] = hero['max_health'], hero['max_mana']
                                    self.message(event, 'Новый уровень! Получены новые характеристики.')

                                elif hero['health'] <= 0:
                                    self.message(event, 'Вы погибли. Возрождение через 3..2..1..')
                                    hero['fighting'] = None
                                    hero['health'] = hero['max_health']

                                if enemy['health'] <= 0:
                                    self.message(event,
                                                 'Победа! Вы получили {} опыта и {} золотых.'.format(enemy['experience'],
                                                                                                     enemy['gold']))
                                    hero['base_exp'] += enemy['experience']
                                    hero['gold'] += enemy['gold']
                                    hero['fighting'] = None
                                else:
                                    self.message(event, '{}, ты встретил монстра! Вы обменялись ударами.\n'
                                                        '{}: {} хп\n'
                                                        '{}: {} хп'.format(hero['name'], enemy['name'], enemy['health'],
                                                                           hero['name'],
                                                                           hero['health']))
                                with open('heroes.json', 'w') as writefile:
                                    self.heroes.update({str(event.obj.from_id): hero})
                                    json.dump(self.heroes, writefile)

                        elif text == '/стата перса':
                            hero = self.heroes[str(event.obj.from_id)]
                            self.message(event, 'Уровень: {}\n'
                                                'Здоровье: {}/{}\n'
                                                'Мана: {}/{}\n'
                                                'Опыт: {}\n'
                                                'Золото: {}\n'
                                                'Атака: {}\n'
                                                'Инвентарь: \n {}\n'
                                                'Снаряжение: \n'
                                                'Оружие: {}\n'
                                                'Наручи: {}\n'
                                                'Поножи: {}\n'
                                                'Ботинки: {}\n'
                                                'Голова: {}\n'
                                                'Плечи: {}\n'
                                                'Аксессуар: {}\n'
                                                'Аксессуар: {}\n'
                                                'Кольцо: {}\n'
                                                'Кольцо: {}\n'
                                                'Грудь: {}\n'
                                                'Запястья: {}'.format(hero['level'], hero['health'],
                                                                      hero['max_health'], hero['mana'],
                                                                      hero['max_mana'],
                                                                      hero['base_exp'], hero['gold'], hero['attack'],
                                                                      "\n".join(list(hero['inventory'].keys())),
                                                                      hero['equipment']['weapon'],
                                                                      hero['equipment']['arms'], hero['equipment']['legs'],
                                                                      hero['equipment']['boots'], hero['equipment']['head'],
                                                                      hero['equipment']['shoulders'],
                                                                      hero['equipment']['l_trinket'],
                                                                      hero['equipment']["r_trinket"],
                                                                      hero['equipment']['l_ring'],
                                                                      hero['equipment']["r_ring"],
                                                                      hero['equipment']['chest'],
                                                                      hero['equipment']['cuffs']))
                        elif text.startswith('/дроп'):
                            doc = event.obj.text.split('\n')
                            name = doc[1]
                            chars = doc[2]
                            slot = doc[3]
                            with open('heroes.json', 'r') as readfile5:
                                hero = json.load(readfile5)[str(event.object.from_id)]
                            hero['inventory'].update({name: {'chars': chars, 'slot': slot}})
                            with open('heroes.json', 'w') as writefile:
                                self.heroes.update({str(event.obj.from_id): hero})
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Зафиксировано.')

                        elif text.startswith('/снарядить'):
                            item = event.obj.text.split('\n')
                            name = item[1]
                            with open('heroes.json', 'r') as readfile5:
                                hero = json.load(readfile5)[str(event.object.from_id)]
                            hero['equipment'][hero['inventory'][name]['slot']].update(
                                {name: hero['inventory'][name]['chars']})
                            hero['inventory'].pop(name)
                            with open('heroes.json', 'w') as writefile:
                                self.heroes.update({str(event.obj.from_id): hero})
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Снаряжено.')

                        elif text == "/очисти инвентарь":
                            with open('heroes.json', 'r') as readfile5:
                                hero = json.load(readfile5)[str(event.object.from_id)]
                            hero['inventory'].clear()
                            with open('heroes.json', 'w') as writefile:
                                self.heroes.update({str(event.obj.from_id): hero})
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Очищено.')

                        elif text == '/выброси оружие':
                            with open('heroes.json', 'r') as readfile5:
                                hero = json.load(readfile5)[str(event.object.from_id)]
                            hero['equipment']['weapon'].clear()
                            with open('heroes.json', 'w') as writefile:
                                self.heroes.update({str(event.obj.from_id): hero})
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Выброшено.')

                        elif text.startswith('/новый перс'):
                            anketa = event.obj.text.split('\n')
                            name, clas = anketa[1], anketa[2]
                            self.heroes.update({str(event.obj.from_id):
                                                    {'name': name, 'class': clas, 'health': 120, 'mana': 60, 'max_mana': 60,
                                                     'max_health': 120, 'attack': 20, 'gold': 0, 'base_exp': 0, 'level': 1,
                                                     'fighting': None,
                                                     'inventory': {},
                                                     'equipment': {'weapon': {}, 'head': {}, 'shoulders': {}, 'boots': {},
                                                                   "legs": {}, 'arms': {},
                                                                   'cuffs': {}, 'chest': {}, "l_ring": {}, 'r_ring': {},
                                                                   "l_trinket": {}, 'r_trinket': {}}}})
                            with open('heroes.json', 'w') as writefile:
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Персонаж создан.')


                        elif text.startswith('/атрибут'):
                            attr = event.obj.text.split('\n')
                            link = attr[1]
                            attribute = attr[2]
                            value = attr[3]
                            affects = attr[4]
                            if value.isdigit() or value.startswith('-'):
                                value = int(attr[3])
                            self.heroes[str(link)].update({attribute: {'value': value, 'affects': affects}})
                            with open('heroes.json', 'w') as writefile:
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Атрибут добавлен.')

                        elif text.startswith('/каст'):
                            spells = event.obj.text.split('\n')
                            for ch in spells:
                                ch.rstrip()
                            spell = spells[1]
                            target = spells[2][3:12] if spells[2][11].isdigit() else spells[2][3:11]
                            self.heroes[str(target)][self.heroes[str(event.obj.from_id)][spell]['affects']] += int(
                                self.heroes[str(event.obj.from_id)][spell]['value'])
                            with open('heroes.json', 'w') as writefile:
                                json.dump(self.heroes, writefile)
                            self.message(event, 'Использовано.')

                        elif text == "/побег":
                            with open('heroes.json', 'r') as readfile5:
                                hero = json.load(readfile5)[str(event.object.from_id)]
                                hero['fighting'] = None
                                hero['health'] = hero['max_health']
                                with open('heroes.json', 'w') as writefile:
                                    self.heroes.update({str(event.obj.from_id): hero})
                                    json.dump(self.heroes, writefile)
                            self.message(event, 'Вы сбежали от монстра.')

                        elif text.startswith('/измени статы'):
                            stats = event.obj.text.split('\n')
                            link = stats[1]
                            stat_to_change = stats[2]
                            value = int(stats[3])
                            self.heroes[str(link)][stat_to_change] = value
                            with open('heroes.json', 'w') as writefile:
                                json.dump(self.heroes, writefile)
                            self.message(event, "Статы изменены.")

                        elif text.startswith('/дуэль'):
                            x = text.split()
                            link = x[2][3:12] if x[2][11].isdigit() else x[2][3:11]
                            page1 = self.getusers(link)[0]
                            page2 = self.getusers(event.object.from_id)[0]
                            if page1['id'] == 167028699:
                                winner = page1['first_name']
                            elif page2['id'] == 167028699:
                                winner = page2['first_name']
                            else:
                                winner = random.choice([page1['first_name'], page2['first_name']])
                            self.message(event, '{}: Ну и кто тут босс?\n\
                                                {} и {} сошлись в схватке. Победителем вышел {}.'.format(
                                page2['first_name'],
                                page2['first_name'],
                                page1['first_name'], winner))


                        elif text == '/врубай перчатку':
                            if self.admin:
                                ar = {random.choice(ids) for i in range(len(ids) // 2)}
                                while len(ar) != len(ids) // 2:
                                    a = random.choice(ids)
                                    if a not in admins:
                                        ar.add(a)
                                for ch in ar:
                                    print(ch)
                                    self.kicking(event, ch)

                    self.admin = False
            except Exception:
                continue


RunningDownTheRoad = GodBot("963247fc49e843e974fd2dde3cbaf039ae6f2856c973541fd6a6576ab279c87ad0f15f88282e94fd3a227")
RunningDownTheRoad.main()
