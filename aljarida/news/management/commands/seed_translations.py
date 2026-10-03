"""Fill in Urdu / Arabic values for the standing section vocabulary.

Article prose has to be written by the newsroom, but section names are fixed
vocabulary, so seeding them here makes the navigation, category headings and
article badges render in the active language immediately instead of falling
back to English everywhere.

Idempotent: existing non-empty translations are left alone unless --overwrite
is passed.

    python manage.py seed_translations
"""
from django.core.management.base import BaseCommand

from news.models import Category

# Keyed by Category.kind so it matches on the stable choice value rather than
# on a display name an editor may have renamed.
SECTION_NAMES = {
    "national":      {"ur": "قومی خبریں",        "ar": "أخبار محلية"},
    "international": {"ur": "بین الاقوامی خبریں", "ar": "أخبار دولية"},
    "sports":        {"ur": "کھیل",              "ar": "رياضة"},
    "technology":    {"ur": "ٹیکنالوجی",          "ar": "تكنولوجيا"},
    "health":        {"ur": "صحت",               "ar": "صحة"},
    "entertainment": {"ur": "تفریح",             "ar": "ترفيه"},
    "opinion":       {"ur": "رائے و اداریہ",      "ar": "رأي وافتتاحية"},
    "islamic":       {"ur": "اسلامی مواد",        "ar": "محتوى إسلامي"},
    "world":         {"ur": "دنیا",              "ar": "العالم"},
}


class Command(BaseCommand):
    help = "Seed Urdu/Arabic translations for category names."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite", action="store_true",
            help="Replace existing Urdu/Arabic values instead of skipping them.",
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        updated = skipped = 0

        for category in Category.objects.all():
            names = SECTION_NAMES.get(category.kind)
            if not names:
                continue

            changed = []
            for code, value in names.items():
                field = f"name_{code}"
                if getattr(category, field) and not overwrite:
                    continue
                setattr(category, field, value)
                changed.append(code)

            # Keep the English column populated so the fallback always
            # resolves, even for rows created before translation was added.
            if not category.name_en:
                category.name_en = category.name
                changed.append("en")

            if changed:
                category.save(update_fields=[f"name_{c}" for c in changed])
                updated += 1
                self.stdout.write(
                    f"  {category.slug}: set {', '.join(sorted(changed))}")
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done — {updated} categor{'y' if updated == 1 else 'ies'} updated, "
            f"{skipped} already translated."))
