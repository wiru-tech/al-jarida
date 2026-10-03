"""Relative-time filter with unit words we control and translate ourselves.

Django's built-in |timesince pulls "hour"/"minute"/etc from Django's own
core catalog, which for ur/ar only localizes the list separator, not the
unit words — so output like "4 hours, 19 minutes" only half-translates.
This filter uses our own msgids (translated in locale/*/LC_MESSAGES) for
every unit, so the whole phrase translates consistently.
"""
from django import template
from django.utils import timezone
from django.utils.translation import get_language, gettext, ngettext

register = template.Library()


@register.filter
def translate(value):
    """Translate a runtime string (e.g. a JSON-stored label) via gettext.

    Fixed-vocabulary values that live in a JSONField — transport stop names,
    schedule labels — can't get per-language DB columns the way model fields
    do, so they're looked up in the same .po/.mo catalog as static template
    strings instead. Register the source strings there by hand since
    `makemessages` only scans template/Python literals, not JSON data.
    """
    return gettext(value) if value else value


@register.filter
def content_lang(obj, fields="title,name,excerpt"):
    """Report which language a record's text will actually render in.

    Translated fields fall back to English when the Urdu/Arabic column is
    blank (MODELTRANSLATION_FALLBACK_LANGUAGES), so on an RTL page a record
    may still be showing English prose. Templates stamp the result on the
    element as ``lang="…"`` and rtl.css keys the LTR/Latin-font treatment off
    that, instead of blanket-forcing every database string to LTR — which
    would mangle genuinely translated Urdu and Arabic headlines.

    Usage: ``<article lang="{{ a|content_lang }}">``
    """
    active = (get_language() or "en").split("-")[0]
    if active == "en":
        return "en"
    for field in fields.split(","):
        value = getattr(obj, f"{field.strip()}_{active}", None)
        if value and str(value).strip():
            return active
    return "en"

_UNITS = (
    ("year", 60 * 60 * 24 * 365),
    ("month", 60 * 60 * 24 * 30),
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("minute", 60),
)

def _unit_text(unit, count):
    # Each branch passes its strings as literals so `makemessages` can
    # statically extract them — a dict-of-strings lookup wouldn't be seen.
    if unit == "year":
        text = ngettext("%(num)d year", "%(num)d years", count)
    elif unit == "month":
        text = ngettext("%(num)d month", "%(num)d months", count)
    elif unit == "week":
        text = ngettext("%(num)d week", "%(num)d weeks", count)
    elif unit == "day":
        text = ngettext("%(num)d day", "%(num)d days", count)
    elif unit == "hour":
        text = ngettext("%(num)d hour", "%(num)d hours", count)
    else:
        text = ngettext("%(num)d minute", "%(num)d minutes", count)
    return text % {"num": count}


@register.filter
def smart_timesince(value):
    """Self-translated equivalent of Django's |timesince, depth 2."""
    if not value:
        return ""
    now = timezone.now()
    delta = now - value
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return gettext("just now")

    for i, (unit, unit_seconds) in enumerate(_UNITS):
        count = seconds // unit_seconds
        if count == 0:
            continue
        parts = [_unit_text(unit, count)]
        remaining = seconds - count * unit_seconds
        if i + 1 < len(_UNITS):
            next_unit, next_seconds = _UNITS[i + 1]
            next_count = remaining // next_seconds
            if next_count > 0:
                parts.append(_unit_text(next_unit, next_count))
        return ", ".join(parts)
    return gettext("just now")
