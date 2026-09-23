# coding: utf-8
"""Презентация к защите MedApp.

Собирается вокруг **кадров настоящего интерфейса**: почти каждое утверждение доклада подтверждается
экраном из коллекции `src/AndroidApp/docs/screens`, а не прямоугольником со стрелкой. Схема здесь
ровно одна - устройство системы, для которого интерфейса не существует.

Файл организован по макетам: `cover`, `hero`, `triptych`, `versus`, `table`, `prose`, `scheme`,
`numbers`. Слайд описывается данными и собирается одним из них - поэтому у всех слайдов одинаковые
поля, один вертикальный ритм и одна логика цвета.

Цвета - палитра самого приложения (`ui/theme/Color.kt`, `Accents.kt`): зелёный значит «применено»,
янтарь «ждём», красный «отказ» - ровно как на снимках. Шрифты фирменные: Navigo в заголовках,
HSE Sans в тексте.
"""
import os
import re
import zipfile

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# ---------------------------------------------------------------- палитра и метрики

INK    = RGBColor(0x10, 0x2D, 0x69)     # ФКН: заголовки и основной текст
GREEN  = RGBColor(0x1B, 0x6B, 0x4A)     # продукт: сделано, применено
MINT   = RGBColor(0xA8, 0xF0, 0xC6)
WASH   = RGBColor(0xF2, 0xF7, 0xF0)     # подложка кадра
TEAL   = RGBColor(0x3B, 0x64, 0x70)
AMBER  = RGBColor(0x8A, 0x5A, 0x00)     # ждём
SAND   = RGBColor(0xFF, 0xDE, 0xA6)
RUST   = RGBColor(0xBA, 0x1A, 0x1A)     # отказ
BLUSH  = RGBColor(0xFF, 0xDA, 0xD6)
MUTE   = RGBColor(0x55, 0x5F, 0x77)
HAIR   = RGBColor(0xDD, 0xE4, 0xDB)     # тонкие линии и рамки
GHOST  = RGBColor(0x9A, 0xA3, 0xB2)
PAPER  = RGBColor(0xFF, 0xFF, 0xFF)
NIGHT  = RGBColor(0x0C, 0x23, 0x52)

HEAD, BODY = 'Navigo', 'HSE Sans'

W, H = Inches(13.333), Inches(7.5)
EDGE = Inches(0.7)                      # поле
SPAN = W - EDGE * 2                     # полоса набора
KICKER_Y = Inches(0.62)                 # рубрика - на одной высоте у всех слайдов
TITLE_Y = Inches(1.04)
CANVAS_Y = Inches(2.0)                  # верх содержимого, если подписи под заголовком нет

SCREENS = '/Users/kert0n/Documents/SharedDocs/Programming/Projects/MedApp/src/AndroidApp/docs/screens'
ASSETS = 'assets'
CROPPED = os.path.join(ASSETS, 'cropped')


# ---------------------------------------------------------------- текст и фигуры

def _plain(p):
    """Маркеры приходят из умолчаний python-pptx; списки размечаются здесь."""
    pPr = p._p.get_or_add_pPr()
    for tag in ('a:buChar', 'a:buAutoNum', 'a:buNone'):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    pPr.insert_element_before(pPr.makeelement(qn('a:buNone'), {}), 'a:tabLst', 'a:defRPr', 'a:extLst')


def frame(s, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """Текстовая рамка без полей: положение задаём мы."""
    tb = s.shapes.add_textbox(int(x), int(y), int(w), int(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.paragraphs[0].alignment = align
    return tf


def say(tf, value, size, colour=INK, font=BODY, bold=False, before=0, leading=None,
        align=None, italic=False):
    p = tf.paragraphs[0] if (not tf.paragraphs[0].runs and not tf.text) else tf.add_paragraph()
    _plain(p)
    p.space_before, p.space_after = Pt(before), Pt(0)
    if align is not None:
        p.alignment = align
    if leading:
        p.line_spacing = leading
    r = p.add_run(); r.text = value
    r.font.size, r.font.bold, r.font.italic = Pt(size), bold, italic
    r.font.color.rgb, r.font.name = colour, font
    return p


def label(s, x, y, w, h, value, size, colour=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
          anchor=MSO_ANCHOR.TOP, leading=None):
    """Одна строка (или абзац) в своей рамке."""
    tf = frame(s, x, y, w, h, align, anchor)
    say(tf, value, size, colour, font, bold, leading=leading)
    return tf


def block(s, x, y, w, h, fill, radius=None, edge=None, width=1.0):
    shape_kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = s.shapes.add_shape(shape_kind, int(x), int(y), int(w), int(h))
    if radius:
        sh.adjustments[0] = radius
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if edge is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb, sh.line.width = edge, Pt(width)
    sh.shadow.inherit = False
    sh.text_frame.text = ''
    return sh


def pointer(s, x1, y1, x2, y2, colour=GHOST, width=1.5):
    sh = s.shapes.add_connector(2, int(x1), int(y1), int(x2), int(y2))
    sh.line.color.rgb, sh.line.width = colour, Pt(width)
    el = sh.line._get_or_add_ln()
    el.append(el.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return sh


# ---------------------------------------------------------------- кадр интерфейса

def _find(name):
    """Снимки зовутся «экран/состояние»: расширение дописывается здесь."""
    path = os.path.join(SCREENS, name if name.endswith('.png') else name + '.png')
    if not os.path.exists(path):
        raise FileNotFoundError(f'нет снимка {name}')
    return path


def _trim(path):
    """Обрезать пустой низ снимка.

    Экраны сняты целиком, и у большинства нижняя треть - пустой фон. Вставленный как есть, такой
    снимок читается «полупустым телефоном», поэтому кадр режется по последней строке, где ещё есть
    содержимое. Фон определяется по самому нижнему ряду пикселей, а не задаётся числом: у светлой
    и тёмной темы он разный.
    """
    os.makedirs(CROPPED, exist_ok=True)
    out = os.path.join(CROPPED, path.replace(SCREENS + '/', '').replace('/', '-'))
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(path):
        return out

    im = Image.open(path).convert('RGB')
    w, h = im.size
    small = im.resize((w // 4, h // 4))
    sw, sh_ = small.size
    pixels = small.load()
    back = pixels[sw // 2, sh_ - 2]

    def busy(row):
        different = 0
        for col in range(0, sw, 2):
            r, g, b = pixels[col, row]
            if abs(r - back[0]) + abs(g - back[1]) + abs(b - back[2]) > 24:
                different += 1
        return different > sw // 90

    last = sh_ - 1
    while last > sh_ // 3 and not busy(last):
        last -= 1
    bottom = min(h, int((last + 3) * 4))
    im.crop((0, 0, w, bottom)).save(out)
    return out


def shot(s, name, x, y, height, caption=None, caption_colour=MUTE):
    """Кадр интерфейса: подложка, рамка, сам снимок и подпись под ним.

    Возвращает ширину - по ней выкладываются соседние кадры.
    """
    path = _trim(_find(name))
    iw, ih = Image.open(path).size
    w = int(height * iw / ih)
    pad = Inches(0.06)
    block(s, x - pad, y - pad, w + pad * 2, int(height) + pad * 2, WASH, radius=0.03, edge=HAIR)
    s.shapes.add_picture(path, int(x), int(y), w, int(height))
    if caption:
        tf = frame(s, x - Inches(0.1), y + height + Inches(0.18), w + Inches(0.2), Inches(0.6))
        say(tf, caption, 12, caption_colour, align=PP_ALIGN.CENTER)
    return w


# ---------------------------------------------------------------- макеты

def sheet(prs, number=None, kicker=None, title=None, lead=None, dark=False):
    """Общая шапка: рубрика, заголовок, при нужде - поясняющая строка. Возвращает слайд и верх
    свободного места. Заголовки у всех слайдов стоят на одной высоте."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if dark:
        block(s, 0, 0, W, H, NIGHT)
    if kicker:
        block(s, EDGE, KICKER_Y + Inches(0.05), Inches(0.13), Inches(0.2), GREEN)
        label(s, EDGE + Inches(0.28), KICKER_Y, Inches(9), Inches(0.28), kicker.upper(), 12, GREEN,
              bold=True)
    if title:
        label(s, EDGE, TITLE_Y, SPAN, Inches(0.72), title, 33, PAPER if dark else INK, font=HEAD,
              bold=True)
    y = CANVAS_Y
    if lead:
        tf = frame(s, EDGE, Inches(1.92), SPAN, Inches(0.6))
        say(tf, lead, 14, MUTE)
        y = Inches(2.52)
    if number is not None:
        label(s, W - Inches(1.3), Inches(6.78), Inches(0.6), Inches(0.3), str(number), 13,
              MINT if dark else GHOST, align=PP_ALIGN.RIGHT)
    return s, y


def cover(prs, **kw):
    """Обложка: титульная и финальная."""
    dark = kw.get('dark', False)
    s, _ = sheet(prs, number=kw.get('number'), dark=dark)
    if not dark:
        block(s, 0, 0, W, Inches(0.15), GREEN)
        s.shapes.add_picture(os.path.join(ASSETS, 'logo-fcs.png'), int(EDGE), int(Inches(0.62)),
                             int(Inches(1.5)), int(Inches(0.29)))
        s.shapes.add_picture(os.path.join(ASSETS, 'logo-hse.png'), int(EDGE + Inches(1.8)),
                             int(Inches(0.5)), int(Inches(0.52)), int(Inches(0.52)))

    # мотив: блистер, три ячейки уже приняты
    taken = {(0, 0), (0, 1), (1, 0)}
    empty = RGBColor(0x1C, 0x3C, 0x7E) if dark else RGBColor(0xE6, 0xEC, 0xE4)
    for row in range(5):
        for col in range(4):
            block(s, Inches(9.55) + col * Inches(0.78), Inches(1.3) + row * Inches(0.78),
                  Inches(0.56), Inches(0.56), GREEN if (row, col) in taken else empty, radius=0.5)

    tf = frame(s, EDGE, Inches(2.2), Inches(8.3), Inches(2.4))
    for i, (value, size, colour) in enumerate(kw['head']):
        say(tf, value, size, colour, font=HEAD, bold=True, leading=0.95, before=0 if i == 0 else 2)
    if kw.get('under'):
        say(tf, kw['under'], 15, MINT if dark else MUTE, before=18)

    if kw.get('lines'):
        block(s, EDGE, Inches(4.86), Inches(2.2), Inches(0.03), GREEN)
        tf = frame(s, EDGE, Inches(5.12), Inches(8.4), Inches(1.9))
        for i, (value, size, colour, bold) in enumerate(kw['lines']):
            say(tf, value, size, colour, bold=bold, before=0 if i == 0 else 11)

    if kw.get('qr'):
        block(s, EDGE, Inches(5.94), Inches(3.4), Inches(1.14), PAPER, radius=0.08)
        s.shapes.add_picture(os.path.join(ASSETS, 'qr-repos.png'), int(EDGE + Inches(0.18)),
                             int(Inches(6.09)), int(Inches(0.84)), int(Inches(0.84)))
        label(s, EDGE + Inches(1.2), Inches(6.2), Inches(2.1), Inches(0.3), 'Репозитории проекта',
              12, INK, bold=True)
        label(s, EDGE + Inches(1.2), Inches(6.46), Inches(2.1), Inches(0.3), 'github.com/Kert0n',
              11, GREEN)
    return s


def hero(prs, number, kicker, title, screen, points, accent=None, lead=None, caption=None):
    """Кадр слева, мысль справа: экран показывает то, о чём идёт речь."""
    s, y = sheet(prs, number, kicker, title, lead)
    height = Inches(4.05) if lead else Inches(4.35)
    width = shot(s, screen, EDGE, y, height, caption)
    x = EDGE + width + Inches(0.9)
    right = W - EDGE - x
    ty = y + Inches(0.06)
    for head, tail in points:
        block(s, x, ty + Inches(0.05), Inches(0.05), Inches(0.62), GREEN)
        label(s, x + Inches(0.26), ty, right - Inches(0.3), Inches(0.34), head, 19, INK, bold=True)
        tf = frame(s, x + Inches(0.26), ty + Inches(0.38), right - Inches(0.3), Inches(0.8))
        say(tf, tail, 14, MUTE)
        ty += Inches(1.18)
    if accent:
        block(s, x, ty + Inches(0.1), right, Inches(0.86), MINT, radius=0.1)
        tf = frame(s, x + Inches(0.32), ty + Inches(0.28), right - Inches(0.64), Inches(0.6))
        say(tf, accent, 15, INK, bold=True)
    return s


def triptych(prs, number, kicker, title, panels, lead=None):
    """Три кадра в ряд: каждый - доказательство своей строки."""
    s, y = sheet(prs, number, kicker, title, lead)
    height = Inches(3.16)
    gap = Inches(0.62)
    widths = []
    for name, *_ in panels:
        path = _trim(_find(name))
        iw, ih = Image.open(path).size
        widths.append(height * iw / ih)
    total = sum(widths) + gap * (len(panels) - 1)
    x = (W - total) / 2
    for (name, head, tail, colour), width in zip(panels, widths):
        shot(s, name, x, y, height)
        # Подпись держится в пределах своего кадра с небольшим запасом: шире - и соседние
        # столбцы наезжают друг на друга.
        room = width + Inches(0.56)
        label(s, x - Inches(0.28), y + height + Inches(0.24), room, Inches(0.52), head, 14, colour,
              bold=True, align=PP_ALIGN.CENTER, leading=1.1)
        tf = frame(s, x - Inches(0.28), y + height + Inches(0.8), room, Inches(0.9),
                   align=PP_ALIGN.CENTER)
        say(tf, tail, 12, MUTE, align=PP_ALIGN.CENTER, leading=1.15)
        x += width + gap
    return s


def versus(prs, number, kicker, title, left, right, middle, lead=None):
    """Два кадра по краям и лента событий между ними."""
    s, y = sheet(prs, number, kicker, title, lead)
    height = Inches(3.45)
    lw = shot(s, left['screen'], EDGE, y, height)
    rw_path = _trim(_find(right['screen']))
    iw, ih = Image.open(rw_path).size
    rw = int(height * iw / ih)
    shot(s, right['screen'], W - EDGE - rw, y, height)

    for side, x, width in ((left, EDGE, lw), (right, W - EDGE - rw, rw)):
        label(s, x - Inches(0.2), y + height + Inches(0.22), width + Inches(0.4), Inches(0.3),
              side['head'], 15, side['colour'], bold=True, align=PP_ALIGN.CENTER)
        tf = frame(s, x - Inches(0.2), y + height + Inches(0.52), width + Inches(0.4), Inches(0.6),
                   align=PP_ALIGN.CENTER)
        say(tf, side['note'], 11, MUTE, align=PP_ALIGN.CENTER, leading=1.1)

    x0 = EDGE + lw + Inches(0.5)
    band = W - EDGE - rw - Inches(0.5) - x0
    ty = y + Inches(0.1)
    for i, (head, tail, colour, fill) in enumerate(middle):
        block(s, x0, ty, band, Inches(0.72), fill, radius=0.12)
        label(s, x0 + Inches(0.26), ty + Inches(0.13), band - Inches(0.5), Inches(0.28), head, 14,
              INK, bold=True)
        label(s, x0 + Inches(0.26), ty + Inches(0.42), band - Inches(0.5), Inches(0.28), tail, 12,
              colour)
        if i < len(middle) - 1:
            pointer(s, x0 + band / 2, ty + Inches(0.74), x0 + band / 2, ty + Inches(0.92), GHOST)
        ty += Inches(0.96)
    return s


def table(prs, number, kicker, title, columns, rows, footer=None, lead=None):
    """Таблица сравнения: у каждой колонки имя и автор, своя колонка подсвечена целиком."""
    s, y = sheet(prs, number, kicker, title, lead)
    name_w = Inches(3.84)
    col_w = (SPAN - name_w) / len(columns)
    head_h, row_h = Inches(0.66), Inches(0.35)
    mine = len(columns) - 1
    block(s, EDGE + name_w + mine * col_w, y, col_w, head_h + len(rows) * row_h + Inches(0.08),
          MINT, radius=0.04)
    for j, (name, author) in enumerate(columns):
        x = EDGE + name_w + j * col_w
        own = (j == mine)
        label(s, x, y + Inches(0.08), col_w, Inches(0.26), name, 11, GREEN if own else INK,
              bold=own, align=PP_ALIGN.CENTER)
        label(s, x, y + Inches(0.34), col_w, Inches(0.24), author, 9, GREEN if own else MUTE,
              align=PP_ALIGN.CENTER)
    for i, (name, values) in enumerate(rows):
        ry = y + head_h + i * row_h
        if i:
            block(s, EDGE, ry, name_w + mine * col_w, Inches(0.01), HAIR)
        label(s, EDGE + Inches(0.14), ry + Inches(0.07), name_w - Inches(0.2), Inches(0.28), name,
              12, INK)
        for j, has in enumerate(values):
            own = (j == mine)
            label(s, EDGE + name_w + j * col_w, ry + Inches(0.05), col_w, Inches(0.3),
                  '+' if has else '–',            # в HSE Sans нет знака минус
                  15 if own else 13, (GREEN if own else INK) if has else GHOST, bold=own,
                  align=PP_ALIGN.CENTER)
    if footer:
        tf = frame(s, EDGE, y + head_h + len(rows) * row_h + Inches(0.26), SPAN, Inches(0.4))
        say(tf, footer, 15, INK, bold=True)
    return s


def prose(prs, number, kicker, title, lead=None, banner=None, columns=None, pairs=None,
          numbered=None, note=None, outro=None):
    """Текстовый слайд: плашка, колонки, пары «что - чем» или нумерованный список."""
    s, y = sheet(prs, number, kicker, title, lead)
    if banner:
        lines = max(1, -(-len(banner[1]) // 96))          # сколько строк займёт текст плашки
        tall = Inches(0.72) + Inches(0.28) * lines
        block(s, EDGE, y, SPAN, tall, MINT, radius=0.07)
        tf = frame(s, EDGE + Inches(0.44), y + Inches(0.22), SPAN - Inches(0.9), tall - Inches(0.3))
        say(tf, banner[0], 11, GREEN, bold=True)
        say(tf, banner[1], 16, INK, before=6)
        y += tall + Inches(0.34)

    if numbered:
        for i, item in enumerate(numbered):
            col, row = i % 2, i // 2
            x = EDGE + col * Inches(6.3)
            ty = y + row * Inches(0.66)
            block(s, x, ty, Inches(0.38), Inches(0.38), PAPER, radius=0.5, edge=GREEN)
            label(s, x, ty + Inches(0.07), Inches(0.38), Inches(0.3), str(i + 1), 12, GREEN,
                  bold=True, align=PP_ALIGN.CENTER)
            tf = frame(s, x + Inches(0.56), ty + Inches(0.04), Inches(5.4), Inches(0.56))
            say(tf, item, 15, INK)
        y += Inches(0.66) * ((len(numbered) + 1) // 2) + Inches(0.2)

    if columns:
        width = (SPAN - Inches(0.36) * (len(columns) - 1)) / len(columns)
        # Высота колонок считается по самой длинной: иначе следующий блок ляжет поверх них.
        deepest = max(sum(Inches(0.2) + Inches(0.23) * max(1, -(-len(i) // 38)) for i in items)
                      for _, _, items in columns)
        tall = deepest + Inches(0.9)
        for i, (head, colour, items) in enumerate(columns):
            x = EDGE + i * (width + Inches(0.36))
            block(s, x, y, width, tall, WASH, radius=0.05, edge=HAIR)
            block(s, x, y, width, Inches(0.08), colour)
            label(s, x + Inches(0.3), y + Inches(0.32), width - Inches(0.6), Inches(0.3), head, 12,
                  colour, bold=True)
            yy = y + Inches(0.76)
            for item in items:
                lines = max(1, -(-len(item) // 38))
                block(s, x + Inches(0.3), yy + Inches(0.08), Inches(0.13), Inches(0.13), colour,
                      radius=0.5)
                tf = frame(s, x + Inches(0.58), yy, width - Inches(0.9), Inches(0.24) * lines)
                say(tf, item, 13, INK)
                yy += Inches(0.2) + Inches(0.23) * lines
        y += tall + Inches(0.2)

    if pairs:
        width = (SPAN - Inches(0.36)) / 2
        for i, (head, tail, colour) in enumerate(pairs):
            col, row = i % 2, i // 2
            x = EDGE + col * (width + Inches(0.36))
            ty = y + row * Inches(1.42)
            block(s, x, ty, width, Inches(1.2), WASH, radius=0.05, edge=HAIR)
            block(s, x, ty, Inches(0.08), Inches(1.2), colour)
            label(s, x + Inches(0.34), ty + Inches(0.22), width - Inches(0.6), Inches(0.32), head,
                  18, INK, bold=True)
            tf = frame(s, x + Inches(0.34), ty + Inches(0.58), width - Inches(0.6), Inches(0.52))
            say(tf, tail, 12, MUTE)
        y += Inches(1.42) * ((len(pairs) + 1) // 2)

    if note:
        block(s, EDGE, y + Inches(0.16), SPAN, Inches(0.88), SAND, radius=0.08)
        tf = frame(s, EDGE + Inches(0.4), y + Inches(0.36), SPAN - Inches(0.8), Inches(0.5))
        say(tf, note, 14, RGBColor(0x2B, 0x17, 0x00))
    if outro:
        block(s, EDGE, y + Inches(0.16), SPAN, Inches(0.92), MINT, radius=0.08)
        tf = frame(s, EDGE + Inches(0.44), y + Inches(0.36), SPAN - Inches(0.9), Inches(0.56))
        say(tf, outro, 16, INK, bold=True)
    return s


def listing(prs, number, kicker, title, items):
    """Источники: пара «что - откуда» на строку."""
    s, y = sheet(prs, number, kicker, title)
    for i, (head, tail) in enumerate(items):
        ty = y + i * Inches(0.58)
        block(s, EDGE, ty + Inches(0.06), Inches(0.05), Inches(0.42), GREEN if i % 2 == 0 else TEAL)
        label(s, EDGE + Inches(0.26), ty, Inches(11.4), Inches(0.3), head, 14, INK)
        label(s, EDGE + Inches(0.26), ty + Inches(0.26), Inches(11.4), Inches(0.3), tail, 11, MUTE)
    return s


def numbers(prs, number, kicker, title, figures, footer=None, lead=None):
    """Четыре величины крупно."""
    s, y = sheet(prs, number, kicker, title, lead)
    width = (SPAN - Inches(0.31) * 3) / 4
    for i, (big, cap, tail) in enumerate(figures):
        x = EDGE + i * (width + Inches(0.31))
        block(s, x, y, width, Inches(2.4), WASH, radius=0.05, edge=HAIR)
        label(s, x + Inches(0.26), y + Inches(0.28), width - Inches(0.5), Inches(0.9), big, 40,
              GREEN, font=HEAD, bold=True)
        label(s, x + Inches(0.26), y + Inches(1.1), width - Inches(0.5), Inches(0.3), cap, 14, INK,
              bold=True)
        tf = frame(s, x + Inches(0.26), y + Inches(1.46), width - Inches(0.5), Inches(0.86))
        say(tf, tail, 12, MUTE)
    if footer:
        block(s, EDGE, y + Inches(2.76), SPAN, Inches(0.94), MINT, radius=0.08)
        tf = frame(s, EDGE + Inches(0.44), y + Inches(2.96), SPAN - Inches(0.9), Inches(0.6))
        say(tf, footer, 16, INK, bold=True)
    return s


def scheme(prs, number, kicker, title, lead=None):
    """Единственная схема: три части системы. Интерфейса для неё не существует."""
    s, y = sheet(prs, number, kicker, title, lead)
    part_w = Inches(5.2)
    parts = [('ANDROID-КЛИЕНТ', 'Kotlin · Jetpack Compose', GREEN, MINT,
              [('28 экранов', 'Material 3'), ('Room', 'местная база'),
               ('Очередь операций', 'работа без сети')]),
             ('СЕРВЕР', 'Kotlin · Spring Boot · PostgreSQL', TEAL, RGBColor(0xBF, 0xE9, 0xF8),
              [('Общие аптечки', 'состав участников'), ('Общий остаток и брони', 'источник истины'),
               ('Справочник', 'препараты РФ')])]
    for i, (head, stack, colour, fill, rows) in enumerate(parts):
        x = EDGE + i * (part_w + Inches(2.13))
        block(s, x, y, part_w, Inches(2.5), WASH, radius=0.05, edge=colour)
        label(s, x + Inches(0.32), y + Inches(0.24), part_w - Inches(0.6), Inches(0.3), head, 12,
              colour, bold=True)
        label(s, x + Inches(0.32), y + Inches(0.58), part_w - Inches(0.6), Inches(0.3), stack, 12,
              MUTE)
        for j, (name, note) in enumerate(rows):
            ry = y + Inches(1.02) + j * Inches(0.47)
            block(s, x + Inches(0.32), ry, part_w - Inches(0.64), Inches(0.4), fill, radius=0.2)
            label(s, x + Inches(0.5), ry + Inches(0.08), Inches(2.6), Inches(0.3), name, 13, INK,
                  bold=True)
            label(s, x + part_w - Inches(2.5), ry + Inches(0.09), Inches(2.1), Inches(0.3), note,
                  11, colour, align=PP_ALIGN.RIGHT)

    mid = EDGE + part_w
    pointer(s, mid + Inches(0.14), y + Inches(0.95), mid + Inches(2.0), y + Inches(0.95), GREEN)
    pointer(s, mid + Inches(2.0), y + Inches(1.6), mid + Inches(0.14), y + Inches(1.6), TEAL)
    label(s, mid + Inches(0.14), y + Inches(0.55), Inches(1.86), Inches(0.36),
          'аптечки, брони,\nсинхронизация', 10, MUTE, align=PP_ALIGN.CENTER)
    label(s, mid + Inches(0.14), y + Inches(1.68), Inches(1.86), Inches(0.36),
          'справочник,\nснимок полки', 10, MUTE, align=PP_ALIGN.CENTER)

    sy = y + Inches(2.9)
    block(s, EDGE + Inches(8.53), sy, Inches(3.3), Inches(0.72), WASH, radius=0.05, edge=HAIR)
    label(s, EDGE + Inches(8.78), sy + Inches(0.12), Inches(3.0), Inches(0.3),
          'Скраппер справочника', 13, INK, bold=True)
    label(s, EDGE + Inches(8.78), sy + Inches(0.38), Inches(3.0), Inches(0.3),
          'Python · разовая загрузка, в работе не участвует', 10, MUTE)
    pointer(s, EDGE + Inches(10.1), sy, EDGE + Inches(10.1), y + Inches(2.5), GHOST)

    block(s, EDGE, sy - Inches(0.06), Inches(6.4), Inches(0.92), MINT, radius=0.07)
    tf = frame(s, EDGE + Inches(0.36), sy + Inches(0.12), Inches(5.7), Inches(0.62))
    say(tf, 'Клиент без сети работает полностью: сеть нужна только общей аптечке.', 15, INK,
        bold=True)
    return s


# ---------------------------------------------------------------- содержание

def build(prs):
    cover(prs,
          head=[('Органайзер', 54, INK), ('лекарств', 54, GREEN)],
          under='Приложение для Android · "Medicine Organizer" Android Application',
          lines=[('Индивидуальный программный проект', 15, INK, True),
                 ('Волошин Никита, БПИ245', 15, INK, False),
                 ('Научный руководитель: Е. Ю. Песоцкая, к. э. н., доцент департамента '
                  'программной инженерии ФКН НИУ ВШЭ', 13, MUTE, False),
                 ('Москва, 2026', 12, MUTE, False)])

    hero(prs, 2, 'предметная область', 'Откуда взялась задача',
         '02-med-kits/filled',
         [('Лекарства лежат в трёх местах',
           'дома, в общежитии, в рюкзаке - и каждое место живёт своим списком'),
          ('«А я сегодня таблетку пил — или это было вчера?»',
           'курс надо пить по часам, а через пятнадцать минут я уже не помню'),
          ('Общая аптечка',
           'из одной пачки берут все: я рассчитываю на неё, а её уже допили')],
         accent='Одни приложения напоминают о приёме, другие ведут список того, что дома. '
                'Весь сценарий не закрывает ни одно.',
         caption='Так это выглядит в итоге: три места одним списком')

    table(prs, 3, 'анализ аналогов', 'Каждое закрывает свой кусок',
          [('Medisafe', 'Medisafe Inc.'), ('MyTherapy', 'smartpatient'),
           ('Домашняя аптечка', 'pewaru-333'), ('Аптечка. Учёт', 'DecSoft'),
           ('Честный ЗНАК', 'ЦРПТ'), ('MedApp', 'этот проект')],
          [('Напоминания о приёме', [1, 1, 1, 1, 1, 1]),
           ('Учёт остатка упаковки', [1, 1, 1, 1, 0, 1]),
           ('Несколько мест хранения', [0, 0, 0, 1, 0, 1]),
           ('Контроль сроков годности', [0, 0, 1, 1, 1, 1]),
           ('Сканирование кода маркировки', [0, 0, 1, 1, 1, 1]),
           ('Общая аптечка с общим остатком', [0, 0, 0, 0, 0, 1]),
           ('Бронирование под курс лечения', [0, 0, 0, 0, 0, 1]),
           ('Работа без сети', [0, 1, 1, 1, 0, 1]),
           ('Учётная запись без имени и контактов', [0, 0, 0, 0, 0, 1])],
          footer='Общего остатка на несколько устройств и брони под курс нет ни у кого - это и '
                 'пришлось проектировать самому.',
          lead='Сравнение по открытым описаниям приложений, сентябрь 2026 г.')

    prose(prs, 4, 'цель и задачи', 'Закрыть сценарий одним окном',
          banner=('ЦЕЛЬ', 'Разработать приложение для Android, которое ведёт упаковки и сроки, '
                  'курсы и напоминания, заводит пачку по коду с упаковки, показывает расход и '
                  'позволяет пользоваться общей аптечкой нескольким людям - не выходя из одного '
                  'приложения.'),
          numbered=['Проанализировать предметную область и аналоги',
                    'Сформулировать требования и согласовать техническое задание',
                    'Собрать справочник препаратов, продающихся в РФ',
                    'Спроектировать модель: упаковка, курс, приём, бронь',
                    'Разработать серверную часть: общие аптечки и брони',
                    'Разработать Android-клиент: учёт, напоминания, аналитика',
                    'Провести испытания и подготовить документацию по ГОСТ 19'])

    triptych(prs, 5, 'требования', 'Что программа обязана уметь',
             lead='Три группы требований - и два сквозных, прямо из сценария: работа без сети и '
                  'никаких персональных данных.',
             panels=[('04-med-kit-contents/filled', 'Учёт - правда',
               'просроченная поднята первой, сроки и места видно сразу',
               GREEN),
              ('16-course-sources/stack', 'Ответы о будущем',
               '«не хватает 9 приёмов с 21.09» видно заранее', TEAL),
              ('06-package-card/claimed-by-others', 'Общая аптечка',
               'видно, сколько из остатка забронировали другие', INK)])

    prose(prs, 6, 'средства реализации', 'Чем это сделано',
          columns=[('КЛИЕНТ', GREEN, ['Kotlin · JetBrains', 'Jetpack Compose · Google',
                                      'Room · Google', 'WorkManager · Google',
                                      'CameraX и ML Kit · Google', 'Ktor Client · JetBrains']),
                   ('СЕРВЕР', TEAL, ['Kotlin · JetBrains', 'Spring Boot · Broadcom',
                                     'Exposed · JetBrains', 'PostgreSQL · PGDG',
                                     'Testcontainers · AtomicJar', 'Docker · Docker Inc.']),
                   ('ДАННЫЕ', INK, ['Python · PSF', 'Scrapy · Zyte',
                                    'BeautifulSoup · L. Richardson', 'справочник препаратов РФ'])],
          note='Почему не ORM: форма SQL-запроса здесь часть требований - в запросе выражены '
               'доступ вызывающего, предикат версии и режим блокировки.')

    scheme(prs, 7, 'архитектура системы', 'Три части с разной причиной меняться')

    hero(prs, 8, 'модель предметной области', 'Единица учёта — упаковка',
         '06-package-card/on-course',
         [('Приём списывает из конкретной пачки',
           'у двух пачек одного лекарства разные сроки годности, часто и разная дозировка'),
          ('Курс держит упаковки-источники',
           'и порядок, в котором их расходовать: сначала то, что испортится раньше'),
          ('Бронь принадлежит человеку',
           'это его решение о запасе, а не служебная отметка сервера')],
         accent='«Одно лекарство» определить нечем: вещество, название, комплектация и '
                'производитель дают четыре разных ответа.',
         caption='Карточка упаковки: остаток, срок, бронь под курс')

    hero(prs, 9, 'приватность', 'Чего сервер не знает',
         '01-setup/key-lost',
         [('О человеке - только идентификатор и хеш ключа',
           'ни имени, ни почты, ни телефона; журнал приёмов на сервер не уходит вовсе'),
          ('Проверять право отдельным шагом нечем',
           'доступ выражен внутри запроса: чтение принимает вызывающего и этим же проверяет право'),
          ('У решения есть цена',
           'ключ утрачен - восстановить учётную запись некому, и это приходится честно сказать')],
         lead='Данные тут медицинские: серверу знать их незачем. Это требование определило его '
              'устройство сильнее любой функции.',
         caption='Экран «ключ утрачен»: что останется, а что пропадёт')

    versus(prs, 10, 'общий остаток', 'Одну упаковку меняют одновременно',
           left={'screen': '06-package-card/on-course', 'head': 'Устройство А',
                 'note': 'расход применён, версия стала восьмой', 'colour': GREEN},
           right={'screen': '06-package-card/refused-by-server', 'head': 'Устройство Б',
                  'note': 'предъявило версию семь и получило отказ', 'colour': RUST},
           middle=[('Оба прочитали версию 7', 'одна и та же пачка на двух устройствах', MUTE, WASH),
                   ('Команда удерживает корень аптечки',
                    'и под удержанием перечитывает изменяемое', AMBER, SAND),
                   ('Предикат версии в самом UPDATE',
                    'ноль изменённых строк - гонка проиграна', RUST, BLUSH),
                   ('Проигравший перечитывает и повторяет',
                    'человек видит, что осталось на самом деле', GREEN, MINT)],
           lead='Прочитанное не даёт права писать: участника могут исключить из аптечки прямо во '
                'время его команды.')

    triptych(prs, 11, 'работа без сети', 'Что человек видит, пока связи нет',
             lead='Повтор идёт тем же замороженным запросом: иначе потерянный ответ стал бы вторым '
                  'списанием.',
             panels=[('04-med-kit-contents/shared-in-flight', 'Записано сразу',
               'строка помечена: к серверу ещё не доехало', AMBER),
              ('28-sync/rows', 'Очередь ждёт',
               '«отправится, когда будет связь»',
               TEAL),
              ('06-package-card/refused-by-server', 'Отказ - словами',
               'сервер отклонил - приложение предлагает пересчитать', RUST)])

    numbers(prs, 12, 'испытания', 'Чем проверено',
            [('1130', 'проверок без устройства', 'домен, отображения, представления'),
             ('957', 'инструментальных', 'Android 10 (360×640 dp) и большой экран с крупным шрифтом'),
             ('38', 'сквозных историй', '21 на клиенте и 17 на сервере; каждая проходит путь '
              'человека целиком'),
             ('40 000', 'строк в выборке', 'планы запросов: число обращений к базе не растёт с '
              'объёмом')],
            footer='Гонки проверяются настоящими параллельными транзакциями: проверка задерживает '
                   'одну и убеждается, что вторая получает отказ по версии.',
            lead='Проверки идут на каждом изменении; нарушение границ слоёв роняет сборку.')

    prose(prs, 13, 'результаты', 'Что сделано и сдано',
          pairs=[('Android-приложение', 'учёт упаковок и сроков, курсы и напоминания, сканирование '
                  'кода маркировки, отчёты, общая аптечка', GREEN),
                 ('Сервер общих аптечек', 'приглашения, общий остаток и брони, разрешение '
                  'конкурентных изменений, контракт OpenAPI', TEAL),
                 ('Справочник препаратов', 'собран отдельным скраппером из открытых источников, '
                  'подсказки при заведении пачки', INK),
                 ('Документация по ГОСТ 19', 'техническое задание, пояснительная записка, '
                  'руководство оператора, ПМИ, текст программы', MUTE)],
          outro='Сценарий закрыт одним окном: общий остаток и бронь под курс - без учётной записи, '
                'имени и контактов.')

    prose(prs, 14, 'развитие', 'Куда проект идёт дальше',
          lead='Заявленный объём работ выполнен и проверен; развитие ведётся задачами в '
               'репозиториях проекта.',
          columns=[('КЛИЕНТ', GREEN, ['расписания «через день» и «каждые N дней»: цикл вместо '
                                      'недельной сетки',
                                      'правка записанных ответов и просмотр прошлых дней',
                                      'кэш справочника: подсказки и поиск без сети']),
                   ('СЕРВЕР', TEAL, ['разграничение доступа политиками самой базы: второй рубеж '
                                     'поверх предиката в запросе',
                                     'журнал повторов в постоянном хранилище',
                                     'свой предел размера тела запроса']),
                   ('ПРОДУКТ', INK, ['полная поддержка экранного чтеца, проверка на TalkBack',
                                     'публикация в RuStore и страница приложения'])])

    listing(prs, 15, 'источники', 'Список источников',
            [('ГОСТ 19.101-77, 19.201-78, 19.301-79, 19.401-78, 19.404-79, 19.505-79',
              'Единая система программной документации'),
             ('Adherence to long-term therapies: evidence for action',
              'World Health Organization, 2003'),
             ('Kotlin, Exposed, Ktor', 'JetBrains · kotlinlang.org, jetbrains.com/help/exposed'),
             ('Jetpack Compose, Room, WorkManager, ML Kit', 'Google · developer.android.com'),
             ('Spring Boot', 'Broadcom (VMware Tanzu) · docs.spring.io/spring-boot'),
             ('PostgreSQL', 'PostgreSQL Global Development Group · postgresql.org/docs'),
             ('Medisafe · MyTherapy · «Домашняя аптечка» · «Аптечка. Учёт медикаментов» · '
              '«Честный ЗНАК»',
              'Medisafe Inc. · smartpatient GmbH · pewaru-333 · DecSoft · ЦРПТ'),
             ('Репозитории проекта', 'github.com/Kert0n · MedAppDocs, MedAppAndroid, MedAppServer')])

    cover(prs, number=16, dark=True,
          head=[('Демонстрация', 54, PAPER)],
          under='Видео: две минуты работы приложения',
          lines=[('Спасибо за внимание. Готов ответить на вопросы.', 18, PAPER, False)],
          qr=True)


def retheme(path):
    """В теме пустой презентации стоит Calibri, которого на машине нет: в PDF вместо него встаёт
    чужой шрифт. Имя правится прямо в теме - она здесь одна."""
    source = zipfile.ZipFile(path)
    items = [(i, source.read(i.filename)) for i in source.infolist()]
    source.close()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as out:
        for info, data in items:
            if info.filename.startswith('ppt/theme/') and info.filename.endswith('.xml'):
                body = data.decode('utf-8')
                body = re.sub(r'typeface="Calibri Light"', f'typeface="{HEAD}"', body)
                body = re.sub(r'typeface="Calibri"', f'typeface="{BODY}"', body)
                data = body.encode('utf-8')
            out.writestr(info, data)


def main():
    import segno
    segno.make('https://github.com/Kert0n', error='h').save(os.path.join(ASSETS, 'qr-repos.png'),
                                                            scale=12, border=2, dark='#102D69',
                                                            light='#FFFFFF')
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    build(prs)
    prs.save('Презентация.pptx')
    retheme('Презентация.pptx')
    print('слайдов собрано:', len(prs.slides._sldIdLst))


if __name__ == '__main__':
    main()
