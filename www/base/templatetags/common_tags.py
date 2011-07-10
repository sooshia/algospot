# -*- coding: utf-8 -*-
from __future__ import division
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django import template
import datetime
import re
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

register = template.Library()

@register.filter
def print_username(user):
    profile_link = reverse('user_profile', kwargs={"user_id": user.id})
    return mark_safe('<a href="%s" class="userlink">%s</a>' % 
            (profile_link, user.username))

unit_size = [60,    24,      7,     52,      99999]
unit_name = [u"분", u"시간", u"일", u"주일", u"년"]

def format_readable(diff):
    if diff < 60:
        return u"방금 전"
    cumulative_size = 60
    for sz, name in zip(unit_size, unit_name):
        if diff < cumulative_size*sz:
            return u"%d%s 전" % (diff/ cumulative_size, name)
        cumulative_size *= sz
    return None

@register.filter
def print_datetime(dt):
    fallback = dt.strftime("%Y/%m/%d %H:%M")
    diff = datetime.datetime.now() - dt
    # python 2.6 compatibility. no total_seconds() :(
    diff = diff.seconds + diff.days * 24 * 3600
    return mark_safe(u'<span title="%s">%s</span>' % (fallback, 
        format_readable(diff) or fallback))

code_pattern = re.compile(r'<code lang=([^>]+)>(.+?)</code>', re.DOTALL)
def syntax_highlight(text):
    def proc(match):
        lang = match.group(1).strip('"\'')
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(style="colorful")
        code = match.group(2).replace("\t", "  ")
        highlighted = highlight(code, lexer, formatter)
        return highlighted.replace("\n", "<br/>")
    return code_pattern.sub(proc, text)

@register.filter
def render_text(text):
    text = syntax_highlight(text)
    text = markdown.markdown(text, extensions=["toc"])
    try:
        from wiki.utils import link_to_pages
        text = link_to_pages(text)
    except:
        pass
    return mark_safe(text)


