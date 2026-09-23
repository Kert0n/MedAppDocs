# coding: utf-8
"""Бронь и обеспечение курса на одной пачке (раздел 7 текста выступления).

Числа выдуманы для примера и согласованы между собой: доза курса одна таблетка, бронь курса
6 таблеток = 6 необеспеченных ещё не принятых приёмов. Правило из плана Android (строки 1170,
1630): курсу доступно физически оставшееся минус брони других; выделение = min(прежнее, доступное).
"""
from svgkit import Canvas, BLUE, LILAC, PALE, WHITE, GREY, RED, YELLOW

W = 1600
c = Canvas(W)
CELL, X0 = 56, 110


def bar(y, cells, caption):
    c.text(X0, y - 18, caption, 22, 'bold')
    for i, (fill, dash) in enumerate(cells):
        c.rect(X0 + i * CELL, y, CELL - 6, 52, fill=fill, stroke=GREY if dash else BLUE, rx=8, dash=dash)


def brace(y, first, count, label, color=BLUE):
    x1, x2 = X0 + first * CELL, X0 + (first + count) * CELL - 6
    c.line(x1, y, x2, y, color, 2)
    c.line(x1, y - 8, x1, y, color, 2)
    c.line(x2, y - 8, x2, y, color, 2)
    c.text((x1 + x2) / 2, y + 26, label, 18, color=color, anchor='middle')


# Было
y = 60
bar(y, [(BLUE, None)] * 6 + [(LILAC, None)] * 8 + [(WHITE, None)] * 6, 'Было: в пачке 20 таблеток')
brace(y + 72, 0, 6, 'бронь этого курса: 6')
brace(y + 72, 6, 8, 'брони других участников: 8')
brace(y + 72, 14, 6, 'свободно: 6')

# Стало
y = 250
bar(y, [(BLUE, None)] * 2 + [(LILAC, None)] * 8 + [(WHITE, '5 4')] * 10,
    'Другой участник взял 10 таблеток мимо курса: осталось 10')
brace(y + 72, 0, 2, 'этому курсу доступно: 2', RED)
brace(y + 72, 2, 8, 'брони других: 8')
brace(y + 72, 10, 10, 'взято мимо курса: 10', GREY)
c.text(X0 + 20 * CELL + 20, y + 22, 'доступно курсу =', 18, color=GREY)
c.text(X0 + 20 * CELL + 20, y + 46, 'остаток − брони других', 18, color=GREY)

# Что меняется, что нет
y = 420
pw = (W - 2 * X0 - 30) / 2
c.rect(X0, y, pw, 200, fill=PALE)
c.text(X0 + 24, y + 40, 'Назначение: не меняется', 24, 'bold')
c.lines(X0 + 24, y + 80, ['доза, дни, время приёма', 'назначенное число доз',
                          'это решение врача, а не соседа по аптечке'], 19, step=30)
x = X0 + pw + 30
c.rect(x, y, pw, 200, fill=WHITE, stroke=RED, width=2)
c.text(x + 24, y + 40, 'Обеспечение: пересчитано', 24, 'bold', RED)
c.lines(x + 24, y + 80, ['обеспечено приёмов: было 6, стало 2', 'названа дата первого необеспеченного приёма',
                         'уведомление: подключить ещё лекарство', 'или изменить порядок источников'], 19, step=30)
c.text(W / 2, y + 240, 'Сервер брони других не исправляет: своё обеспечение пересчитывает телефон каждого участника',
       19, color=GREY, anchor='middle')
c.save('09-claim.svg', y + 262)
