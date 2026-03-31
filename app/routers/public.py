"""Public marketing site routes for Texas Turf Pros."""

import logging
from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response

log = logging.getLogger(__name__)

router = APIRouter()

# ── Neighborhood data for templates ──────────────────────────

ZONES = {
    "lakeway": [
        {"name": "Rough Hollow", "homes": "1,200", "slug": "rough-hollow"},
        {"name": "Lakeway Highlands", "homes": "800", "slug": "lakeway-highlands"},
        {"name": "The Hills", "homes": "600", "slug": "the-hills"},
        {"name": "Flintrock Falls", "homes": "450", "slug": "flintrock-falls"},
        {"name": "Tuscan Village", "homes": "350", "slug": "tuscan-village"},
    ],
    "westlake": [
        {"name": "Westlake Hills", "homes": "3,000", "slug": "westlake-hills"},
        {"name": "Rob Roy", "homes": "500", "slug": "rob-roy"},
        {"name": "Davenport Ranch", "homes": "800", "slug": "davenport-ranch"},
        {"name": "Eanes Creek", "homes": "400", "slug": "eanes-creek"},
    ],
    "bee_caves": [
        {"name": "Falconhead", "homes": "500", "slug": "falconhead"},
        {"name": "Spanish Oaks", "homes": "400", "slug": "spanish-oaks"},
        {"name": "Sweetwater", "homes": "350", "slug": "sweetwater"},
    ],
    "spicewood": [
        {"name": "West Cypress Hills", "homes": "300", "slug": "west-cypress-hills"},
        {"name": "Briarcliff", "homes": "250", "slug": "briarcliff"},
    ],
}

AREAS_SUMMARY = {
    "Lakeway": ["Rough Hollow", "Lakeway Highlands", "The Hills", "Flintrock Falls", "Tuscan Village"],
    "Westlake": ["Westlake Hills", "Rob Roy", "Davenport Ranch", "Eanes Creek"],
    "Bee Cave": ["Falconhead", "Spanish Oaks", "Sweetwater"],
    "Spicewood": ["West Cypress Hills", "Briarcliff"],
}

# ── Blog content ─────────────────────────────────────────────

BLOG_POSTS = [
    {
        "slug": "lakeway-lawn-care-calendar",
        "title": "The Complete Lakeway Lawn Care Calendar: Month-by-Month Guide",
        "tag": "Seasonal Guide",
        "excerpt": "A month-by-month breakdown of what your Central Texas lawn needs, from pre-emergent timing to winterizer applications.",
        "content": """
<h2>Your Year-Round Lawn Care Schedule</h2>
<p>Central Texas lawns operate on a different calendar than the rest of the country. Our warm-season grasses (Bermuda, St. Augustine, Zoysia) have specific windows for treatments that, if missed, can mean an entire season of weeds or weak turf.</p>

<h3>January &ndash; February: Pre-Emergent Round 1</h3>
<p>This is the most important application of the year. Pre-emergent herbicides like <strong>Barricade</strong> or <strong>Dimension</strong> create a chemical barrier in the soil that prevents weed seeds from germinating. Apply when soil temperatures are still below 55&deg;F &mdash; typically late January through mid-February in the Lakeway area.</p>
<p><strong>Key tip:</strong> Don't aerate your lawn after applying pre-emergent. It breaks the barrier.</p>

<h3>March &ndash; April: Pre-Emergent Round 2 + First Fertilizer</h3>
<p>A second pre-emergent application extends your weed barrier through the summer. This is also when your lawn starts breaking dormancy, making it the perfect time for the first fertilizer application. Use a slow-release nitrogen fertilizer to feed green-up without burning tender new growth.</p>
<p>If you see weeds breaking through, this is when post-emergent herbicides like <strong>Celsius</strong> or <strong>MSM Turf</strong> come into play. These are selective &mdash; they kill weeds without harming warm-season turf.</p>

<h3>May &ndash; June: Fertilizer + Grub Prevention</h3>
<p>Your lawn is in full growth mode. Apply a second round of fertilizer and, critically, your <strong>grub preventive</strong> (imidacloprid/Merit). Grub eggs are laid in May-June, and a preventive application now stops them before they hatch and destroy your roots.</p>
<p>This is also fire ant season. A bifenthrin-based lawn insecticide handles fire ants, chinch bugs, and other surface pests.</p>

<h3>July &ndash; August: Maintenance Mode</h3>
<p>Peak heat in Central Texas means your lawn is under stress. This isn't the time for heavy fertilization. Focus on proper irrigation (deep, infrequent watering) and mowing height (keep Bermuda at 1.5-2", St. Augustine at 3-3.5"). Spot-treat any weeds with post-emergent as needed.</p>

<h3>September &ndash; October: Fall Recovery</h3>
<p>As temperatures drop below 95&deg;F, your lawn enters a second growth surge. This is an excellent time for fertilization &mdash; use a potassium-heavy blend to build root strength. Continue post-emergent weed control for any fall weeds (henbit, chickweed, clover).</p>

<h3>November &ndash; December: Winterizer</h3>
<p>Apply a final winterizer fertilizer before your lawn goes dormant. This feeds the roots through winter and gives your turf a head start on spring green-up. In Central Texas, warm-season grasses typically go dormant in late November to December.</p>

<h3>The Bottom Line</h3>
<p>Timing is everything in Central Texas lawn care. Miss your pre-emergent window and you'll fight weeds all summer. Skip the grub preventive and you risk brown, spongy patches in late summer. A 5-round program covers all of these critical windows.</p>
""",
    },
    {
        "slug": "pre-emergent-central-texas",
        "title": "When to Apply Pre-Emergent in Central Texas (And Why Timing Matters)",
        "tag": "Weed Control",
        "excerpt": "The #1 mistake in Central Texas lawn care is missing the pre-emergent window. Here's exactly when to apply and what products work best.",
        "content": """
<h2>Pre-Emergent: Your Most Important Treatment</h2>
<p>If you only do one thing for your lawn each year, make it pre-emergent weed control. Pre-emergent herbicides don't kill existing weeds &mdash; they prevent weed seeds already in your soil from germinating. Think of it as a shield between the soil surface and the weed seeds below.</p>

<h3>When to Apply in the Lakeway / Bee Cave Area</h3>
<p>The timing window for Central Texas is:</p>
<ul>
    <li><strong>Round 1:</strong> Late January to mid-February</li>
    <li><strong>Round 2:</strong> Late March to mid-April</li>
</ul>
<p>The trigger is <strong>soil temperature</strong>. Pre-emergent needs to be down before soil temps consistently reach 55&deg;F at a 4-inch depth, which is when crabgrass and other summer annuals begin germinating.</p>

<h3>Why Two Applications?</h3>
<p>A single application of pre-emergent breaks down in 8-12 weeks. Central Texas has a long growing season (March through November), so one application leaves a gap in late spring when summer weeds are still trying to germinate. Two applications provide continuous protection through the critical spring and early summer window.</p>

<h3>Best Products for Our Area</h3>
<ul>
    <li><strong>Barricade (prodiamine)</strong> &mdash; Longest-lasting pre-emergent, excellent for our alkaline clay soils. Typically our go-to for Round 1.</li>
    <li><strong>Dimension (dithiopyr)</strong> &mdash; Offers both pre-emergent and early post-emergent activity, meaning it can stop weeds that have just begun to sprout. Great for Round 2.</li>
</ul>

<h3>Common Mistakes</h3>
<ul>
    <li><strong>Applying too late.</strong> If you see crabgrass, it's already too late for pre-emergent. You'll need post-emergent treatment instead.</li>
    <li><strong>Aerating after application.</strong> Core aeration punches holes through the pre-emergent barrier, rendering it ineffective. Always aerate before applying, or wait until fall.</li>
    <li><strong>Not watering it in.</strong> Pre-emergent needs about 0.5 inches of water within 14 days of application to activate and bind to soil particles.</li>
</ul>

<h3>What If You Missed the Window?</h3>
<p>It's not the end of the world. Post-emergent herbicides like Celsius, MSM Turf, Certainty, and Tribute Total can selectively kill weeds that have already emerged without harming your Bermuda or St. Augustine turf. It's more work and more cost, but it's fixable.</p>
""",
    },
    {
        "slug": "bermuda-vs-st-augustine-lakeway",
        "title": "Bermuda vs. St. Augustine: Which Grass is Best for Lakeway Lawns?",
        "tag": "Grass Types",
        "excerpt": "The two most common turf types in the Hill Country have very different care needs. Here's how to choose and maintain each one.",
        "content": """
<h2>Two Grasses, Two Strategies</h2>
<p>Walk through any Lakeway or Bee Cave neighborhood and you'll see two dominant grass types: Bermuda and St. Augustine. Both can thrive here, but they have very different characteristics, care requirements, and trade-offs.</p>

<h3>Bermuda Grass</h3>
<p><strong>Best for:</strong> Full-sun lawns, high-traffic areas, homeowners who want a tight, manicured look.</p>
<ul>
    <li><strong>Sun requirements:</strong> Needs 6+ hours of direct sun. Will thin and die in shade.</li>
    <li><strong>Mowing height:</strong> 1.5 - 2 inches. Bermuda likes to be kept short.</li>
    <li><strong>Drought tolerance:</strong> Excellent. Goes dormant (brown) in drought but recovers quickly.</li>
    <li><strong>Cold tolerance:</strong> Goes dormant earlier in fall, greens up later in spring.</li>
    <li><strong>Growth habit:</strong> Aggressive spreader via stolons and rhizomes. Will invade flower beds if not edged.</li>
    <li><strong>Herbicide compatibility:</strong> Very tolerant. Can handle most selective herbicides.</li>
</ul>

<h3>St. Augustine</h3>
<p><strong>Best for:</strong> Partially shaded lawns, thick carpet-like appearance, low-traffic areas.</p>
<ul>
    <li><strong>Sun requirements:</strong> Tolerates partial shade (4+ hours). Best grass for under-tree areas in Central Texas.</li>
    <li><strong>Mowing height:</strong> 3 - 3.5 inches. Cutting too short stresses the plant.</li>
    <li><strong>Drought tolerance:</strong> Moderate. Needs more water than Bermuda during summer.</li>
    <li><strong>Cold tolerance:</strong> Less cold-hardy. Can suffer damage in hard freezes (remember Feb 2021).</li>
    <li><strong>Growth habit:</strong> Spreads via stolons only (no rhizomes), so it recovers from damage more slowly.</li>
    <li><strong>Herbicide sensitivity:</strong> Sensitive to many herbicides. Products like 2,4-D and atrazine can damage it. Requires St. Augustine-safe formulations.</li>
</ul>

<h3>The Central Texas Factor</h3>
<p>Our alkaline clay soil and limestone-based water create specific challenges:</p>
<ul>
    <li><strong>Iron chlorosis</strong> is common in both grass types due to high soil pH. Supplemental iron applications keep color deep green.</li>
    <li><strong>Chinch bugs</strong> particularly target St. Augustine. If you have St. Aug, preventive pest control in summer is important.</li>
    <li><strong>Take-all root rot</strong> affects St. Augustine in our alkaline soils, especially during cool, wet spring weather.</li>
</ul>

<h3>Our Recommendation</h3>
<p>Most Hill Country properties benefit from Bermuda in full-sun areas and St. Augustine in shaded zones. We adjust our treatment products and timing based on which grass you have &mdash; this is one of the reasons a one-size-fits-all lawn care company can do more harm than good.</p>
""",
    },
]

POSTS_BY_SLUG = {p["slug"]: p for p in BLOG_POSTS}


# ── Template context helper ──────────────────────────────────

def _ctx(request: Request, **extra):
    """Common template context."""
    return {"request": request, "now": datetime.now(), **extra}


# ── Page routes ──────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/index.html", _ctx(request, areas=AREAS_SUMMARY)
    )


@router.get("/services", response_class=HTMLResponse)
async def services(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/services.html", _ctx(request)
    )


@router.get("/areas", response_class=HTMLResponse)
async def areas(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/areas.html", _ctx(request, zones=ZONES)
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/about.html", _ctx(request)
    )


@router.get("/reviews", response_class=HTMLResponse)
async def reviews(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/reviews.html", _ctx(request)
    )


@router.get("/review")
async def review_redirect():
    """Redirect /review to Google Business Profile review page.
    Update this URL once your Google Business Profile is live."""
    # Placeholder — replace with actual Google review link
    return RedirectResponse(url="/reviews", status_code=302)


# ── Blog ─────────────────────────────────────────────────────

@router.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/blog/index.html", _ctx(request, posts=BLOG_POSTS)
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    post = POSTS_BY_SLUG.get(slug)
    if not post:
        return RedirectResponse(url="/blog", status_code=302)
    return request.app.state.templates.TemplateResponse(
        "public/blog/post.html", _ctx(request, post=post)
    )


# ── Quote request ────────────────────────────────────────────

@router.get("/quote", response_class=HTMLResponse)
async def quote_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/quote.html",
        _ctx(
            request,
            utm_source=request.query_params.get("utm_source", ""),
            utm_medium=request.query_params.get("utm_medium", ""),
            utm_campaign=request.query_params.get("utm_campaign", ""),
            src=request.query_params.get("src", ""),
        ),
    )


@router.post("/quote", response_class=HTMLResponse)
async def quote_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    lot_size: str = Form(""),
    heard_from: str = Form(""),
    notes: str = Form(""),
    utm_source: str = Form(""),
    utm_medium: str = Form(""),
    utm_campaign: str = Form(""),
    src: str = Form(""),
):
    # Build services list from checkboxes
    form = await request.form()
    services = form.getlist("services")
    services_str = ", ".join(services) if services else "Not specified"

    # Determine lead source for tracking
    source = src or utm_source or heard_from or "website"

    log.info(
        "NEW LEAD: %s | %s | %s | %s | services=%s | source=%s",
        name, email, phone, address, services_str, source,
    )

    # Send notification email to Cory
    try:
        from ..services.email_service import send_email

        body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:#2d6a4f;color:#fff;padding:20px;text-align:center;">
                <h2 style="margin:0;">New Quote Request</h2>
            </div>
            <div style="padding:20px;background:#f9f9f9;">
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px;font-weight:bold;">Name:</td><td style="padding:8px;">{name}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Phone:</td><td style="padding:8px;">{phone}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Email:</td><td style="padding:8px;">{email}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Address:</td><td style="padding:8px;">{address}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Lot Size:</td><td style="padding:8px;">{lot_size or 'Not specified'}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Services:</td><td style="padding:8px;">{services_str}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Source:</td><td style="padding:8px;">{source}</td></tr>
                    <tr><td style="padding:8px;font-weight:bold;">Notes:</td><td style="padding:8px;">{notes or 'None'}</td></tr>
                </table>
            </div>
            <div style="padding:10px 20px;font-size:12px;color:#999;text-align:center;">
                UTM: source={utm_source} medium={utm_medium} campaign={utm_campaign} src={src}
            </div>
        </div>
        """
        await send_email(
            to="cory@txturfpros.com",
            subject=f"New Quote Request from {name} — {address}",
            body_html=body,
        )
    except Exception as exc:
        log.error("Failed to send lead notification: %s", exc)

    return request.app.state.templates.TemplateResponse(
        "public/quote_thanks.html", _ctx(request, name=name.split()[0])
    )


# ── SEO utilities ────────────────────────────────────────────

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(request: Request):
    base = str(request.base_url).rstrip("/")
    return f"""User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""


# ── Door hanger PDF ──────────────────────────────────────────

@router.get("/tools/door-hanger")
async def door_hanger_pdf(neighborhood: str = "", code: str = "NEIGHBOR"):
    """Generate a print-ready door hanger PDF."""
    from ..services.door_hanger import generate_door_hanger_pdf

    pdf_bytes = generate_door_hanger_pdf(neighborhood=neighborhood, promo_code=code)
    filename = f"doorhanger-{neighborhood.lower().replace(' ', '-') or 'generic'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml(request: Request):
    base = str(request.base_url).rstrip("/")
    pages = ["/", "/services", "/areas", "/about", "/blog", "/reviews", "/quote"]
    pages += [f"/blog/{p['slug']}" for p in BLOG_POSTS]

    urls = ""
    for page in pages:
        urls += f"  <url><loc>{base}{page}</loc></url>\n"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>
"""
