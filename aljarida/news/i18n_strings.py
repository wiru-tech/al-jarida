"""Translation-extraction anchors for strings that don't live in template
or Python literals `makemessages` can scan.

news/models.py WidgetData.meta (a JSONField) stores transport-schedule stop
names as plain data, e.g. {"rows": [["Press Enclave", "09:05"], ...]}.
templates/news/widgets.html looks each one up at render time through the
``translate`` filter (news/templatetags/i18n_extras.py), which calls
gettext() directly on the JSON value.

Because that call site never contains the literal string, `makemessages`
has nothing to extract and — worse — marks any hand-added msgid for these
values as obsolete (`#~`) the next time it runs, silently dropping the
translation. Wrapping the same literals in `_()` here, purely so the
scanner finds them, is the standard Django workaround: this module is
never imported or executed, it only needs to exist for `makemessages` to
walk.

Keep this list in sync with the stop names seeded in news/management/
commands/seed_data.py.
"""
from django.utils.translation import gettext_lazy as _

_("Central")
_("Harbour")
_("University")
_("Press Enclave")
_("City Square")
_("North Terminal")
