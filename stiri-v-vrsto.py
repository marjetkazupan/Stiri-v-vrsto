import bottle, model, statistika, datetime


SKRIVNOST = "To je skrivnost."
JAZ = "jaz"
NASPROTNIK = "nasprotnik"
ZMAGA = "w"
NEODLOCENO = "t"
PORAZ = "l"

stiri_v_vrsto = model.Stiri_v_vrsto()
vse_skupaj = statistika.VseSkupaj.iz_datoteke("statistika.json")

def poisci_ime_igralca(vse_skupaj, ime_polja):
    id_igralca = bottle.request.forms.get(ime_polja)
    return vse_skupaj.uporabniki[int(id_igralca)].uporabnisko_ime if id_igralca else None

def vpisi_igro(stanje, turn):
    igralec1, igralec2 = bottle.request.get_cookie("igralec0"), bottle.request.get_cookie("igralec1")
    if igralec1 == "igralec 1" or igralec2 == "igralec 2":
        return
    if stanje == model.ZMAGA:
        z1 = 3 if turn % 2 == 0 else -1
        z2 = -1 if turn % 2 == 0 else 3
        vse_skupaj.poisci_uporabnika(igralec1).zgodovina.dvoboji.append(statistika.Dvoboj(nasprotnik=igralec2, zmaga=z1, poteza=turn, datum=datetime.date.today(), zacel=True))
        vse_skupaj.poisci_uporabnika(igralec2).zgodovina.dvoboji.append(statistika.Dvoboj(nasprotnik=igralec1, zmaga=z2, poteza=turn, datum=datetime.date.today(), zacel=False))
        shrani_vse_skupaj()
    if stanje != model.ZMAGA:
        vse_skupaj.poisci_uporabnika(igralec1).zgodovina.dvoboji.append(statistika.Dvoboj(nasprotnik=igralec2, zmaga=1, poteza=turn, datum=datetime.date.today(), zacel=True))
        vse_skupaj.poisci_uporabnika(igralec2).zgodovina.dvoboji.append(statistika.Dvoboj(nasprotnik=igralec1, zmaga=1, poteza=turn, datum=datetime.date.today(), zacel=False))
        shrani_vse_skupaj()

@bottle.get("/")
def zacetna_stran():
    bottle.redirect("/igraj/")

@bottle.get("/nova_igra/")
def igraj():
    bottle.response.set_cookie("vpis", "da", path="/")
    return bottle.template("podatki.html", vse_skupaj = vse_skupaj)

@bottle.get("/new/")
def novo():
    bottle.response.delete_cookie("vpis", path="/")
    bottle.redirect("/igraj/")

@bottle.post("/igraj/")
def igralca():
    i1 = str(poisci_ime_igralca(vse_skupaj, "igralec0")) if poisci_ime_igralca(vse_skupaj, "igralec0") is not None else "igralec 1"
    i2 = str(poisci_ime_igralca(vse_skupaj, "igralec1")) if poisci_ime_igralca(vse_skupaj, "igralec1") is not None else "igralec 2"
    bottle.response.set_cookie("igralec0", i1, path="/")
    bottle.response.set_cookie("igralec1", i2, path="/")
    return bottle.redirect("/igra/")

@bottle.get("/igraj/")
def nova_igra():
    id_igre = stiri_v_vrsto.nova_igra()
    bottle.response.set_cookie('id_igre', id_igre, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("igralec0", "igralec 1", path="/")
    bottle.response.set_cookie("igralec1", "igralec 2", path="/")
    return bottle.redirect("/igra/")

@bottle.get("/igra/")
def pokazi_igro():
    id_igre = bottle.request.get_cookie('id_igre', secret=SKRIVNOST)
    igra, stanje = stiri_v_vrsto.igre[id_igre]
    plosca, figure = igra.plosca, igra.figurce()
    velikost = model.velikost_plosce
    igralecf, igralecp = bottle.request.get_cookie(f"igralec{len(plosca) % 2}"), bottle.request.get_cookie(f"igralec{(len(plosca) + 1) % 2}")
    uporabnisko_ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    vpis = bottle.request.get_cookie("vpis") == "da"
    if stanje == model.ZMAGA or len(plosca) == 16:
        vpisi_igro(stanje, len(plosca))
    return bottle.template(
        "igra.html",
        {"stanje": stanje, "model": model, "plosca": plosca, "figure": figure,
        "velikost": velikost, "igralecf": igralecf, "igralecp": igralecp, "uporabnisko_ime": uporabnisko_ime, "vpis": vpis}
    ) if uporabnisko_ime is not None else bottle.template(
        "igra.html",
        {"stanje": stanje, "model": model, "plosca": plosca, "figure": figure,
        "velikost": velikost, "igralecf": igralecf, "igralecp": igralecp, "vpis": vpis}
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
    return bottle.template("navodila.html", {"uporabnisko_ime": uporabnisko_ime}) if uporabnisko_ime is not None else bottle.template("navodila.html")

@bottle.get("/nastavitve/")
def nastavitve():
    uporabnisko_ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    return bottle.template("nastavitve.html", {"uporabnisko_ime": uporabnisko_ime}) if uporabnisko_ime is not None else bottle.template("nastavitve.html")

def shrani_vse_skupaj():
    vse_skupaj.v_datoteko("statistika.json")

@bottle.get("/statistika/")
def stats():
    ime = bottle.request.get_cookie("uporabnisko_ime", secret=SKRIVNOST)
    if ime == None:
        return bottle.template("statistika-neprijavljeni.html")
    stat = vse_skupaj.poisci_uporabnika(ime).zgodovina
    uporabniki = sorted(vse_skupaj.uporabniki, key=lambda uporabnik: uporabnik.zgodovina, reverse=True)[:5]
    return bottle.template(
        "statistika.html", 
        {"stat": stat, "uporabnisko_ime": ime, "top5": uporabniki,
        "JAZ": JAZ, "NASPROTNIK": NASPROTNIK, "ZMAGA": ZMAGA, "NEODLOCENO": NEODLOCENO, "PORAZ": PORAZ})

@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napaka=None)

@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo = bottle.request.forms.getunicode("geslo")
    uporabnik = vse_skupaj.poisci_uporabnika(uporabnisko_ime, geslo)
    if uporabnik:
        bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    else:
        return bottle.template("prijava.html", napaka="Napačno geslo")

@bottle.get("/registracija/")
def prijava_get():
    return bottle.template("registracija.html", napaka=None)

@bottle.post("/registracija/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo = bottle.request.forms.getunicode("geslo")
    for clovek in vse_skupaj.uporabniki:
        if clovek.uporabnisko_ime == uporabnisko_ime:
            return bottle.template("registracija.html", napaka="To uporabniško ime je že zasedeno.")
    if len(geslo) >= 6:
        uporabnik = statistika.Uporabnik(uporabnisko_ime, statistika.Uporabnik.zasifriraj_geslo(geslo), statistika.Igralec([]))
        vse_skupaj.uporabniki.append(uporabnik)
        shrani_vse_skupaj()
        bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    else:
        return bottle.template("registracija.html", napaka="Geslo mora biti dolgo najmanj 6 znakov.")

@bottle.post("/odjava/")
def odjava_post():
    bottle.response.delete_cookie("uporabnisko_ime", path="/", secret=SKRIVNOST)
    bottle.redirect("/")

bottle.run(reloader=True, debug=True)