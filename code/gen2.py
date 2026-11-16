import json, random, os, datetime, collections, re, sys

W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, "videos2")
os.makedirs(OUT, exist_ok=True)
random.seed(4127)

site = json.load(open(os.path.join(W, "site.json")))

AIRPORT = dict(verona="VRN", bologna="BLQ", florence="FLR", milan="MIL", nice="NCE", strasbourg="SXB", seville="SVQ", granada="GRX", cordoba="SVQ",
 valencia="VLC", malaga="AGP", sansebastian="BIO", madrid="MAD", lisbon="LIS", porto="OPO", zakynthos="ZTH", crete="CHQ", rhodes="RHO", santorini="JTR",
 mykonos="JMK", athens="ATH", dubrovnik="DBV", split="SPU", zagreb="ZAG", sarande="CFU", berat="TIA", gjirokaster="TIA", tirana="TIA", sarajevo="SJJ",
 mostar="SJJ", sofia="SOF", plovdiv="SOF", varna="VAR", bansko="SOF", brasov="OTP", timisoara="TSR", bucharest="OTP", budapest="BUD", gdansk="GDN",
 brno="BRQ", bratislava="BTS", vilnius="VNO", kaunas="KUN", nuremberg="NUE", munich="MUC", salzburg="SZG", vienna="VIE", hallstatt="SZG", innsbruck="INN",
 interlaken="ZRH", lucerne="ZRH", bruges="BRU", ghent="BRU", reykjavik="KEF", vik="KEF", akureyri="AEY", tromso="TOS", bergen="BGO", faroe="FAE",
 istanbul="IST", gozo="MLA", marrakech="RAK", fes="FEZ", chefchaouen="TNG", essaouira="ESU", dahab="SSH", luxor="LXR", qaba="ASW", petra="AQJ",
 wadirum="AQJ", tbilisi="TBS", baku="GYD", bukhara="BHK", samarkand="SKD", bali="DPS", hoian="DAD", **{"da-lat": "DLI"}, pokhara="PKR", kathmandu="KTM",
 chiangmai="CNX", bangkok="BKK", krabi="KBV", kohsamui="USM", siemreap="SAI", luangprabang="LPQ", kualalumpur="KUL", goa="GOI", jaipur="JAI", kerala="COK",
 kyoto="KIX", zanzibar="ZNZ", capetown="CPT", oaxaca="OAX", mexicocity="MEX", tulum="CUN", cartagena="CTG", medellin="MDE", antigua="GUA", lima="LIM",
 prague="PRG", krakow="KRK", tallinn="TLL", riga="RIX", ljubljana="LJU", naples="NAP", palermo="PMO", malta="MLA", kotor="TIV", cairo="CAI", hanoi="HAN", **{"da-nang": "DAD"}, yerevan="EVN", belgrade="BEG", salamanca="MAD", toledo="MAD",
 puno="JUL", **{"la-paz": "LPB"}, uyuni="UYU", cuenca="CUE", paraty="GIG")

CC = {"Albania": "AL", "Serbia": "RS", "Estonia": "EE", "Latvia": "LV", "Armenia": "AM", "Austria": "AT", "Azerbaijan": "AZ", "Belgium": "BE", "Bolivia": "BO", "Bosnia and Herzegovina": "BA", "Brazil": "BR", "Bulgaria": "BG",
      "Cambodia": "KH", "Colombia": "CO", "Croatia": "HR", "Czechia": "CZ", "Ecuador": "EC", "Egypt": "EG", "Faroe Islands": "FO", "France": "FR", "Georgia": "GE",
      "Germany": "DE", "Greece": "GR", "Guatemala": "GT", "Hungary": "HU", "Iceland": "IS", "India": "IN", "Indonesia": "ID", "Italy": "IT", "Japan": "JP",
      "Jordan": "JO", "Laos": "LA", "Lithuania": "LT", "Malaysia": "MY", "Malta": "MT", "Mexico": "MX", "Montenegro": "ME", "Morocco": "MA", "Nepal": "NP",
      "North Macedonia": "MK", "Norway": "NO", "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT", "Romania": "RO", "Slovakia": "SK",
      "Slovenia": "SI", "South Africa": "ZA", "Spain": "ES", "Sri Lanka": "LK", "Switzerland": "CH", "Tanzania": "TZ", "Thailand": "TH", "Tunisia": "TN",
      "Turkey": "TR", "Uzbekistan": "UZ", "Vietnam": "VN"}
COUNTRY_FIX = {"Bali, Indonesia": "Indonesia", "Crete, Greece": "Greece", "Czech Republic": "Czechia", "Türkiye": "Turkey", "Bosnia": "Bosnia and Herzegovina"}
HL_FIX = {"madeira": ["Pico do Arieiro sunrise hike", "Levada walk"], "paros": ["Naoussa harbour at sunset", "Lefkes village"], "symi": ["Gialos harbour", "Panormitis monastery"],
          "ksamil": ["Swim to the Ksamil islands", "Butrint ruins day trip"], "lake-bled": ["Row to Bled Island", "Vintgar Gorge"],
          "siquijor-island": ["Cambugahay Falls", "Paliton Beach sunset"], "mirissa": ["Whale watching boat trip", "Coconut Tree Hill"],
          "isla-mujeres": ["Playa Norte", "Snorkel the underwater museum"]}
ASIA_C = {"Indonesia", "Vietnam", "Thailand", "Cambodia", "Laos", "Malaysia", "Philippines", "Nepal", "India", "Sri Lanka", "Japan", "Uzbekistan"}
AFME_C = {"Morocco", "Egypt", "Jordan", "Tunisia", "Tanzania", "South Africa"}
SOLO_IDS = set("hoian bangkok pokhara kathmandu lisbon porto bali cusco medellin mexicocity siargao sapa tbilisi budapest kualalumpur goa krabi koh-lanta zanzibar capetown oaxaca sarajevo sofia chiangmai siemreap luangprabang".split())
FAMILY_IDS = set("tenerife corralejo menorca lagos faro madeira crete rhodes kefalonia zakynthos lefkada split plitvice-lakes brac budva valencia malaga agadir kohsamui langkawi krabi zanzibar gozo lake-balaton heviz interlaken innsbruck sintra capetown".split())


def short(s):
    s = re.split(r" \(", s)[0]
    if len(s) > 46:
        s = s[:46].rsplit(" ", 1)[0]
    return s


POOL = {}
for ln in open(os.path.join(W, "attrs.txt")):
    if not ln.strip():
        continue
    i, tags, months, hotel, tip = ln.rstrip("\n").split("|")
    s = site[i]
    assert s["vis"], i
    country = COUNTRY_FIX.get(s["country"], s["country"])
    hl = HL_FIX.get(i) or [short(h) for h in s["highlights"][:2]]
    assert len(hl) == 2, i
    ap = (s.get("airport") or AIRPORT.get(i))
    assert ap, i
    tg = set(tags.replace(" ", ""))
    if i in SOLO_IDS: tg.add("s")
    if i in FAMILY_IDS: tg.add("y")
    d = dict(id=i, city=s["city"], country=country, cc=CC[country], tagline=s["tagline"], hl=hl, days=s["days"], nights=max(1, s["days"] - 1), ex=int(s["ex"]), f=int(round(s["f"])),
             total=int(s["total"]), region=s["region"], months=months, hotel=hotel, tip=tip, airport=ap, tags=tg)
    if i == "bali": d["city"] = "Ubud"
    POOL[i] = d
DL = list(POOL.values())


def flag(cc):
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in cc)


def euro(d): return d["region"] == "Europe"
def asia(d): return d["country"] in ASIA_C
def afme(d): return d["country"] in AFME_C
def latam(d): return d["region"] == "Americas"
def T(*t): return lambda d: any(x in d["tags"] for x in t)


f_any = lambda d: d["days"] <= 8
f_l = T("l"); f_h = T("h"); f_r = T("r")

FAM = {
 "cheap-couples": dict(name="Cheap Couples Trips", color="#e0457b", target=22, notes="Proven: 5 of the top 10 are couples titles (60K to 716K). Keep titles simple. Slide prices are the site price minus flights, labelled on every slide."),
 "looks-expensive": dict(name="Looks Expensive, Isn't", color="#f59e0b", target=18, notes="Proven: 758K, 417K, 372K, 243K. Pick places that look luxury in photos. Slide prices are the site price minus flights."),
 "never-heard": dict(name="Never Heard Of", color="#22a699", target=16, notes="Proven: 525K and 127K. Genuinely lesser-known places only. Slide prices are the site price minus flights."),
 "hidden-gems": dict(name="Cheap Hidden Gems", color="#6d5bd0", target=10, notes="Proven: 342K and 24K. Slide prices are the site price minus flights."),
 "cheap-places": dict(name="Cheap Places to Visit", color="#2f80ed", target=24, notes="Proven: 158K to 715K for the plain title. Use the edition (Solo, Family, Winter Sun and so on) to vary. Slide prices are the site price minus flights."),
 "more-romantic": dict(name="More Romantic Than", color="#d946ef", target=8, notes="Proven: 26.8K for the Paris one. Use famous romantic places as the hook. Slide prices are the site price minus flights."),
 "city-breaks": dict(name="Cheap City Breaks", color="#0ea5e9", target=10, notes="Proven: 28.8K. Every city is cheap for hotels, food and getting around, prices exclude flights."),
 "cheaper-than-think": dict(name="Cheaper Than You Think", color="#10b981", target=8, notes="Proven: 87K, 66K, 49K. Slide prices are the site price minus flights."),
}
YEAR = "2027"
specs = []
def add(fam, base, n=5, flt=f_any, edition="", cap=None, min_day=0, max_day=99, extra=None):
    specs.append(dict(fam=fam, base=base, n=n, flt=flt, edition=edition, cap=cap, min_day=min_day, max_day=max_day, extra=extra or {}))

for i in range(6): add("looks-expensive", "6 Places That Look Expensive But Aren't", 6, f_l)
for i in range(4): add("looks-expensive", "Hidden Gems That Look Expensive But Are Shockingly Cheap", 6, f_l)
for i in range(4): add("looks-expensive", "Shockingly Cheap Couples Trips That Look Luxury", 6, lambda d: f_l(d) and f_r(d))
for i in range(4): add("looks-expensive", "Places That Look Expensive... But Aren't", 6, f_l)

cc_titles = [f"Shockingly Cheap Couples Trips for {YEAR}", f"Cheap Couples Trips for {YEAR}", f"Shockingly Affordable Couples Trips for {YEAR}",
             f"Cheap Romantic Trips for Couples in {YEAR}", f"Cheap Places To Visit With Your Partner in {YEAR}", "Romantic Trips That Are Surprisingly Cheap",
             "Couples Escapes You Can Actually Afford"]
cc_eds = [("", f_r), ("Honeymoon Edition", lambda d: f_r(d) and d["days"] <= 6), ("Hidden Gems Edition", lambda d: f_r(d) and "h" in d["tags"]),
          ("Beach Edition", lambda d: f_r(d) and "b" in d["tags"]), ("Island Edition", lambda d: f_r(d) and "i" in d["tags"]),
          ("City Edition", lambda d: f_r(d) and "c" in d["tags"] and euro(d)), ("Winter Sun Edition", lambda d: f_r(d) and "w" in d["tags"])]
for i in range(22):
    t = cc_titles[i % len(cc_titles)]
    ed = cc_eds[(i * 3 + i // 7) % len(cc_eds)]
    add("cheap-couples", t, 6, ed[1], ed[0], min_day=(14 if ed[0] == "Winter Sun Edition" else 0))

for i in range(8): add("never-heard", "Cheap Places You've Never Heard Of", 6, f_h)
for i in range(8): add("never-heard", "6 Cheap Places You've Never Heard Of", 6, f_h)
for i in range(5): add("hidden-gems", f"Cheap Hidden Gems to Visit in {YEAR}", 6, f_h)
for i in range(5): add("hidden-gems", f"Shockingly Cheap Hidden Gems to Visit in {YEAR}", 6, f_h)

cp = [("", f_any), ("", f_any), ("", f_any), ("Couples Edition", f_r), ("Solo Travel Edition", T("s")), ("Family Edition", T("y")),
      ("Winter Sun Edition", T("w")), ("Winter Sun Edition", T("w")), ("Weekend Edition", lambda d: d["days"] <= 3), ("Hidden Gems Edition", T("h")), ("Honeymoon Edition", f_r),
      ("Adventure Edition", T("n")), ("Beach Edition", T("b")), ("Island Edition", T("i")), ("City Edition", T("c")), ("Cold Edition", T("x")),
      ("Christmas Markets Edition", T("x")), ("Girls Trip Edition", T("g")), ("Short Haul Edition", lambda d: d["f"] <= 150),
      ("Nature Edition", T("n")), ("Couples Edition", f_r), ("Solo Travel Edition", T("s")), ("Long Weekend Edition", lambda d: d["days"] <= 3), ("Hidden Gems Edition", T("h"))]
for ed, flt in cp:
    mn = 24 if ed in ("Cold Edition", "Christmas Markets Edition") else (6 if ed == "Winter Sun Edition" else 0)
    add("cheap-places", f"Cheap Places to Visit in {YEAR}", 6, flt, ed, min_day=mn)

for x in ["Paris", "Venice", "Santorini", "the Maldives", "Bali", "Rome", "Dubrovnik", "the Amalfi Coast"]:
    add("more-romantic", f"6 Places More Romantic Than {x} (and Cheaper)", 6, lambda d, x=x: f_r(d) and d["city"] not in ("Venice", "Santorini", "Dubrovnik", "Ubud"), extra=dict(hook=x))

CB = [f"Cheap City Breaks for {YEAR}", "Cheap City Breaks You Can Actually Afford", "Cheap Weekend City Breaks"]
for ci, cap in enumerate([250, 250, 250, 300, 300, 300, 350, 350, 250, 300]):
    add("city-breaks", CB[ci % 3], 6, lambda d, c=cap: "c" in d["tags"] and d["days"] <= 4 and d["ex"] <= c, cap=cap)

for t in ["Places That Are Much Cheaper Than You Think", "Destinations That Are Much Cheaper Than You Think", "Think You Need a Huge Budget to Travel? Think Again",
          "Places That Are Much Cheaper Than You Think", "Destinations That Are Much Cheaper Than You Think", "Think You Need a Huge Budget to Travel? Think Again",
          "Places That Are Much Cheaper Than You Think", "Destinations That Are Much Cheaper Than You Think"]:
    add("cheaper-than-think", t, 6, lambda d: d["days"] <= 6 and ("c" in d["tags"] or "l" in d["tags"]))

assert len(specs) == 116, len(specs)

START = datetime.date(2026, 10, 23)
positions = [(dd, ss) for dd in range(2, 60) for ss in (0, 1)]
remaining = list(range(len(specs)))
order, prev = [], []
famleft = collections.Counter(s["fam"] for s in specs)
def take(pred):
    for i in remaining:
        if pred(specs[i]): return i
for i in (take(lambda s: s["fam"] == "looks-expensive" and s["base"].startswith("6 Places")), take(lambda s: s["fam"] == "cheap-couples" and s["base"].startswith("Shockingly Cheap"))):
    remaining.remove(i); order.append(i); famleft[specs[i]["fam"]] -= 1; prev.append(specs[i]["fam"])
for p in range(2, len(positions)):
    day = positions[p][0]
    cands = [i for i in remaining if specs[i]["min_day"] <= day <= specs[i]["max_day"] and specs[i]["fam"] not in prev[-2:]] or \
            [i for i in remaining if specs[i]["min_day"] <= day] or remaining[:]
    left = len(positions) - p
    best = max(cands, key=lambda i: famleft[specs[i]["fam"]] / left + random.random() * 0.15 + (0.3 if specs[i]["min_day"] > 0 and specs[i]["min_day"] + 10 > day else 0))
    remaining.remove(best); order.append(best); famleft[specs[best]["fam"]] -= 1; prev.append(specs[best]["fam"])

seen = collections.Counter(); titles = []
for idx in order:
    s = specs[idx]; key = (s["base"], s["edition"]); seen[key] += 1
    t = s["base"] + (f" {s['edition']}" if s["edition"] else "")
    if seen[key] > 1: t += f" Part {seen[key]}"
    titles.append(t)

usage = collections.Counter(); last_pos = {}
def pick(spec, p):
    pool = [d for d in DL if spec["flt"](d)]
    if spec["fam"] == "more-romantic":
        pool = [d for d in pool if not (spec["extra"]["hook"] == "Paris" and d["cc"] == "FR")]
    chosen, ccn, regn = [], collections.Counter(), collections.Counter()
    while len(chosen) < spec["n"]:
        best, bs = None, -1e9
        for d in pool:
            if d in chosen or ccn[d["cc"]] >= 2: continue
            sc = -usage[d["id"]] * 6.0 + random.random() * 3
            if d["id"] in last_pos and p - last_pos[d["id"]] < 14: sc -= 10
            if regn[d["region"]] >= 3: sc -= 4
            if spec["fam"] in ("cheap-couples", "looks-expensive", "more-romantic") and "r" not in d["tags"] and "l" not in d["tags"]: sc -= 3
            if sc > bs: best, bs = d, sc
        assert best, (spec["base"], spec["edition"], len(pool), [c["id"] for c in chosen])
        chosen.append(best); ccn[best["cc"]] += 1; regn[best["region"]] += 1
    return chosen

plans = []
for p, idx in enumerate(order):
    s = specs[idx]; ch = pick(s, p)
    for d in ch: usage[d["id"]] += 1; last_pos[d["id"]] = p
    ch.sort(key=lambda d: d["ex"])
    plans.append((p, s, titles[p], ch))

CTAS = ["Get the full itinerary", "Find the cheapest dates", "See all destinations", "Plan this trip", "Compare prices", "Unlock the full guide",
        "Build your trip plan", "See the full breakdown", "Check live prices", "Explore more trips"]
m = lambda x: f"£{x}"

def slide(d, cta):
    return "\n".join([f"{flag(d['cc'])} {d['city']}, {d['country']}", d["tagline"], f"Budget {m(d['ex'])} pp for {d['nights']} nights",
                      "Things to do:", f"• {d['hl'][0]}", f"• {d['hl'][1]}", f"Where to stay: {d['hotel']}", f"Fly to: {d['airport']}",
                      f"Tip: {d['tip']}", f"{cta} @ www.TripFlux.co (link in bio)"])

INTROS = {
 "cheap-couples": ["Looking for cheap couples trips? These {n} romantic places cost far less than you would think once you leave out flights.", "Planning a cheap romantic trip with your partner? These {n} places are shockingly affordable on the ground."],
 "looks-expensive": ["These {n} places look like they cost a fortune, but hotels and food cost far less than the photos suggest.", "Places that look expensive but are not: {n} spots with big views and small bills."],
 "never-heard": ["Cheap places you have probably never heard of: {n} under-the-radar spots with low on-the-ground costs.", "Want somewhere different? These {n} cheap places barely make the usual lists."],
 "hidden-gems": ["Cheap hidden gems for your next trip: {n} spots with big views and small bills.", "These {n} hidden gems are cheap to stay in and eat in, and far less crowded than the famous names."],
 "cheap-places": ["Where should you travel next? These {n} cheap places have low hotel and food costs.", "Cheap places to visit: {n} destinations where your money goes a long way."],
 "more-romantic": ["Looking for a romantic trip that is not the obvious one? These {n} places feel just as romantic and cost less on the ground.", "Skip the crowds: {n} romantic alternatives with lower hotel and food costs."],
 "city-breaks": ["Cheap city breaks: {n} cities where a short stay is cheap for hotels, food and getting around, before flights.", "Want a city break on a budget? These {n} cities are cheap for hotels, food and getting around."],
 "cheaper-than-think": ["You do not need a huge budget to travel. These {n} places are much cheaper than most people think.", "Think travel is too expensive? These {n} places cost far less than you would expect on the ground."],
}
DISC = ["Prices are per person for the nights shown and cover a hotel, food and local costs, based on TripFlux estimates. Flights are not included, so check live fares for your dates.",
        "Prices are per person for the nights shown (hotel, food and local costs). Flights are not included.", "Prices are per person, flights not included."]

def tiktok(title, spec, rows, p):
    n = len(rows); intro = INTROS[spec["fam"]][p % 2].format(n=n)
    lo, hi = min(r["f"] for r in rows), max(r["f"] for r in rows)
    fl = f"Flights are extra: roughly {m(lo)} to {m(hi)} return from the UK depending on where you go."
    def item(i, d, lvl):
        c = d["city"]
        if lvl == 0: return f"{i}. {c}, {d['country']}: {d['tagline']}. Around {m(d['ex'])}pp for {d['nights']} nights, flights not included. Things to do in {c}: {d['hl'][0]}, {d['hl'][1]}. Best time to visit {c}: {d['months']}."
        if lvl == 1: return f"{i}. {c}, {d['country']}: around {m(d['ex'])}pp for {d['nights']} nights, flights not included. Things to do in {c}: {d['hl'][0]}, {d['hl'][1]}. Best time to visit: {d['months']}."
        if lvl == 2: return f"{i}. {c}, {d['country']}: around {m(d['ex'])}pp for {d['nights']} nights, flights not included. Things to do: {d['hl'][0]}, {d['hl'][1]}."
        return f"{i}. {c}, {d['country']}: around {m(d['ex'])}pp for {d['nights']} nights, flights not included. Try: {d['hl'][0]}."
    cands = []
    for di, disc in enumerate(DISC):
        for lvl in range(4):
            for fi in (True, False):
                parts = [f"{title}. {intro}", "\n\n".join(item(i + 1, d, lvl) for i, d in enumerate(rows)), disc]
                if fi: parts.append(fl)
                parts.append("Full guides and live prices at www.TripFlux.co\nWhich one are you booking?")
                txt = "\n\n".join(parts)
                if 800 <= len(txt) <= 1000: cands.append((lvl, 0 if fi else 1, di, -len(txt), txt))
    assert cands, (title, [len(x) for x in []])
    return min(cands)[4]

def ig(title, rows):
    L = [f"{title}. Prices are per person and do not include flights.", ""]
    for i, d in enumerate(rows): L.append(f"{i+1}. {flag(d['cc'])} {d['city']}: {d['tagline']} (about {m(d['ex'])}pp for {d['nights']} nights, excl. flights)")
    L += ["", "Full guides, prices and itineraries → www.TripFlux.co", "", "Which one are you booking? 👇", "", "Save this for later 📌"]
    return "\n".join(L)

def yt(title, rows):
    return f"{title}. Prices exclude flights.\n\n" + ", ".join(d["city"] for d in rows) + ".\n\nFull guides at www.TripFlux.co\n\nWhich one are you booking? 👇 #Shorts"

FT = {"cheap-couples": "#couplestrip #romantictrips", "looks-expensive": "#looksexpensive #luxuryonabudget", "never-heard": "#hiddengems #underratedplaces", "hidden-gems": "#hiddengems #underratedplaces",
      "cheap-places": "#cheaptravel #budgettravel", "more-romantic": "#romantictrips #couplestrip", "city-breaks": "#citybreak #europetravel", "cheaper-than-think": "#cheaptravel #budgettravel"}
def tags(spec, rows):
    t = ["#travel", "#traveltok", "#tripflux", FT[spec["fam"]]]
    for d in rows[:3]: t.append("#" + re.sub(r"[^a-z0-9]", "", d["city"].lower()))
    return " ".join(t)

def build(p, spec, title, rows):
    dd, ss = positions[p]; fam = spec["fam"]; cta = CTAS[p % len(CTAS)]
    dests = [dict(airport=d["airport"], budget=str(d["ex"]), cc=d["cc"], city=d["city"], country=d["country"], cta="", custom=slide(d, cta),
                  extra=f"Site total £{d['total']} incl. flights £{d['f']}", hotel=d["hotel"], months=d["months"], nights=str(d["nights"]), onSite=True,
                  photo=f"Hero shot: {d['hl'][0]}", tagline=d["tagline"], tip=d["tip"], todo1=d["hl"][0], todo2=d["hl"][1]) for d in rows]
    chk = "; ".join(f"{d['id']} £{d['ex']} (site £{d['total']} less £{d['f']} flights)" for d in rows)
    notes = (f"Series: {FAM[fam]['name']}. Proven formula: simple title, 5 or 6 places, one slide each, your fixed slide format. Slide price = the price on tripflux.co minus the flight, "
             f"stated as excluding flights on the final slide and in the caption only (not on the cover or the destination slides). PRICE CHECK (site at 24 Oct 2026): {chk}. "
             "LANDING PAGE: the site shows totals INCLUDING flights, so add a description line saying the slide prices exclude flights. "
             "DRAFT. Hotels are real properties from general knowledge: confirm each is open and in budget on Expedia on posting day, and re-check the site prices have not changed. Photos still to choose.")
    return dict(captions=dict(tiktok=tiktok(title, spec, rows, p), instagram=ig(title, rows), youtube=yt(title, rows)), cover=title, cta=cta,
                date=(START + datetime.timedelta(days=dd)).isoformat(), destinations=dests, example=False,
                final="Which one are you booking?\nComment below 👇\n\nPrices exclude flights\nFull guides and prices\nwww.TripFlux.co (link in bio)", hashtags=tags(spec, rows), notes=notes, part="",
                posted=dict(instagram=False, tiktok=False, youtube=False), saves="", shares="", seriesId=fam, slot=ss, status="drafted", title=title, url="", verdict="", views47=""), f"plan-d{dd:02d}-s{ss}"

if __name__ == "__main__":
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    for p, s, t, rows in plans:
        doc, name = build(p, s, t, rows)
        assert "*" not in json.dumps(doc, ensure_ascii=False)
        json.dump(doc, open(os.path.join(OUT, name + ".json"), "w"), ensure_ascii=False, indent=1)
    print("written", len(plans), "distinct titles", len(set(titles)))
    print(collections.Counter(s["fam"] for _, s, _, _ in plans))
    print("dests used", len(usage), "max reuse", usage.most_common(6))
    for p, s, t, rows in plans[:6]:
        print(positions[p], t, "|", ", ".join(f"{d['city']} £{d['ex']}" for d in rows))
