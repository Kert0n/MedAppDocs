# coding: utf-8
"""Общие примитивы ручной инфографики: цвета ФКН, шрифт HSE Sans, текст, плашки, линии.

Схемы, у которых смысл держится на раскладке (кто напротив кого, что внутри чего), рисуются
здесь вручную, а не mermaid: автоматическая раскладка переставляет блоки как ей удобно.
"""
from xml.sax.saxutils import escape

BLUE, LILAC, YELLOW = '#102D69', '#DFC7F2', '#DCFF05'
PALE, SRV, GREY, RED, WHITE = '#F7F5FC', '#E3E8F4', '#55607A', '#BA1A1A', '#FFFFFF'
FONT = "HSE Sans, Navigo, sans-serif"


class Canvas:
    def __init__(self, width):
        self.width = width
        self.items = []

    def text(self, x, y, s, size=18, weight='normal', color=BLUE, anchor='start'):
        self.items.append(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def lines(self, x, y, rows, size=18, step=None, **kw):
        step = step or round(size * 1.3)
        for i, row in enumerate(rows):
            self.text(x, y + i * step, row, size, **kw)
        return y + len(rows) * step

    def rect(self, x, y, w, h, fill=WHITE, stroke=BLUE, rx=10, width=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{width}"{d}/>')

    def line(self, x1, y1, x2, y2, color=BLUE, width=1.6, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        m = ' marker-end="url(#arrow)"' if arrow else ''
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                          f'stroke-width="{width}"{d}{m}/>')

    def save(self, path, height):
        defs = (f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
                f'markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{BLUE}"/></marker></defs>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" '
               f'viewBox="0 0 {self.width} {height}">{defs}'
               f'<rect width="{self.width}" height="{height}" fill="{WHITE}"/>' + ''.join(self.items) + '</svg>')
        with open(path, 'w') as f:
            f.write(svg)
