# coding: utf-8
"""Глобальная схема данных: база устройства (Room) и база сервера (PostgreSQL) рядом.

Рисуется вручную, а не mermaid: главное на этой схеме - соответствие таблиц, и оно читается,
только когда парные таблицы стоят строго друг напротив друга.
Источники: src/MedAppServer/db/schema.sql и Room-схема app/schemas/.../3.json.
"""
from xml.sax.saxutils import escape

BLUE, LILAC, YELLOW, PALE, SRV, GREY = '#102D69', '#DFC7F2', '#DCFF05', '#F7F5FC', '#E3E8F4', '#55607A'
FONT = "HSE Sans, Navigo, sans-serif"
W = 1600
L0, L1 = 30, 650          # панель устройства
R0, R1 = 950, 1570        # панель сервера
out = []


def text(x, y, s, size=17, weight='normal', color=BLUE, anchor='start', mono=False):
    fam = "Menlo, monospace" if mono else FONT
    out.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
               f'fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')


def box(x, y, w, h, name, note, fill):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{BLUE}" stroke-width="1.5"/>')
    text(x + 14, y + 26, name, size=16, weight='bold', mono=True)
    for i, line in enumerate(note.split('\n')):
        text(x + 14, y + 50 + i * 21, line, size=16)


def arrow(y, label):
    out.append(f'<line x1="{L1 + 8}" y1="{y}" x2="{R0 - 8}" y2="{y}" stroke="{BLUE}" stroke-width="1.6" '
               f'stroke-dasharray="6 5" marker-start="url(#a)" marker-end="url(#a)"/>')
    for i, line in enumerate(label.split('\n')):
        text((L1 + R0) / 2, y - 10 - (len(label.split('\n')) - 1 - i) * 20, line, size=15, anchor='middle')


# заголовки панелей
text((L0 + L1) / 2, 42, 'Устройство · Room (SQLite)', 22, 'bold', anchor='middle')
text((R0 + R1) / 2, 42, 'Сервер · PostgreSQL', 22, 'bold', anchor='middle')

# 1. Общее: синхронизируется
y = 72
text(L0, y + 8, 'СИНХРОНИЗИРУЕТСЯ', 14, 'bold', GREY)
pairs = [
    (('med_kits', 'название, место хранения,\nпризнак публикации'), ('med_kits', 'только идентификатор'),
     'аптечка: у сервера нет\nдаже названия'),
    (('packages', 'остаток, версия,\nверсия броней'), ('user_drugs', 'остаток, версия,\nсумма и версия броней'),
     'лекарство общей аптечки:\nостаток и версия'),
    (('claims', 'брони: сумма и своя'), ('reservations', 'бронь каждого участника,\nключ через членство'),
     'устройство знает сумму и свою бронь,\nсервер: бронь каждого'),
    (('drug_templates', 'снимок справочника'), ('parsed_drugs', 'справочник,\nнеточный поиск pg_trgm'),
     'подсказки при вводе'),
    (('form_types · quantity_units', 'формы и единицы'), ('form_types · quantity_units', 'формы и единицы'),
     'единый словарь:\n«шт» везде одна'),
]
y += 22
for (ln, lnote), (rn, rnote), label in pairs:
    h = 44 + 21 * max(len(lnote.split('\n')), len(rnote.split('\n')))
    box(L0, y, L1 - L0, h, ln, lnote, LILAC)
    box(R0, y, R1 - R0, h, rn, rnote, LILAC)
    arrow(y + h / 2 + 8, label)
    y += h + 14

# 2. Только на одной стороне
y += 20
text(L0, y + 8, 'ТОЛЬКО НА УСТРОЙСТВЕ', 14, 'bold', GREY)
text(R0, y + 8, 'ТОЛЬКО НА СЕРВЕРЕ', 14, 'bold', GREY)
y += 22
top = y
cw = (L1 - L0 - 14) / 2
local = [
    ('package_details', 'срок годности, доза, цена,\nзаметка, даты покупки', YELLOW),
    ('intakes', 'журнал приёмов', YELLOW),
    ('courses · course_times\ncourse_sources', 'курсы, расписание,\nисточники и порядок', YELLOW),
    ('course_records\ncoverage_reductions', 'история лечения,\nсокращения обеспечения', YELLOW),
    ('sync_operations\nsync_operation_dependencies', 'очередь, замороженный\nзапрос, записанный ответ', '#FFFFFF'),
    ('package_records · reminders\nactive_package_assignments', 'вечная запись о лекарстве,\nнапоминания', '#FFFFFF'),
]
for i, (name, note, fill) in enumerate(local):
    x = L0 + (i % 2) * (cw + 14)
    yy = top + (i // 2) * 118
    names = name.split('\n')
    out.append(f'<rect x="{x}" y="{yy}" width="{cw}" height="104" rx="8" fill="{fill}" stroke="{BLUE}" stroke-width="1.5"/>')
    for j, n in enumerate(names):
        text(x + 14, yy + 24 + j * 20, n, 15, 'bold', mono=True)
    for j, line in enumerate(note.split('\n')):
        text(x + 14, yy + 30 + len(names) * 20 + j * 20, line, 15)
box(R0, top, R1 - R0, 72, 'users', 'идентификатор и хеш ключа', SRV)
box(R0, top + 86, R1 - R0, 72, 'user_med_kits', 'членство в аптечках', SRV)
ny = top + 186
out.append(f'<rect x="{R0}" y="{ny}" width="{R1 - R0}" height="152" rx="8" fill="#FFFFFF" stroke="{BLUE}" stroke-width="1.5" stroke-dasharray="5 4"/>')
text(R0 + 14, ny + 28, 'На сервере нет:', 16, 'bold')
for j, line in enumerate(['имени, почты, телефона;', 'сроков годности, цен и заметок;',
                          'курсов лечения и журнала приёмов;', 'журналов обращений в промышленной сборке.']):
    text(R0 + 14, ny + 56 + j * 22, line, 16)
mid = top + 170
text((L1 + R0) / 2, mid - 12, 'на сервер', 16, 'bold', anchor='middle')
text((L1 + R0) / 2, mid + 10, 'не передаётся', 16, 'bold', anchor='middle')
out.append(f'<line x1="{L1 + 30}" y1="{mid + 34}" x2="{R0 - 30}" y2="{mid + 34}" stroke="{GREY}" stroke-width="1.6"/>')
cx = (L1 + R0) / 2
out.append(f'<path d="M{cx - 10} {mid + 24} L{cx + 10} {mid + 44} M{cx + 10} {mid + 24} L{cx - 10} {mid + 44}" stroke="#BA1A1A" stroke-width="3"/>')

# 3. Легенда
y = top + 3 * 118 + 24
for i, (fill, label) in enumerate([(LILAC, 'есть на обеих сторонах'), (YELLOW, 'личное: не покидает устройство'),
                                    (SRV, 'только на сервере'), ('#FFFFFF', 'служебное')]):
    x = L0 + i * 380
    out.append(f'<rect x="{x}" y="{y}" width="26" height="18" rx="4" fill="{fill}" stroke="{BLUE}"/>')
    text(x + 36, y + 15, label, 16)
H = y + 40

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       f'<path d="M0 0 L10 5 L0 10 z" fill="{BLUE}"/></marker></defs>'
       f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>' + ''.join(out) + '</svg>')
open('08-databases.svg', 'w').write(svg)
