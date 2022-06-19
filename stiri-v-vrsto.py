import bottle, model
from datetime import date


SKRIVNOST = "To je skrivnost."

stiri_v_vrsto = model.Stiri_v_vrsto()

@bottle.get("/")
def zacetna_stran():
    bottle.redirect("/igraj/")

@bottle.get("/nova_igra/")
def igraj():
    return bottle.template("podatki.html")

@bottle.get("/igraj/")
def nova_igra():
    id_igre = stiri_v_vrsto.nova_igra()
    bottle.response.set_cookie('id_igre', id_igre, path="/", secret=SKRIVNOST)
    return bottle.redirect("/igra/")

@bottle.get("/igra/")
def pokazi_igro():
    id_igre = bottle.request.get_cookie('id_igre', secret=SKRIVNOST)
    igra, stanje = stiri_v_vrsto.igre[id_igre]
    plosca = igra.plosca
    velikost = model.velikost_plosce
    figure = igra.figurce()
    return bottle.template(
        "igra.html",
        {"stanje": stanje, "model": model, "plosca": plosca, "figure": figure, "velikost": velikost}
    )

@bottle.post("/igra/")
def igraj():
    id_igre = bottle.request.get_cookie('id_igre', secret=SKRIVNOST)
    barva, oblika, luknja, ozadje = (int(st) for st in bottle.request.forms.get("figura"))
    figura = model.Figura(barva, oblika, luknja, ozadje)
    mesto = tuple(int(st) for st in bottle.request.forms.get("mesto"))
    stiri_v_vrsto.igraj(id_igre, figura, mesto)
    return bottle.redirect("/igra/")

@bottle.get("/static/<ime_datoteke:path>")
def slika(ime_datoteke):
    return bottle.static_file(ime_datoteke, "static")

@bottle.get("/navodila/")
def navodila():
    return bottle.template("navodila.html")

@bottle.get("/nastavitve/")
def nastavitve():
    return bottle.template("nastavitve.html")

bottle.run(reloader=True, debug=True)