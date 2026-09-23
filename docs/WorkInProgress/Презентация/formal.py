# coding: utf-8
"""Сборка презентации к защите на официальном шаблоне ФКН НИУ ВШЭ.

Шрифты фирменные: заголовки набраны Navigo (шаблон ФКН), текст - HSE Sans из
брендбука университета: в мелком кегле он читается лучше, а начертаний у него больше.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

BLUE = RGBColor(0x10, 0x2D, 0x69)      # фирменный тёмно-синий ФКН
LILAC = RGBColor(0xDF, 0xC7, 0xF2)
YELLOW = RGBColor(0xDC, 0xFF, 0x05)
GREY = RGBColor(0x55, 0x5F, 0x77)
FONT = 'Navigo'                        # заголовки
FONT_BODY = 'HSE Sans'                 # текст, таблицы, подписи

W, H = Inches(13.333), Inches(7.5)
BODY_TOP, BODY_BOTTOM = Inches(2.33), Inches(6.98)


def drop_yandex(prs):
    """Логотип партнёрской программы из шаблона проекту не принадлежит."""
    for idx in (0, 5, 10):
        layout = prs.slide_layouts[idx]
        for sh in list(layout.shapes):
            # логотип «Яндекс» в подвале титульного макета
            if not sh.is_placeholder and sh.top > Inches(6.5) and sh.left < Inches(1.0):
                sh._element.getparent().remove(sh._element)


def clean(prs):
    """Убрать демонстрационные слайды шаблона."""
    ids = prs.slides._sldIdLst
    for sld in list(ids):
        prs.part.drop_rel(sld.rId)
        ids.remove(sld)


def no_bullet(p):
    """Снять маркер макета: списки размечаются здесь, а не наследуются."""
    pPr = p._p.get_or_add_pPr()
    for tag in ('a:buChar', 'a:buAutoNum', 'a:buNone'):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    # порядок элементов внутри a:pPr задан схемой: буллет идёт перед a:tabLst и a:defRPr
    pPr.insert_element_before(pPr.makeelement(qn('a:buNone'), {}), 'a:tabLst', 'a:defRPr', 'a:extLst')


def number(slide, n):
    """Номер слайда справа вверху, как в шаблоне ФКН."""
    box = slide.shapes.add_textbox(Inches(12.4), Inches(0.42), Inches(0.6), Inches(0.4))
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = str(n)
    r.font.size, r.font.color.rgb, r.font.name = Pt(14), BLUE, FONT_BODY


def title_slide(prs, **kw):
    s = prs.slides.add_slide(prs.slide_layouts[0])
    body, head = None, None
    for ph in s.placeholders:
        if ph.placeholder_format.idx == 10: body = ph
        else: head = ph
    tf = body.text_frame
    tf.word_wrap = True

    def line(text, size, bold=False, space_before=0, color=BLUE, font=FONT_BODY):
        p = tf.paragraphs[0] if not tf.paragraphs[0].runs and not tf.text else tf.add_paragraph()
        p.space_before = Pt(space_before)
        no_bullet(p)
        r = p.add_run(); r.text = text
        r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(size), bold, color, font
        return p

    line(kw['ru'], 30, bold=True, font=FONT)
    line(kw['en'], 15, space_before=10, color=GREY)
    line(kw['kind'], 15, space_before=14)
    line(kw['author'], 14, space_before=18)
    line(kw['supervisor'], 14)
    line(kw['place'], 12, space_before=18, color=GREY)
    head.text_frame.text = ''
    return s


def frame(prs, title, sub=None, title_size=30):
    """Заголовок и, если нужно, поясняющая строка под ним.

    Возвращает слайд, освободившийся текстовый плейсхолдер и верх, с которого
    начинается содержимое: подпись занимает своё место, а не наезжает на таблицу.
    """
    s = prs.slides.add_slide(prs.slide_layouts[5])
    t, body = None, None
    for ph in s.placeholders:
        if ph.placeholder_format.idx == 0: t = ph
        else: body = ph
    r = t.text_frame.paragraphs[0].add_run(); r.text = title
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(title_size), True, BLUE, FONT
    top = BODY_TOP
    if sub:
        box = s.shapes.add_textbox(Inches(0.56), top, Inches(12.24), Inches(0.66))
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        no_bullet(p)
        rr = p.add_run(); rr.text = sub
        rr.font.size, rr.font.color.rgb, rr.font.name = Pt(14), GREY, FONT_BODY
        top = Inches(3.05)
    return s, body, top


def hanging(p, left, hang):
    """Висячий отступ: перенесённая строка встаёт под текст, а не под маркер."""
    pPr = p._p.get_or_add_pPr()
    pPr.set('marL', str(int(left)))
    pPr.set('indent', str(int(-hang)))


def text_slide(prs, n, title, blocks, sub=None):
    """Слайд с заголовком и списком абзацев: (текст, уровень).

    Текст набирается в своей рамке во всю полосу: плейсхолдер шаблона разбит на две
    колонки, и список в нём рвётся посередине.
    """
    s, body, top = frame(prs, title, sub)
    body._element.getparent().remove(body._element)
    box = s.shapes.add_textbox(Inches(0.56), int(top), Inches(12.24), int(BODY_BOTTOM - top))
    tf = box.text_frame; tf.word_wrap = True
    first = True
    for text, level in blocks:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(14 if not level else 10)
        no_bullet(p)
        hanging(p, Inches(0.42) if level else 0, Inches(0.42) if level else 0)
        r = p.add_run(); r.text = ('\u2014 ' if level else '') + text
        r.font.size = Pt(19 if not level else 17)
        r.font.color.rgb = BLUE if not level else GREY
        r.font.name = FONT_BODY
    number(s, n)
    return s


def split_slide(prs, n, title, blocks, image, sub=None, share=0.47):
    """Тезисы слева, схема справа: вывод и его иллюстрация на одном слайде."""
    from PIL import Image as PILImage
    s, body, top = frame(prs, title, sub)
    body._element.getparent().remove(body._element)
    text_w = int(Inches(12.24) * share)
    box = s.shapes.add_textbox(Inches(0.56), int(top), text_w, int(BODY_BOTTOM - top))
    tf = box.text_frame; tf.word_wrap = True
    first = True
    for text, level in blocks:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(12 if not level else 8)
        no_bullet(p)
        hanging(p, Inches(0.38) if level else 0, Inches(0.38) if level else 0)
        r = p.add_run(); r.text = ('\u2014 ' if level else '') + text
        r.font.size = Pt(16 if not level else 14)
        r.font.color.rgb = BLUE if not level else GREY
        r.font.name = FONT_BODY

    iw, ih = PILImage.open(image).size
    max_w = Inches(12.24) - text_w - Inches(0.4)
    max_h = Inches(7.05) - top
    scale = min(max_w / iw, max_h / ih)
    w, h = int(iw * scale), int(ih * scale)
    x = Inches(0.56) + text_w + Inches(0.4) + int((max_w - w) / 2)
    s.shapes.add_picture(image, int(x), int(top) + int((max_h - h) / 2), w, h)
    number(s, n)
    return s


def picture_slide(prs, n, title, image, sub=None, height=None, top=None):
    """Слайд с заголовком и одним изображением, вписанным в оставшееся место."""
    from PIL import Image as PILImage
    s, body, auto_top = frame(prs, title, sub)
    body._element.getparent().remove(body._element)
    top = int(top) if top is not None else int(auto_top)

    iw, ih = PILImage.open(image).size
    max_w, max_h = Inches(12.24), height or (Inches(7.05) - top)
    scale = min(max_w / iw, max_h / ih)
    w, h = int(iw * scale), int(ih * scale)
    y = top + int((max_h - h) / 2)          # схема стоит по центру, а не жмётся к заголовку
    s.shapes.add_picture(image, int((W - w) / 2), y, w, h)
    number(s, n)
    return s


def table_slide(prs, n, title, head, rows, sub=None, col_widths=None, size=11):
    s, body, top = frame(prs, title, sub)
    body._element.getparent().remove(body._element)
    row_h = min(Inches(0.34), int((Inches(6.9) - top) / (len(rows) + 1)))
    shape = s.shapes.add_table(len(rows) + 1, len(head), Inches(0.56), int(top),
                               Inches(12.24), row_h * (len(rows) + 1))
    table = shape.table
    for r_ in table.rows:
        r_.height = int(row_h)
    if col_widths:
        for i, wd in enumerate(col_widths):
            table.columns[i].width = wd

    def fill(cell, text, bold, colour, align):
        cell.text = text
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_top = cell.margin_bottom = Inches(0.02)
        cell.margin_left = cell.margin_right = Inches(0.07)
        for p in cell.text_frame.paragraphs:
            p.alignment = align
            for run in p.runs:
                run.font.size, run.font.bold, run.font.name = Pt(size), bold, FONT_BODY
                run.font.color.rgb = colour

    for j, text in enumerate(head):
        cell = table.cell(0, j)
        fill(cell, text, True, RGBColor(0xFF, 0xFF, 0xFF), PP_ALIGN.CENTER if j else PP_ALIGN.LEFT)
        cell.fill.solid(); cell.fill.fore_color.rgb = BLUE
    for i, row in enumerate(rows, start=1):
        for j, text in enumerate(row):
            cell = table.cell(i, j)
            own = (j == len(row) - 1)
            fill(cell, text, own, BLUE, PP_ALIGN.CENTER if j else PP_ALIGN.LEFT)
            cell.fill.solid()
            # Полосы через строку убраны: они читались как цвет, который что-то значит. Выделена
            # только своя колонка - её и сравнивают со всеми остальными.
            cell.fill.fore_color.rgb = RGBColor(0xD9, 0xF2, 0xE4) if own else RGBColor(0xFF, 0xFF, 0xFF)
    number(s, n)
    return s


def screens_slide(prs, n, title, images, captions, sub=None):
    """Ряд снимков экрана с подписями."""
    from PIL import Image as PILImage
    s, body, top = frame(prs, title, sub)
    body._element.getparent().remove(body._element)

    max_h, gap = Inches(3.5), Inches(0.3)
    sizes = []
    for img in images:
        iw, ih = PILImage.open(img).size
        sizes.append((int(max_h * iw / ih), int(max_h)))
    total = sum(w for w, _ in sizes) + gap * (len(images) - 1)
    if total > Inches(12.24):                       # ряд не шире полосы набора
        k = Inches(12.24) / total
        sizes = [(int(w * k), int(h * k)) for w, h in sizes]
        total = sum(w for w, _ in sizes) + gap * (len(images) - 1)
    x = int((W - total) / 2)
    for (w, h), img, cap in zip(sizes, images, captions):
        s.shapes.add_picture(img, x, int(top), w, h)
        box = s.shapes.add_textbox(x - Inches(0.2), int(top) + h + Inches(0.06), w + Inches(0.4), Inches(0.36))
        p = box.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        no_bullet(p)
        rr = p.add_run(); rr.text = cap
        rr.font.size, rr.font.color.rgb, rr.font.name = Pt(12), GREY, FONT_BODY
        x += w + gap
    number(s, n)
    return s


SCR = '/Users/kert0n/Documents/SharedDocs/Programming/Projects/MedApp/src/AndroidApp/docs/screens'

def main():
    prs = Presentation('шаблон-ФКН.pptx')
    clean(prs)
    drop_yandex(prs)

    title_slide(
        prs,
        ru='Приложение для Android\n«Органайзер лекарств»',
        en='"Medicine Organizer" Android Application',
        kind='Индивидуальный | Программный',
        author='Выполнил: Волошин Никита, БПИ245',
        supervisor='Научный руководитель: Е. Ю. Песоцкая, к. э. н., доцент департамента\nпрограммной инженерии ФКН НИУ ВШЭ',
        place='Москва, 2026')

    text_slide(prs, 2, 'Предметная область', [
        ('Единица учёта - купленная упаковка: свой срок годности, свой остаток, обе величины меняются каждый день.', 0),
        ('Три вопроса, на которые отвечает программа:', 0),
        ('Что есть сейчас и где лежит.', 1),
        ('Чего не хватит до конца курса лечения.', 1),
        ('Что испортится раньше, чем его успеют принять.', 1),
        ('Программа не назначает лечение: она ведёт учёт, напоминает и согласует общий запас.', 0),
    ])

    text_slide(prs, 3, 'Актуальность', [
        ('Половина пациентов с хроническими заболеваниями принимает лекарства не так, как предписано (ВОЗ); '
         'причина чаще бытовая - забыли принять или не купили вовремя.', 0),
        ('Общая аптечка есть более чем у 90 % российских домохозяйств (опросы).', 0),
        ('Напоминание закрывает половину задачи - ту, что про время.', 0),
        ('Вторая половина про запас: пока напоминание срабатывает, лекарство из общей пачки могли уже допить.', 1),
        ('Эту половину не закрывает ни одно из рассмотренных приложений.', 1),
    ])

    text_slide(prs, 4, 'Цель и задачи',
        [('Проанализировать предметную область и существующие решения.', 1),
         ('Сформулировать требования к программе и согласовать техническое задание.', 1),
         ('Собрать справочник лекарственных препаратов, продающихся в РФ.', 1),
         ('Спроектировать модель предметной области: упаковка, курс лечения, приём, бронь.', 1),
         ('Разработать серверную часть: общие аптечки, брони, разрешение конкурентных изменений.', 1),
         ('Разработать Android-клиент: учёт, напоминания, сканирование, аналитика.', 1),
         ('Провести испытания и подготовить документацию по ГОСТ 19.', 1)],
        sub='Цель: разработать мобильное приложение для Android, которое ведёт учёт домашних аптечек, '
            'напоминает о приёмах и позволяет нескольким людям пользоваться одной аптечкой согласованно.')

    table_slide(prs, 5, 'Анализ аналогов',
        ['Возможность', 'Medisafe', 'MyTherapy', 'Домашняя аптечка', 'Аптечка. Учёт', 'Честный ЗНАК', 'MedApp'],
        [['Напоминания о приёме', '+', '+', '+', '+', '+', '+'],
         ['Учёт остатка упаковки', '+', '+', '+', '+', '-', '+'],
         ['Несколько мест хранения', '-', '-', '-', '+', '-', '+'],
         ['Контроль сроков годности', '-', '-', '+', '+', '+', '+'],
         ['Сканирование кода маркировки', '-', '-', '+', '+', '+', '+'],
         ['Общая аптечка с общим остатком', '-', '-', '-', '-', '-', '+'],
         ['Бронирование под курс лечения', '-', '-', '-', '-', '-', '+'],
         ['Работа без сети', '-', '+', '+', '+', '-', '+'],
         ['Учётная запись без имени и контактов', '-', '-', '-', '-', '-', '+']],
        sub='Medisafe (Medisafe Inc.), MyTherapy (smartpatient GmbH), «Домашняя аптечка» (открытый код, pewaru-333), '
            '«Аптечка. Учёт медикаментов» (DecSoft), «Честный ЗНАК» (ЦРПТ); по открытым описаниям, сентябрь 2026 г.',
        col_widths=[Inches(3.5)] + [Inches(1.45)] * 6)

    text_slide(prs, 6, 'Требования', [
        ('Учёт, который остаётся правдой', 0),
        ('Списание при приёме, сроки годности, места хранения, просроченное не теряется.', 1),
        ('Ответы о будущем, а не только о текущем', 0),
        ('Хватит ли до конца курса, что истечёт раньше, чем будет принято, сколько истрачено за период.', 1),
        ('Аптечка на несколько человек', 0),
        ('Остаток общий, решение о запасе личное: бронь под курс лечения.', 1),
        ('Сквозные требования ко всем трём группам: работа без сети и никаких персональных данных.', 0),
    ])

    text_slide(prs, 7, 'Средства реализации и обоснование', [
        ('Клиент: Kotlin (JetBrains), Jetpack Compose, Room, WorkManager, CameraX и ML Kit (Google), Ktor Client (JetBrains).', 1),
        ('Сервер: Kotlin, Spring Boot (Broadcom/VMware), Exposed (JetBrains), PostgreSQL, Testcontainers, Docker.', 1),
        ('Справочник: скраппер на Python (Scrapy, BeautifulSoup).', 1),
        ('Почему не ORM: форма SQL-запроса здесь часть требований - в запросе выражены доступ вызывающего, предикат версии и режим блокировки.', 0),
        ('JPA и Hibernate прячут текст запроса и момент обращения к базе: N+1 при чтении содержимого аптечки, ручные подсказки JOIN FETCH, несовместимость с неизменяемыми типами Kotlin.', 1),
        ('Exposed пишет запрос явно: число обращений видно в коде, план запроса проверяется испытанием.', 1),
    ])

    picture_slide(prs, 8, 'Архитектура системы', 'schemes/system.png',
                  sub='Три части с разной причиной меняться: клиент работает без сети, сервер - источник истины по общему остатку, '
                      'скраппер наполняет справочник мимо приложения.')

    text_slide(prs, 9, 'Модель предметной области', [
        ('Складывать одинаковые препараты в одну позицию нельзя:', 0),
        ('у двух пачек разные сроки годности, часто и разная дозировка;', 1),
        ('«одно лекарство» определить нечем - вещество, торговое название, комплектация и производитель '
         'дают четыре разных ответа.', 1),
        ('Что из этого следует:', 0),
        ('приём списывает дозу из конкретной пачки;', 1),
        ('курс хранит упаковки-источники и порядок: сначала то, что испортится раньше;', 1),
        ('бронь принадлежит человеку, а не серверу: она и есть его решение о запасе.', 1),
    ])

    split_slide(prs, 10, 'Приватность, доступ и конкурентность', [
        ('Пользователя как личности нет: идентификатор, хеш ключа, членство в аптечках и брони - ни имени, ни почты, ни телефона. Журнал приёмов на сервер не уходит.', 0),
        ('Отдельной проверки права нет: доступ выражен внутри запроса, чтение принимает вызывающего и этим же '
         'проверяет право.', 0),
        ('Прочитанное не даёт права писать: команда удерживает корень аптечки и перечитывает изменяемое под '
         'удержанием.', 0),
        ('Версия проверяется предикатом в самом UPDATE: ноль изменённых строк - гонка проиграна.', 0),
    ], 'schemes/race.png', share=0.40,
        sub='Требование ТЗ не обрабатывать персональные данные определило устройство сервера сильнее любой функции.')

    picture_slide(prs, 11, 'Работа без сети и синхронизация', 'schemes/offline.png',
                  sub='Изменение и команда к серверу записываются одной транзакцией. Перед отправкой команда собирается '
                      'заново по свежему состоянию: запрос уходит, либо операция закрывается без сервера - отказом '
                      '(состояние негодно) или применённой (на сервере уже так).')

    screens_slide(prs, 12, 'Особенности реализации: экраны',
        [f'{SCR}/02-med-kits/filled.png', f'{SCR}/06-package-card/on-course.png', f'{SCR}/12-day/today.png',
         f'{SCR}/16-course-sources/stack.png', f'{SCR}/20-sharing/shared.png', f'{SCR}/26-reports/summary.png',
         f'{SCR}/29-notification/shade.png'],
        ['Аптечки', 'Карточка упаковки', 'План дня', 'Источники курса', 'Приглашение', 'Отчёты', 'Напоминание'],
        sub='28 экранов, Material 3. Цвет нигде не единственный носитель: рядом всегда текст и значок.')

    text_slide(prs, 13, 'Испытания', [
        ('1130 проверок без устройства и 957 инструментальных на двух устройствах: Android 10 (360×640 dp) '
         'и большой экран с крупным шрифтом.', 1),
        ('Гонки проверяются настоящими параллельными транзакциями: проверка задерживает одну и убеждается, '
         'что вторая получает отказ по версии.', 1),
        ('Планы запросов проверяются на 40 000 строк: число обращений к базе не растёт с объёмом данных.', 1),
        ('Границы слоёв проверяются по дереву исходных текстов и байт-коду - нарушение роняет сборку.', 1),
        ('38 сквозных историй людей - 21 на клиенте и 17 на сервере: каждая проходит путь человека целиком.', 1),
        ('Контракт сервера порождается самой программой и проверяется против боевого сервера.', 1),
    ])

    text_slide(prs, 14, 'Результаты', [
        ('Учёт упаковок: сроки годности, места хранения, списание при приёме, пересчёт и перенос.', 1),
        ('Курсы лечения: расписание, напоминания, ответ по каждому приёму, упаковки-источники и порядок их расходования.', 1),
        ('Общая аптечка: приглашение по коду, общий остаток на несколько устройств, бронь под курс.', 1),
        ('Работа без сети целиком: очередь операций, повтор тем же запросом, разбор отказов.', 1),
        ('Сканирование кода маркировки со справочником препаратов и аналитика: остаток, расход до даты, истраченное.', 1),
        ('Подготовлена документация по ГОСТ 19: ТЗ, ПЗ, руководство оператора, ПМИ, текст программы.', 1),
        ('Достигнуто главное отличие от аналогов: общий остаток и бронь под курс лечения - без учётной записи, имени и контактов.', 0),
    ])

    text_slide(prs, 15, 'Развитие', [
        ('Заявленный объём работ выполнен и проверен; развитие ведётся задачами в репозиториях проекта.', 0),
        ('Клиент: расписания «через день» и «каждые N дней» - цикл вместо недельной сетки; правка записанных '
         'ответов и просмотр прошлых дней; кэш справочника с подсказками и поиском без сети.', 1),
        ('Сервер: разграничение доступа политиками самой базы - второй рубеж поверх предиката в запросе; '
         'журнал повторов в постоянном хранилище; свой предел размера тела запроса.', 1),
        ('Доступность: полная поддержка экранного чтеца и проверка на TalkBack.', 1),
        ('Публикация в RuStore и подготовка страницы приложения.', 1),
    ])

    text_slide(prs, 16, 'Источники', [
        ('ГОСТ 19.101-77, 19.201-78, 19.301-79, 19.401-78, 19.404-79, 19.505-79. Единая система программной документации.', 1),
        ('Adherence to long-term therapies: evidence for action. World Health Organization, 2003.', 1),
        ('Kotlin, Exposed, Ktor - JetBrains. URL: kotlinlang.org, jetbrains.com/help/exposed', 1),
        ('Jetpack Compose, Room, WorkManager, ML Kit - Google. URL: developer.android.com', 1),
        ('Spring Boot - Broadcom (VMware Tanzu). URL: docs.spring.io/spring-boot', 1),
        ('PostgreSQL Global Development Group. URL: postgresql.org/docs', 1),
        ('Medisafe (Medisafe Inc.), MyTherapy (smartpatient GmbH), «Домашняя аптечка» (pewaru-333), «Аптечка. Учёт медикаментов» (DecSoft), «Честный ЗНАК» (ЦРПТ).', 1),
        ('Репозитории проекта: github.com/Kert0n/MedAppDocs, MedAppAndroid, MedAppServer', 1),
    ])

    s, body, top = frame(prs, 'Демонстрация', title_size=40)
    body._element.getparent().remove(body._element)
    box = s.shapes.add_textbox(Inches(0.56), int(top), Inches(12.24), int(BODY_BOTTOM - top))
    tf = box.text_frame; tf.word_wrap = True
    for text, size in (('Показ приложения вживую', 22), ('', 10),
                       ('Спасибо за внимание. Готов ответить на вопросы.', 20)):
        p = tf.paragraphs[0] if not tf.paragraphs[0].runs else tf.add_paragraph()
        no_bullet(p)
        rr = p.add_run(); rr.text = text
        rr.font.size, rr.font.color.rgb, rr.font.name = Pt(size), BLUE, FONT_BODY
    number(s, 17)

    prs.save('Презентация (формальная).pptx')
    print('слайдов собрано:', len(prs.slides.__iter__.__self__._sldIdLst))


if __name__ == '__main__':
    main()
