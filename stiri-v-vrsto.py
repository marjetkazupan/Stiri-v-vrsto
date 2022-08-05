import bottle, model, statistika


with open("skrivnost.txt") as d:
    SKRIVNOST = d.read()
JAZ = "jaz"
NASPROTNIK = "nasprotnik"
ZMAGA = "w"
NEODLOCENO = "t"
PORAZ = "l"
DATOTEKA = "stat.json"
STEVILO_IMG = 2

stiri_v_vrsto = model.Stiri_v_vrsto()
vse_skupaj = statistika.VseSkupaj.iz_datoteke(DATOTEKA)

def poisci_ime_igralca(vse_skupaj, ime_polja):
    id_igralca = bottle.request.forms.get(ime_polja)
    return vse_skupaj.uporabniki[int(id_igralca)].uporabnisko_ime if id_igralca else None

def shrani_vse_skupaj():
    vse_skupaj.v_datoteko(DATOTEKA)

@bottle.get("/")
def zacetna_stran():
    bottle.response.set_cookie("kvadrat", None, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("img", "0", path="/", secret=SKRIVNOST)
    bottle.redirect("/igraj/")

@bottle.get("/vpis/")
def igraj():
    return bottle.template("podatki.html", vse_skupaj=vse_skupaj, napaka=None)

@bottle.post("/vpis/")
def igralca():
    i1 = poisci_ime_igralca(vse_skupaj, "igralec0")
    i2 = poisci_ime_igralca(vse_skupaj, "igralec1")
    if i1 == None or i2 == None:
        return bottle.template("podatki.html", vse_skupaj=vse_skupaj, napaka="Prosim, izberite oba igralca.")
    if i1 == i2:
        return bottle.template("podatki.html", vse_skupaj=vse_skupaj, napaka="Prosim, izberite dva različna igralca. Ne morete igrati sami proti sebi.")
    bottle.response.set_cookie("vpis", "da", path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("igralec0", i1, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("igralec1", i2, path="/", secret=SKRIVNOST)
    return bottle.redirect("/igra/")

@bottle.get("/igraj/")
def nova_igra():
    bottle.response.delete_cookie("vpis", path="/", secret=SKRIVNOST)
    k = bottle.request.get_cookie("kvadrat", secret=SKRIVNOST) == "da"
    id_igre = stiri_v_vrsto.nova_igra(k)
    bottle.response.set_cookie('id_igre', id_igre, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("igralec0", "igralec 1", path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("igralec1", "igralec 2", path="/", secret=SKRIVNOST)
    return bottle.redirect("/igra/")

@bottle.get("/igra/")
def pokazi_igro():
    id_igre = bottle.request.get_cookie('id_igre', secret=SKRIVNOST)
    igra, stanje = stiri_v_vrsto.igre[id_igre]
    plosca, figure = igra.plosca, igra.figurce()
    velikost = model.velikost_plosce
    igralecf, igralecp = bottle.request.get_cookie(f"igralec{len(plosca) % 2}", secret=SKRIVNOST), bottle.request.get_cookie(f"igralec{(len(plosca) + 1) % 2}", secret=SKRIVNOST)
    uporabnisko_ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    vpis = bottle.request.get_cookie("vpis", secret=SKRIVNOST) == "da"
    napaka = model.doloci_napako(stanje)
    im = bottle.request.get_cookie("img", secret=SKRIVNOST)
    if stanje == model.ZMAGA or len(plosca) == 16:
        i1, i2 = bottle.request.get_cookie("igralec0", secret=SKRIVNOST), bottle.request.get_cookie("igralec1", secret=SKRIVNOST)
        zmaga = stanje == model.ZMAGA
        vse_skupaj.vpisi_igro(i1, i2, zmaga, len(plosca))
        shrani_vse_skupaj()
    return bottle.template(
        "igra.html",
        {"stanje": stanje, "model": model, "plosca": plosca, "figure": figure, "napaka": napaka, "im": im,
        "velikost": velikost, "igralecf": igralecf, "igralecp": igralecp, "uporabnisko_ime": uporabnisko_ime, "vpis": vpis}
    )

@bottle.post("/igra/")
def igraj():
    id_igre = bottle.request.get_cookie('id_igre', secret=SKRIVNOST)
    f = bottle.request.forms.get("figura")
    m = bottle.request.forms.get("mesto").split(",")
    stiri_v_vrsto.igraj(id_igre, f, m)
    return bottle.redirect("/igra/")

@bottle.get("/static/<ime_datoteke:path>")
def slika(ime_datoteke):
    return bottle.static_file(ime_datoteke, "static")

@bottle.get("/navodila/")
def navodila():
    uporabnisko_ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    im = bottle.request.get_cookie("img", secret=SKRIVNOST)
    return bottle.template("navodila.html", {"uporabnisko_ime": uporabnisko_ime, "im": im}) if uporabnisko_ime is not None else bottle.template("navodila.html", {"im": im})

@bottle.get("/nastavitve/")
def nastavitve():
    uporabnisko_ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    kvadrat = bottle.request.get_cookie("kvadrat", secret=SKRIVNOST)
    im = int(bottle.request.get_cookie("img", secret=SKRIVNOST))
    return bottle.template("nastavitve.html", {"uporabnisko_ime": uporabnisko_ime, "kvadrat": kvadrat, "img": im, "st": STEVILO_IMG}) if uporabnisko_ime is not None else bottle.template("nastavitve.html", {"kvadrat": kvadrat, "img": im, "st": STEVILO_IMG})

@bottle.post("/nastavitve/")
def nastavitve():
    kvadrat = bottle.request.forms.get("kvadrat")
    img = bottle.request.forms.get("img")
    bottle.response.set_cookie("kvadrat", kvadrat, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("img", img, path="/", secret=SKRIVNOST)
    return bottle.redirect("/igraj/")

@bottle.get("/statistika/")
def stats():
    ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    if ime == None:
        return bottle.template("statistika-neprijavljeni.html")
    stat = vse_skupaj.poisci_uporabnika(ime).zgodovina
    uporabniki = sorted(vse_skupaj.uporabniki, key=lambda uporabnik: uporabnik.zgodovina, reverse=True)[:5]
    return bottle.template(
        "statistika.html", 
        {"stat": stat, "uporabnisko_ime": ime, "top5": uporabniki, "statistika": statistika,
        "JAZ": JAZ, "NASPROTNIK": NASPROTNIK, "ZMAGA": ZMAGA, "NEODLOCENO": NEODLOCENO, "PORAZ": PORAZ})

@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napakai=None, napakag=None)

@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo = bottle.request.forms.getunicode("geslo")
    uporabnik = vse_skupaj.poisci_uporabnika(uporabnisko_ime, geslo)
    if uporabnik:
        bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    elif not vse_skupaj.poisci_uporabnika(uporabnisko_ime):
        return bottle.template("prijava.html", napakai="To uporabniško ime ne obstaja.", napakag=None)
    else:
        return bottle.template("prijava.html", napakai=None, napakag="Napačno geslo")

@bottle.get("/registracija/")
def prijava_get():
    return bottle.template("registracija.html", napakai=None, napakag=None)

@bottle.post("/registracija/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo = bottle.request.forms.getunicode("geslo")
    for clovek in vse_skupaj.uporabniki:
        if clovek.uporabnisko_ime == uporabnisko_ime:
            return bottle.template("registracija.html", napakag=None, napakai="To uporabniško ime je že zasedeno.")
    if len(geslo) >= 6:
        uporabnik = statistika.Uporabnik(uporabnisko_ime, statistika.Uporabnik.zasifriraj_geslo(geslo), statistika.Igralec([]))
        vse_skupaj.uporabniki.append(uporabnik)
        shrani_vse_skupaj()
        bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    else:
        return bottle.template("registracija.html", napakag="Geslo mora biti dolgo najmanj 6 znakov.")

@bottle.post("/odjava/")
def odjava_post():
    bottle.response.delete_cookie("uporabnisko_ime", path="/", secret=SKRIVNOST)
    bottle.redirect("/")

bottle.run(reloader=True)