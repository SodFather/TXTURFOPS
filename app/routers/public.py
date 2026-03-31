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
    from ..config import get_settings
    s = get_settings()
    return {
        "request": request,
        "now": datetime.now(),
        "ga_id": s.ga_measurement_id,
        "gads_id": s.google_ads_id,
        "gads_conversion": s.google_ads_conversion,
        "fb_pixel": s.fb_pixel_id,
        **extra,
    }


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

    # Send notification to Cory + auto-reply to lead
    try:
        from ..services.email_service import send_email

        # Notification to Cory
        notify_body = f"""
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
            body_html=notify_body,
        )

        # Auto-reply to the lead
        first_name = name.split()[0]
        auto_reply = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:#2d6a4f;color:#fff;padding:24px;text-align:center;">
                <h2 style="margin:0;font-size:22px;">Texas Turf Pros</h2>
                <p style="margin:6px 0 0;opacity:.8;font-size:14px;">Professional Lawn Care &bull; Lakeway, TX</p>
            </div>
            <div style="padding:24px;background:#fff;">
                <p style="font-size:16px;">Hi {first_name},</p>
                <p>Thanks for requesting a quote from Texas Turf Pros! I received your information and will review your property details personally.</p>
                <p><strong>Here's what happens next:</strong></p>
                <ol style="line-height:1.8;">
                    <li>I'll review your property at <strong>{address}</strong></li>
                    <li>I'll put together a custom treatment plan based on your lawn's needs</li>
                    <li>You'll hear from me within 24 hours with your quote</li>
                </ol>
                <div style="background:#f0f7f3;border-left:4px solid #2d6a4f;padding:16px;margin:20px 0;border-radius:4px;">
                    <p style="margin:0;font-size:14px;"><strong>Why Texas Turf Pros?</strong></p>
                    <ul style="margin:8px 0 0;padding-left:20px;font-size:14px;line-height:1.6;">
                        <li>TDA Licensed Applicator &mdash; every treatment meets state regulations</li>
                        <li>Owner-operated &mdash; I personally treat every lawn</li>
                        <li>No contracts &mdash; stay because you're happy, not because you're locked in</li>
                        <li>Products and timing tailored for Central Texas soil &amp; turf</li>
                    </ul>
                </div>
                <p>In the meantime, feel free to call or text me directly:</p>
                <p style="text-align:center;margin:16px 0;">
                    <a href="tel:+15129837070" style="display:inline-block;background:#2d6a4f;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:16px;">(512) 983-7070</a>
                </p>
                <p>Looking forward to helping you get a great-looking lawn!</p>
                <p>Cory<br><span style="color:#666;font-size:13px;">Owner, Texas Turf Pros<br>TDA Licensed Applicator</span></p>
            </div>
            <div style="padding:12px 20px;font-size:11px;color:#999;text-align:center;background:#f9f9f9;">
                TX TURF PROS LLC &bull; Lakeway, TX &bull; <a href="https://texasturfpros.com" style="color:#2d6a4f;">texasturfpros.com</a>
            </div>
        </div>
        """
        await send_email(
            to=email,
            subject=f"{first_name}, your lawn care quote request is confirmed!",
            body_html=auto_reply,
        )
    except Exception as exc:
        log.error("Failed to send lead emails: %s", exc)

    return request.app.state.templates.TemplateResponse(
        "public/quote_thanks.html", _ctx(request, name=name.split()[0])
    )


# ── Marketing tools dashboard ────────────────────────────────

CONTENT_CALENDAR = {
    "Week 1 — Launch": [
        {"day": "Monday", "platform": "Facebook", "topic": "Introduction Post",
         "text": "Hey Lakeway neighbors! I'm Cory, owner of Texas Turf Pros. I'm a TDA Licensed Applicator specializing in weed control and fertilization right here in the Hill Country. If your lawn has been taken over by weeds or is looking thin after winter, I can help. DM me or visit texasturfpros.com for a free quote. Serving Lakeway, Bee Cave, Westlake & Spicewood."},
        {"day": "Wednesday", "platform": "Instagram", "topic": "Seasonal Tip",
         "text": "Spring is HERE in Central Texas and that means it's go-time for your lawn. Right now is the perfect window for Round 2 pre-emergent + your first fertilizer application. If you missed Round 1 in February, don't worry - post-emergent treatments can still get your lawn back on track. Drop a comment if you have questions about your lawn! #LakewayTX #LawnCare #WeedControl #TexasTurf #HillCountryLawns"},
        {"day": "Friday", "platform": "Facebook", "topic": "Service Area Spotlight",
         "text": "Driving through Rough Hollow this week and the lawns are waking up fast. If you're in Rough Hollow, Flintrock Falls, or Lakeway Highlands - now is the time to get on a weed control program before the warm-season weeds explode. We're booking this week. Free quotes at texasturfpros.com or call/text (512) 983-7070."},
        {"day": "Saturday", "platform": "Instagram Story", "topic": "Behind the Scenes",
         "text": "Loading up the truck for today's treatments. Pre-emergent + fertilizer going down across Lakeway today. Your lawn's best season starts with the right products at the right time. Book your spot: link in bio"},
    ],
    "Week 2 — Education": [
        {"day": "Monday", "platform": "Facebook", "topic": "Educational Post",
         "text": "One question I get all the time: 'Why do I need TWO rounds of pre-emergent?' Great question. A single application breaks down in 8-12 weeks. Here in Central Texas, our growing season runs March through November - way longer than one application covers. Round 2 in April extends your weed barrier through the summer. It's the difference between a few weeds and a weed takeover. Want to get on a program? texasturfpros.com"},
        {"day": "Wednesday", "platform": "Instagram", "topic": "Common Weeds ID",
         "text": "Know your enemy. The top 5 weeds I'm seeing in Lakeway lawns right now: 1) Crabgrass - spreading, light green 2) Dandelions - the yellow flower everyone knows 3) Clover - round leaves, white flowers 4) Nutsedge - tall, V-shaped blade 5) Henbit - purple flowers, square stem. All treatable with selective herbicides that won't harm your Bermuda or St. Augustine. DM for a free lawn assessment. #LawnCare #WeedControl #LakewayTX"},
        {"day": "Thursday", "platform": "Google Business", "topic": "Seasonal Update",
         "text": "Now booking Round 2 pre-emergent + fertilizer applications across Lakeway, Bee Cave, Westlake, and Spicewood. This is your last chance to get a weed barrier down before summer. Free quotes - call (512) 983-7070 or visit texasturfpros.com."},
        {"day": "Friday", "platform": "Facebook", "topic": "Neighborhood Focus",
         "text": "Bee Cave homeowners - Falconhead, Spanish Oaks, Sweetwater - we're scheduling treatments in your area next week. If your lawn needs some attention before summer hits, now's the perfect time to start. First treatment $20 off with code NEIGHBOR. Book at texasturfpros.com"},
    ],
    "Week 3 — Social Proof": [
        {"day": "Monday", "platform": "Facebook", "topic": "Customer Value",
         "text": "What does professional weed control actually cost? Less than you think. Our treatments start at $55 and cover pre-emergent, post-emergent, AND fertilizer. Compare that to buying products at Home Depot, renting a sprayer, and spending your Saturday trying to figure out application rates. We're TDA Licensed, meaning we use commercial-grade products you can't buy retail. Free quotes: texasturfpros.com"},
        {"day": "Wednesday", "platform": "Instagram", "topic": "Tips for Homeowners",
         "text": "Mowing tip for Central TX: Bermuda grass should be cut at 1.5-2 inches. St. Augustine at 3-3.5 inches. Cutting too short stresses your turf and invites weeds. Most people cut their St. Augustine WAY too short. Raise that mowing deck! Questions about your lawn type? DM me. #LawnTips #CentralTexas #LakewayLawns"},
        {"day": "Friday", "platform": "Facebook", "topic": "5-Round Program",
         "text": "Here's what a full year of lawn care looks like with Texas Turf Pros:\n\nRound 1 (Feb-Mar): Pre-emergent + fertilizer\nRound 2 (Apr-May): Pre-emergent + weed control\nRound 3 (Jun-Jul): Fertilizer + grub preventive\nRound 4 (Sep-Oct): Fertilizer + weed control\nRound 5 (Nov-Dec): Winterizer\n\nStarting at $55/treatment based on lot size. No contracts. Cancel anytime. Your lawn covered, year-round. texasturfpros.com"},
        {"day": "Saturday", "platform": "Instagram Story", "topic": "Treatment Day",
         "text": "Saturday morning treatments in The Hills and Lakeway Highlands. Products going down: Dimension pre-emergent + Celsius post-emergent spot treatment + slow-release fertilizer. Your lawn on a program is a lawn that wins. Book: link in bio"},
    ],
    "Week 4 — Push & Convert": [
        {"day": "Monday", "platform": "Facebook", "topic": "Urgency Post",
         "text": "Fair warning Lakeway: the weed pressure is about to get REAL. Once soil temps hit 65+ (which is any day now), every weed seed in your soil starts germinating. If you don't have a pre-emergent barrier down yet, you're about to see crabgrass, spurge, and nutsedge everywhere. It's not too late for Round 2 - but it will be soon. Get on the schedule: texasturfpros.com or call (512) 983-7070."},
        {"day": "Tuesday", "platform": "Google Business", "topic": "Service Highlight",
         "text": "Grub preventive season is coming up in May-June. White grubs feed on grass roots underground - you won't see the damage until it's too late (brown, spongy patches in late summer). A preventive application of imidacloprid now stops them before they hatch. Add it to your program - call (512) 983-7070."},
        {"day": "Wednesday", "platform": "Instagram", "topic": "Q&A Post",
         "text": "FAQ: 'Is it safe for my dog?'\n\nYes! After application, we recommend keeping pets off the treated area until the product dries - typically 1-2 hours. Once dry, it's bound to the soil and safe for pets and kids. We always send a post-service email with specific care instructions after every treatment.\n\nMore questions? DM me anytime. #LawnCare #PetSafe #LakewayTX"},
        {"day": "Friday", "platform": "Facebook", "topic": "Westlake Focus",
         "text": "Westlake Hills homeowners - we're expanding our route in 78746. If you're in Rob Roy, Davenport Ranch, Eanes Creek, or anywhere in Westlake, we'd love to add you to the schedule. Same professional weed control and fertilization that Lakeway homeowners are getting. First treatment $20 off. texasturfpros.com"},
    ],
}

GOOGLE_ADS = [
    {
        "name": "Ad Group 1: Weed Control",
        "keywords": ["weed control lakeway", "weed removal lakeway tx", "weed killer service bee cave",
                     "post emergent weed control austin", "pre emergent lakeway", "weed spray service 78734",
                     "lawn weed treatment lakeway", "weed control westlake tx", "weed control bee cave"],
        "headlines": ["Lakeway Weed Control Pros", "TDA Licensed Applicator", "Free Weed Control Quote",
                      "Weed Control from $55", "Lakeway & Bee Cave Area", "Same-Week Service",
                      "Kill Weeds, Not Your Grass", "Licensed & Insured"],
        "descriptions": [
            "Professional weed control for Lakeway, Bee Cave & Spicewood. Pre & post-emergent programs.",
            "TDA Licensed Applicator. Kill weeds without harming your turf. Free quotes — call today.",
            "Serving Rough Hollow, Flintrock Falls, Spanish Oaks & more. Results in 7-14 days.",
        ],
    },
    {
        "name": "Ad Group 2: Fertilization",
        "keywords": ["lawn fertilization lakeway", "fertilizer service lakeway tx", "lawn feeding bee cave",
                     "lawn fertilization near me", "fertilization program 78738", "lawn treatment lakeway",
                     "fertilization service westlake tx", "lawn care program lakeway"],
        "headlines": ["Lakeway Lawn Fertilization", "5-Round Lawn Program", "Fertilization from $55",
                      "Year-Round Lawn Care", "Green Lawn Guaranteed", "Local Lakeway Expert",
                      "TDA Licensed Pro", "Free Estimate Today"],
        "descriptions": [
            "Year-round fertilization programs for Central Texas lawns. Bermuda & St. Augustine experts.",
            "5-round lawn care program starting at $55/treatment. No contracts. Locally owned in Lakeway.",
            "Professional fertilization tuned for Hill Country soil. Free quote in minutes.",
        ],
    },
    {
        "name": "Ad Group 3: Pest & Grub Control",
        "keywords": ["lawn pest control lakeway", "grub control lakeway tx", "fire ant treatment lakeway",
                     "chinch bug treatment bee cave", "lawn insect control 78734", "grub prevention lakeway"],
        "headlines": ["Grub & Pest Control", "Fire Ant Treatment", "Stop Grubs Before Damage",
                      "Lawn Pest Control $65", "Licensed Applicator", "Lakeway Pest Experts"],
        "descriptions": [
            "Grub preventive + fire ant + chinch bug treatments for Lakeway area lawns. TDA Licensed.",
            "Don't wait for brown patches. Preventive grub control stops damage before it starts.",
        ],
    },
    {
        "name": "Ad Group 4: Irrigation",
        "keywords": ["irrigation repair lakeway", "sprinkler repair lakeway tx", "irrigation service bee cave",
                     "sprinkler system repair 78738", "irrigation diagnostic lakeway"],
        "headlines": ["Irrigation Repair $85", "Sprinkler System Repair", "Lakeway Irrigation Pro",
                      "Fix Sprinklers Fast", "Diagnostic + Repair", "Licensed & Insured"],
        "descriptions": [
            "Irrigation diagnostics starting at $85. Zone-by-zone inspection, head repairs, programming.",
            "Broken sprinkler heads? Coverage gaps? We diagnose and fix same-week. Lakeway & Bee Cave.",
        ],
    },
]

FACEBOOK_ADS = [
    {"headline": "Your Lawn Deserves Better — Weed Control from $55",
     "text": "Tired of weeds taking over your lawn? Texas Turf Pros provides professional weed control and fertilization for Lakeway, Bee Cave, Westlake & Spicewood homes. TDA Licensed Applicator. No contracts. Get a free quote today."},
    {"headline": "Lakeway's Trusted Lawn Care Pro",
     "text": "Hi, I'm Cory - owner and sole operator of Texas Turf Pros. I personally treat every lawn with commercial-grade products tailored for our Hill Country soil. Pre-emergent, post-emergent, fertilization, pest control. Starting at $55. Get your free quote."},
    {"headline": "5-Round Lawn Care Program — Starting at $55",
     "text": "Year-round weed control and fertilization designed for Central Texas. 5 treatments, perfectly timed to your lawn's growth cycle. Bermuda and St. Augustine specialists. No contracts, cancel anytime. Serving Lakeway, Bee Cave, Westlake & Spicewood."},
    {"headline": "First Treatment $20 Off — Code: NEIGHBOR",
     "text": "New customers get $20 off their first treatment. Professional weed control, fertilization, and pest control from a TDA Licensed Applicator. Locally owned in Lakeway. Free quotes at texasturfpros.com or call (512) 983-7070."},
]

NEXTDOOR_POSTS = [
    {"type": "Introduction", "when": "Week 1",
     "text": "Hi neighbors! I'm Cory, owner of Texas Turf Pros. I'm a TDA Licensed Applicator offering professional weed control and fertilization right here in our community. I live in the Lakeway area and treat every lawn personally - no subcontractors. If your lawn needs help getting ready for spring, I'd love to give you a free assessment. You can reach me at (512) 983-7070 or texasturfpros.com. Happy to answer any lawn care questions!"},
    {"type": "Seasonal Tip", "when": "Week 1",
     "text": "Lakeway lawn tip: If you haven't put down pre-emergent yet, it's not too late for Round 2. This application is your last line of defense before summer weeds take over. Soil temps are climbing fast. Pro tip: water it in within 14 days of application to activate it. Questions? Happy to help - just reply here."},
    {"type": "Educational", "when": "Week 2",
     "text": "Seeing a lot of nutsedge popping up in Lakeway lawns this week. That tall, light-green grass-like weed growing faster than everything else? That's nutsedge. Regular weed killer won't touch it - you need a specialized herbicide like Certainty or SedgeHammer. If it's just a few, pull them. If it's taking over, a professional treatment is the way to go. Happy to answer questions!"},
    {"type": "Community", "when": "Week 2",
     "text": "Heads up Lakeway & Bee Cave neighbors - I'm treating lawns in Rough Hollow, Falconhead, and The Hills this week. If you've been thinking about getting on a weed control program, this is a great time to start. I can swing by for a free lawn assessment while I'm in the area. Call/text (512) 983-7070. Mention Nextdoor for $10 off your first treatment!"},
    {"type": "Seasonal Tip", "when": "Week 3",
     "text": "Central Texas irrigation tip: We're heading into the hot months. Now is the time to check your sprinkler system before you NEED it. Walk each zone and look for: broken heads, heads not popping up, dry spots, and overspray on driveways. A quick check now prevents dead spots in August. I offer $85 irrigation diagnostics if you want a professional walkthrough."},
    {"type": "Expert Advice", "when": "Week 4",
     "text": "Question I get a lot: 'What's the difference between the stuff at Home Depot and what you use?' The main differences: 1) We use commercial-grade concentrates, not diluted retail products. 2) We can access restricted-use products only available to licensed applicators. 3) We calibrate application rates precisely for your lot size. 4) Products like Celsius and Certainty aren't available retail. It's the difference between a good result and a professional result."},
    {"type": "Offer", "when": "Week 4",
     "text": "Spring special for our Nextdoor neighbors: $20 off your first weed control or fertilization treatment. No contracts, no obligations. Just great lawn care from a local, licensed pro. I serve Lakeway, Bee Cave, Westlake, and Spicewood. Call/text (512) 983-7070 or visit texasturfpros.com. Use code NEIGHBOR at checkout."},
]

DOOR_HANGER_ZONES = {
    "Lakeway": [
        {"name": "Rough Hollow", "code": "ROUGHHOLLOW"},
        {"name": "Lakeway Highlands", "code": "HIGHLANDS"},
        {"name": "The Hills", "code": "THEHILLS"},
        {"name": "Flintrock Falls", "code": "FLINTROCK"},
        {"name": "Tuscan Village", "code": "TUSCAN"},
    ],
    "Westlake": [
        {"name": "Westlake Hills", "code": "WESTLAKE"},
        {"name": "Rob Roy", "code": "ROBROY"},
        {"name": "Davenport Ranch", "code": "DAVENPORT"},
    ],
    "Bee Cave": [
        {"name": "Falconhead", "code": "FALCON"},
        {"name": "Spanish Oaks", "code": "SPANOAKS"},
        {"name": "Sweetwater", "code": "SWEETWTR"},
    ],
    "Spicewood": [
        {"name": "West Cypress Hills", "code": "CYPRESS"},
        {"name": "Briarcliff", "code": "BRIARCLF"},
    ],
}


@router.get("/tools", response_class=HTMLResponse)
async def tools_dashboard(request: Request):
    return request.app.state.templates.TemplateResponse(
        "public/tools.html",
        _ctx(
            request,
            content_calendar=CONTENT_CALENDAR,
            google_ads=GOOGLE_ADS,
            facebook_ads=FACEBOOK_ADS,
            nextdoor_posts=NEXTDOOR_POSTS,
            door_hanger_zones=DOOR_HANGER_ZONES,
        ),
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
