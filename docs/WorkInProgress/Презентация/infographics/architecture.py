# coding: utf-8
"""Архитектура системы и путь одной операции (раздел 9 текста выступления).

Клиент — кольца Clean Architecture по AGENTS «Описание» и LayerBoundariesTest.maySee на main после
PR #87–#89; сервер — слои ARCHITECTURE.md; путь «Принял» — IntakeConfirmation, QueueService,
MedAppPacking/MedAppCourier, DrugSynchronisation, IntakeJournal.
"""
from svgkit import Canvas, BLUE, YELLOW, LILAC, SRV, PALE, WHITE, GREY, FONT

W, H = 1800, 1060
c = Canvas(W)


def badge(x, y, n):
    c.items.append(f'<circle cx="{x}" cy="{y}" r="17" fill="{BLUE}"/>')
    c.text(x, y + 7, str(n), 19, 'bold', WHITE, 'middle')


# Клиент: кольца
c.text(40, 40, 'Android-приложение · зависимости только внутрь', 24, 'bold')
rings = [
    (40, 60, 860, 760, PALE, 'Ведущие адаптеры: экраны (presentation, ui) и входы Android (app)'),
    (95, 125, 750, 630, WHITE, 'Ведомые адаптеры: storage (Room) · network (Ktor) · platform (устройство)'),
    (160, 195, 620, 490, LILAC, 'Сценарии: feature · поручения серверу: queue'),
    (300, 250, 340, 170, YELLOW, 'Домен'),
]
for x, y, w, h, fill, label in rings:
    c.rect(x, y, w, h, fill=fill, rx=28)
    c.text(x + 60, y + 36, label, 19, 'bold')
c.lines(322, 320, ['упаковка, аптечка, курс,', 'приём, доза — и решения', 'о них с причиной отказа'], 18)

# Что лежит в кольцах
c.lines(230, 480, ['IntakeConfirmation: ведёт действие',
                   'QueueService: выдаёт поручение',
                   'порты объявляют сами: IntakeRecords,',
                   'Courier, Packing, Transactions'], 18, step=28)
c.lines(160, 715, ['RoomTransactions, *RoomRepository исполняют порты',
                   'MedAppPacking собирает посылку, MedAppCourier везёт её'], 18, step=28)
c.text(70, 805, 'экран проверяет только ввод; данные наблюдает через порты чтения', 17, color=GREY)

# Сервер: слои
SX, SW = 1110, 520
c.text(SX, 40, 'Сервер · слои сверху вниз', 24, 'bold')
layers = ['Контроллер: перевод HTTP, коды ответа',
          'Прикладной сервис: владеет транзакцией',
          'Оркестратор: DrugSynchronisation',
          'Сервис агрегата и домен: правило',
          'Хранилище: Exposed, предикат версии']
ly = 70
for i, name in enumerate(layers):
    c.rect(SX, ly, SW, 70, fill=SRV)
    c.text(SX + 20, ly + 43, name, 19)
    if i:
        c.line(SX + SW / 2, ly - 22, SX + SW / 2, ly - 2, arrow=True)
    ly += 92
c.rect(SX, ly, SW, 70, fill=WHITE)
c.text(SX + 20, ly + 43, 'PostgreSQL: общие аптечки, брони, справочник', 19)
c.line(SX + SW / 2, ly - 22, SX + SW / 2, ly - 2, arrow=True)
c.rect(SX + SW + 20, 254, 150, 110, fill=YELLOW)
c.lines(SX + SW + 34, 290, ['журнал', 'повторов:', 'память, сутки'], 17, step=24)
c.line(SX + SW, 300, SX + SW + 18, 300, dash='5 4')

# Провод: запрос и ответ
c.line(902, 92, SX - 4, 92, width=2.2, arrow=True)
c.text(930, 78, 'PUT /sync/{номер}', 16, 'bold')
c.line(SX - 4, 128, 904, 128, width=2.2, dash='8 5', arrow=True)
c.text(930, 156, 'снимок пачки', 16, 'bold')

# Внешние
c.rect(SX, 640, 250, 80, fill=PALE, dash='6 4')
c.lines(SX + 20, 672, ['«Честный знак»', 'код маркировки'], 18, step=26)
c.line(902, 690, SX - 4, 690, dash='6 4', arrow=True)
c.rect(SX + 280, 640, 390, 80, fill=PALE, dash='6 4')
c.lines(SX + 300, 672, ['Сбор справочника: Python,', 'разово грузит в PostgreSQL'], 18, step=26)
c.line(SX + 450, 640, SX + 450, 626, arrow=True)

# Нумерация пути «Принял»
for n, x, y in ((1, 70, 90), (2, 205, 474), (3, 330, 280), (4, 205, 502), (5, 135, 709),
                (6, SX - 20, 60), (7, 860, 160)):
    badge(x, y, n)

steps = [
    '1. Человек нажимает «Принял» у приёма из общей пачки.',
    '2. Экран передаёт нажатие сценарию подтверждения приёма.',
    '3. Домен решает, можно ли принять из этой пачки.',
    '4. Одной транзакцией: приём записан, выделение курса пересчитано, очередь выдала поручение.',
    '5. Сеть читает пачку, собирает посылку по решению очереди и везёт её на сервер.',
    '6. Сервер: журнал повторов → бронь и расход одной транзакцией → запись в журнал после фиксации.',
    '7. Очередь толкует ответ: снимок пачки и закрытие поручения ложатся одной транзакцией.',
]
c.lines(40, 890, steps, 19, step=24)
c.save('11-architecture.svg', H)
