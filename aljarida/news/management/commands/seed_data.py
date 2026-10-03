"""Populate the database with realistic demo content matching the design."""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from news.models import (Article, Author, Category, Comment, GalleryImage,
                         MarketRate, Tag, WidgetData)

# Every article, gallery frame and stream thumbnail below points at a real
# photograph on the Unsplash image CDN, chosen to match that specific
# story: the tunnel shot belongs to the subterranean-infrastructure piece,
# the trading screens to the inflation piece, and so on.
#
# The previous version used picsum.photos with a per-index seed, which
# returns an arbitrary stock photo — a wall clock illustrated the transfer
# deal and a dog in a blanket illustrated the central banks story. A news
# front page where the pictures don't match the headlines reads as broken
# even when every other detail is right, so the mapping is now explicit
# and hand-checked rather than generated from a seed.
#
# The query string is Unsplash's own transform API: it serves a resized,
# re-encoded copy instead of the multi-megabyte original.
IMG = "https://images.unsplash.com/{}?w=1200&q=70&fm=jpg&auto=format&fit=crop"


class Command(BaseCommand):
    help = "Seed AL-JARIDA with demo categories, articles, widgets and users."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true",
                            help="Delete existing news content first.")

    def handle(self, *args, **opts):
        if opts["flush"]:
            for m in (Comment, GalleryImage, Article, Tag, Author,
                      MarketRate, WidgetData, Category):
                m.objects.all().delete()
            self.stdout.write("Cleared existing content.")

        User = get_user_model()
        if not User.objects.filter(username="editor").exists():
            User.objects.create_superuser("editor", "editor@al-jarida.example", "aljarida123")
            self.stdout.write(self.style.SUCCESS("Admin created — editor / aljarida123"))

        # ---- Categories ----
        cat_defs = [
            ("World", Category.Kind.WORLD, 1),
            ("National", Category.Kind.NATIONAL, 2),
            ("Technology", Category.Kind.TECH, 3),
            ("Islamic", Category.Kind.ISLAMIC, 4),
            ("Sports", Category.Kind.SPORTS, 5),
            ("Health", Category.Kind.HEALTH, 6),
        ]
        cats = {}
        for name, kind, order in cat_defs:
            cats[kind] = Category.objects.get_or_create(
                name=name, defaults={"kind": kind, "order": order})[0]

        # ---- Authors ----
        authors = [
            Author.objects.get_or_create(display_name="Sarah Jenkins",
                defaults={"role": "Global Affairs Editor"})[0],
            Author.objects.get_or_create(display_name="Tariq Rahman",
                defaults={"role": "Senior Political Correspondent"})[0],
            Author.objects.get_or_create(display_name="Ayesha Malik",
                defaults={"role": "Technology Desk"})[0],
        ]

        # ---- Tags ----
        tag_names = ["infrastructure", "economy", "climate", "urban", "policy",
                     "innovation", "energy", "heritage"]
        tags = [Tag.objects.get_or_create(name=t)[0] for t in tag_names]

        now = timezone.now()

        # ---- Articles ----
        # (title, cat, kicker, excerpt, featured, breaking, photo)
        # `photo` is the Unsplash id substituted into IMG above; the comment
        # beside each one records what the picture actually shows, so a
        # mismatch with the headline is visible while editing this table
        # rather than only after rendering the page.
        data = [
            ("The Paradigm Shift in Urban Infrastructure Planning", Category.Kind.WORLD,
             "GLOBAL AFFAIRS",
             "As metropolitan centers grapple with unprecedented population density, a new wave of architectural innovation prioritizes subterranean expansion over traditional vertical growth.",
             True, False,
             "photo-1761069234641-3a68266c4740"),      # unfinished subterranean tunnel
            ("Economic Reforms Sweep the Nation as Infrastructure Bill Passes",
             Category.Kind.NATIONAL, "NATIONAL",
             "A comprehensive analysis of the new policy framework designed to modernize urban centers and stimulate rural economic growth over the next decade.",
             False, True,
             "photo-1594581979864-36977b15d0dc"),      # capitol dome at golden hour
            ("Central Banks Signal Cautious Optimism Amidst Inflation Data",
             Category.Kind.WORLD, "ECONOMY",
             "Policymakers weigh the balance between growth and price stability as fresh figures reshape market expectations.",
             False, True,
             "photo-1560221328-12fe60f83ab8"),         # trading screens, rate charts
            ("Quantum Computing Breakthrough Could Redefine Encryption Standards",
             Category.Kind.TECH, "TECHNOLOGY",
             "Researchers unveil a milestone that may force a global rethink of how sensitive data is protected.",
             False, False,
             "photo-1681908571122-97f349e1ace0"),      # quantum computer cryostat
            ("Historic Accords Signed at the Geneva Climate Summit",
             Category.Kind.WORLD, "ENVIRONMENT",
             "Delegates from more than a hundred nations commit to an accelerated emissions timeline in a landmark agreement.",
             False, False,
             "photo-1633095975779-fd354aa0dc95"),      # rank of national flags
            ("Next-Gen Microprocessors Promise Unprecedented Efficiency",
             Category.Kind.TECH, "INNOVATION",
             "Tech giants unveil architectural changes that could drastically reduce data-center energy consumption.",
             False, False,
             "photo-1587845323226-bad89242c735"),      # silicon wafer of chip dies
            ("Renewable Sector Sees Record Investment Quarter",
             Category.Kind.WORLD, "ENERGY",
             "Global shifts towards sustainable energy production are driving the largest capital inflows on record.",
             False, False,
             "photo-1466611653911-95081537e5b7"),      # wind farm at sunset
            ("Legislative Deadlock Broken in Historic Midnight Session",
             Category.Kind.NATIONAL, "POLITICS",
             "Bipartisan efforts finally yield a comprehensive framework for the coming fiscal year.",
             False, False,
             "photo-1762246433142-d7d357c76cb5"),      # empty legislative chamber
            ("The Evolution of Geometric Art in Modern Architecture",
             Category.Kind.ISLAMIC, "HERITAGE",
             "Exploring how contemporary designers are integrating classical motifs into brutalist structures.",
             False, False,
             "photo-1558114965-eeb97aa84c3b"),         # geometric tiled dome interior
            ("Preserving Ancient Manuscripts in the Digital Age",
             Category.Kind.ISLAMIC, "HERITAGE",
             "New digitisation projects race to safeguard centuries of scholarship for future generations.",
             False, False,
             "photo-1602660187275-7275b639d7ea"),      # illuminated manuscript page
            ("The Philosophy of Space in Traditional Courtyards",
             Category.Kind.ISLAMIC, "CULTURE",
             "How the design of shared space reflects a deeper social and spiritual philosophy.",
             False, False,
             "photo-1759250451654-72ab594ba2c9"),      # arcaded courtyard with fountain
            ("Championship Finals: Underdog Victory Stuns Fans",
             Category.Kind.SPORTS, "SPORTS",
             "A last-minute turnaround delivers one of the most memorable finishes in recent memory.",
             False, False,
             "photo-1569863959165-56dae551d4fc"),      # packed stadium, confetti
            ("Rising Star Signs Record-Breaking Transfer Deal",
             Category.Kind.SPORTS, "TRANSFERS",
             "The move reshapes the league's balance of power ahead of the new season.",
             False, False,
             "photo-1508087625439-de3978963553"),      # player striking the ball
            ("National Team Clinches Qualification in Dramatic Final Minutes",
             Category.Kind.SPORTS, "INTERNATIONAL",
             "A stoppage-time goal sends supporters into raptures and secures a spot on the world stage.",
             False, False,
             "photo-1706675780107-7c43cc487928"),      # floodlit night match
            ("New Study Links Urban Green Space to Public Health Gains",
             Category.Kind.HEALTH, "HEALTH",
             "Researchers find measurable improvements in wellbeing linked to access to parks and greenery.",
             False, False,
             "photo-1605540827677-693bad36b91f"),      # city park lawn below skyline
            ("Sleep Researchers Identify Key Driver of Daytime Fatigue",
             Category.Kind.HEALTH, "WELLNESS",
             "A large-scale study points to a modifiable habit behind chronic tiredness in adults.",
             False, False,
             "photo-1520179366757-c8a9aa6fbf89"),      # sleeper in morning light
            ("Hospitals Roll Out AI-Assisted Diagnostics for Early Detection",
             Category.Kind.HEALTH, "MEDICINE",
             "Early trials show faster, more accurate screening for a range of common conditions.",
             False, False,
             "photo-1688565631550-ff8aa569f71a"),      # clinician reading a monitor
            ("Battery Chemistry Advance Could Double Electric Vehicle Range",
             Category.Kind.TECH, "INNOVATION",
             "A new electrode design promises significant gains in energy density without added cost.",
             False, False,
             "photo-1593941707874-ef25b8b4a92b"),      # EV charging cable in port
        ]

        body = ("In a landmark session today, officials voted to pass the comprehensive "
                "framework, signaling a major shift in policy aimed at revitalization. "
                "The package focuses heavily on modernizing public transit, expanding "
                "high-speed internet to rural communities, and overhauling aging power grids.\n"
                "Critics argue the timeline is overly ambitious, but proponents emphasize "
                "the immediate job-creation benefits. \"This is not just about concrete and "
                "steel; it's about the future competitiveness of our nation on the global "
                "stage,\" a spokesperson remarked during the closing arguments.\n"
                "Major metropolitan areas stand to benefit most visibly in the short term. "
                "Initial projects slated for next quarter include the expansion of the "
                "central subway system and the implementation of smart-city traffic "
                "management designed to reduce emissions by 15% over five years.")

        urdu = ("یہ ایک تاریخی لمحہ ہے جو ہماری معیشت کو ایک نئی سمت دے گا۔ اس بل کی منظوری "
                "سے نہ صرف روزگار کے نئے مواقع پیدا ہوں گے بلکہ ہمارے بنیادی ڈھانچے میں بھی "
                "نمایاں بہتری آئے گی۔")

        created = []
        rephotographed = 0
        for i, (title, kind, kicker, excerpt, featured, breaking, photo) in enumerate(data):
            art, made = Article.objects.get_or_create(
                title=title,
                defaults=dict(
                    kicker=kicker, excerpt=excerpt, body=body,
                    body_secondary=urdu if i == 1 else "",
                    secondary_language="ur" if i == 1 else "",
                    category=cats[kind], author=random.choice(authors),
                    featured_image_url=IMG.format(photo),
                    image_caption="Photo: Al-Jarida / AFP",
                    status=Article.Status.PUBLISHED, is_featured=featured,
                    is_breaking=breaking,
                    publish_at=now - timedelta(hours=i * 3 + 1),
                    read_minutes=random.randint(3, 7),
                    view_count=random.randint(120, 5400),
                ),
            )
            if made:
                art.tags.set(random.sample(tags, 2))
                created.append(art)
            elif not art.featured_image and art.featured_image_url != IMG.format(photo):
                # Re-seeding an existing database: get_or_create leaves an
                # already-created row untouched, so a demo DB seeded before
                # the photo mapping existed would keep its mismatched
                # picture forever. Repoint it — but never over an image the
                # newsroom uploaded, which is real editorial content.
                art.featured_image_url = IMG.format(photo)
                art.save(update_fields=["featured_image_url"])
                rephotographed += 1

        # Gallery + comments on the national feature
        feature = Article.objects.filter(category=cats[Category.Kind.NATIONAL]).first()
        if feature and not feature.gallery.exists():
            for j, photo in enumerate([
                "photo-1761909922561-6595d426f6e7",   # tower crane at sunset
                "photo-1773643331846-00b9a123bdec",   # towers under construction
            ]):
                GalleryImage.objects.create(article=feature,
                    image_url=IMG.format(photo),
                    caption="Infrastructure in focus", order=j)
            Comment.objects.create(article=feature, name="Sarah Jenkins",
                body="I hope they actually stick to the timeline this time. The rural "
                     "broadband initiative is desperately needed.", is_approved=True, likes=12)
            Comment.objects.create(article=feature, name="David M.",
                body="Agreed. The funding allocation seems solid on paper, but execution "
                     "is always the bottleneck.", is_approved=True)

        # ---- Market rates ----
        for k, (pair, rate, chg) in enumerate([
            ("USD / EUR", "0.9200", "-0.04"), ("GBP / USD", "1.2600", "0.12"),
            ("USD / AED", "3.6700", "0.00"), ("USD / PKR", "278.5000", "-0.31"),
        ]):
            MarketRate.objects.get_or_create(pair=pair,
                defaults={"rate": rate, "change_pct": chg, "order": k})

        # ---- Widgets ----
        # Live TV: one stream per category, shown together on the /live-tv/ hub
        # and the first (order=0) surfaced in the homepage sidebar.
        for k, (title, subtitle, photo) in enumerate([
            ("Al-Jarida Global Broadcast", "News",
             "photo-1651465531201-7e430660fd82"),      # broadcast studio, cameras
            ("Al-Jarida Entertainment", "Entertainment",
             "photo-1657208431551-cbf415b8ef26"),      # stage lights over a crowd
            ("Al-Jarida Religious Programming", "Religious",
             "photo-1528862973381-9bc5ad6d4227"),      # mosque prayer hall
        ]):
            stream, made = WidgetData.objects.get_or_create(
                kind=WidgetData.Kind.LIVE_TV, title=title,
                defaults={"subtitle": subtitle, "order": k,
                          "meta": {"thumb": IMG.format(photo),
                                   "stream": "https://www.youtube.com/embed/live_stream"}})
            if not made and stream.meta.get("thumb") != IMG.format(photo):
                stream.meta["thumb"] = IMG.format(photo)
                stream.save(update_fields=["meta"])

        WidgetData.objects.get_or_create(kind=WidgetData.Kind.QUOTE,
            title="Editorial Board",
            defaults={"subtitle": "Editorial Board",
                      "body": "The foundation of a functioning global society relies not "
                              "on unanimous agreement, but on the relentless pursuit of "
                              "verifiable facts amidst a sea of conjecture."})

        # Transport: train + bus, each with a few upcoming stop/time rows.
        WidgetData.objects.get_or_create(kind=WidgetData.Kind.TRANSPORT,
            title="City Metro — Line 1",
            defaults={"subtitle": "Next departures", "order": 0,
                      "meta": {"rows": [["Central", "09:12"], ["Harbour", "09:24"],
                                        ["University", "09:38"]]}})
        WidgetData.objects.get_or_create(kind=WidgetData.Kind.TRANSPORT,
            title="Cross-City Bus — Route 14",
            defaults={"subtitle": "Next departures", "order": 1,
                      "meta": {"rows": [["Press Enclave", "09:05"], ["City Square", "09:20"],
                                        ["North Terminal", "09:41"]]}})

        # Horoscope: one short daily reading per sign.
        for k, (sign, reading) in enumerate([
            ("Aries", "A bold move pays off if you commit to it before midday."),
            ("Taurus", "Slow down — a rushed decision today costs more than it saves."),
            ("Gemini", "A conversation you've been avoiding turns out easier than expected."),
            ("Cancer", "Home matters take priority; work can wait until tomorrow."),
            ("Leo", "Recognition arrives, but stay humble about where credit is due."),
            ("Virgo", "Details you'd normally catch may slip — double-check before sending."),
            ("Libra", "Balance returns to a relationship that's felt lopsided lately."),
            ("Scorpio", "Trust your instincts over anyone else's advice today."),
            ("Sagittarius", "Travel plans or a spontaneous outing lift your mood."),
            ("Capricorn", "Steady progress beats a dramatic breakthrough this week."),
            ("Aquarius", "An unconventional idea finds unexpected support."),
            ("Pisces", "Creative energy is high — put it toward something that lasts."),
        ]):
            WidgetData.objects.get_or_create(kind=WidgetData.Kind.HOROSCOPE, title=sign,
                defaults={"body": reading, "order": k})

        # Islamic content: Ayat + Hadith of the day.
        WidgetData.objects.get_or_create(kind=WidgetData.Kind.ISLAMIC,
            title="Al-Baqarah 2:153",
            defaults={"subtitle": "Ayat of the Day", "order": 0,
                      "body": "O you who believe! Seek help through patience and prayer. "
                              "Indeed, Allah is with the patient.",
                      "meta": {"arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا اسْتَعِينُوا "
                                          "بِالصَّبْرِ وَالصَّلَاةِ ۚ إِنَّ اللَّهَ مَعَ "
                                          "الصَّابِرِينَ"}})
        WidgetData.objects.get_or_create(kind=WidgetData.Kind.ISLAMIC,
            title="Sahih al-Bukhari 6018",
            defaults={"subtitle": "Hadith of the Day", "order": 1,
                      "body": "Whoever believes in Allah and the Last Day should speak "
                              "good or remain silent.",
                      "meta": {"arabic": "مَنْ كَانَ يُؤْمِنُ بِاللَّهِ وَالْيَوْمِ "
                                          "الْآخِرِ فَلْيَقُلْ خَيْرًا أَوْ لِيَصْمُتْ"}})

        if rephotographed:
            self.stdout.write(self.style.SUCCESS(
                f"Repointed {rephotographed} existing article(s) at their "
                f"matching photograph."))

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Article.objects.count()} articles, "
            f"{Category.objects.count()} categories, "
            f"{MarketRate.objects.count()} market rates."))
