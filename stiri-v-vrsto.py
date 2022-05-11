import bottle, model

# Naredimo nov objekt razreda vislice.
stiri_v_vrsto = model.Stiri_v_vrsto()

@bottle.get("/")
def indeks():
    return bottle.template("views/index.tpl")

@bottle.post("/igra/")
def nova_igra():
    i = stiri_v_vrsto.nova_igra()
    return bottle.redirect(f"/igra/{i}/")

@bottle.get("/igra/<id_igre:int>/")
def pokazi_igro(id_igre):
    igra, stanje = stiri_v_vrsto.igre[id_igre]
    plosca = igra.plosca
    figure = igra.figure
    return bottle.template("views/igra.tpl", {"stanje": stanje, "model": model, "plosca": plosca, "figure": figure})

@bottle.post("/igra/<id_igre:int>/")
def igraj(id_igre):
    barva, oblika, luknja, ozadje = (int(st) for st in bottle.request.forms.get("figura"))
    figura = model.Figura(barva, oblika, luknja, ozadje)
    mesto = tuple(int(st) for st in bottle.request.forms.get("mesto"))
    stiri_v_vrsto.igraj(id_igre, figura, mesto)
    return bottle.redirect(f"/igra/{id_igre}/")

bottle.run(reloader=True, debug=True)