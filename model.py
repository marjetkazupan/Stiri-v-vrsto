STEVILO_LASTNOSTI = 4
ZMAGA = "W"
ZACETEK = "Z"
NAPACNA_FIGURA = "-f"
NAPACNO_POLJE = "-p"
ZASEDENA_FIGURA = "-fz"
ZASEDENO_POLJE = "-pz"

# Zmaga kvadrat samo za 4 lastnosti
# Število lastnosti naj izberejo, ne vpišejo (ali pa daj navodilo in check)

velikost_plosce = 2 ** (STEVILO_LASTNOSTI // 2)

class Figura:
    # Figure bodo nabori z vrednostmi 0 in 1.
    def __init__(self, barva, oblika, luknja, ozadje):
        self.barva = barva
        self.oblika = oblika
        self.luknja = luknja
        self.ozadje = ozadje
        self.lastnosti = (barva, oblika, luknja, ozadje)
    # Lastnosti figur bomo pisali z 0 in 1 - Figura(0, 0, 0, 0) je svetla okrogla 
    # figura brez luknje in brez ozadja.

    def __repr__(self) -> str:
        return f"Figura{self.lastnosti}"

    def __str__(self) -> str:
        return f"{self.barva}{self.oblika}{self.luknja}{self.ozadje}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Figura):
            return self.lastnosti == other.lastnosti
        else:
            return False

from itertools import product
vse_figure = [Figura(c, s, h, b) for (c, s, h, b) in list(product([0, 1], repeat=STEVILO_LASTNOSTI))]

class Igra:

    def __init__(self, plosca=None, figure=None, kvadrat=False) -> None:
        if plosca is not None:
            self.plosca = plosca
        else:
            self.plosca = {}
        if figure is not None:
            self.figure = figure
        else:
            self.figure = vse_figure.copy()
        self.kvadrat = kvadrat

    def zmaga(self, mesto):
        # Funkcija preveri zmago (ali se je igra v tej potezi končala); 
        # funkciji podamo še mesto spremembe (kam smo postavili figuro), 
        # da se izognemo nepotrebnim preverjanjem.
        i, j = mesto

        # Naredimo seznam seznamov figur, ki so postavljene na mesta, ki tvorijo vrsto 
        # in na katerih bi potencialno lahko prišlo do zmage. 
        # Najprej dodamo seznam figur v stolpcu in seznam figur v vrstici.
        mozne_zmage = [
            [self.plosca.get((x, j)) for x in range(velikost_plosce)],
            [self.plosca.get((i, x)) for x in range(velikost_plosce)]
        ]

        # Preverimo, ali je mesto, na katero smo postavili figuro, na diagonali. Če je, dodamo še diagonalo.
        if i == j:
            mozne_zmage.append([self.plosca.get((x, x)) for x in range(velikost_plosce)])
        
        if i == velikost_plosce - 1 - j:
            mozne_zmage.append([self.plosca.get((x, velikost_plosce - 1 - x)) for x in range(velikost_plosce)])
            
        # Če je vklopljeno izbirno pravilo za zmago, dodamo še vse možne 2 * 2 kvadratke. 
        # To pravilo lahko uporabimo le na mreži 4 * 4.
        if self.kvadrat:
            kv = [(i, j), (i, j - 1), (i - 1, j), (i - 1, j - 1)]
            for x, y in kv:
                mozne_zmage.append([self.plosca.get((x, y)), self.plosca.get((x + 1, y)), self.plosca.get((x, y + 1)), self.plosca.get((x + 1, y + 1))])
        
        # Preverimo ujemanje figur.
        for seznam in mozne_zmage:
            if None in seznam:
                continue
            vsota = [0 for _ in range(STEVILO_LASTNOSTI)]
            for figura in seznam:
                for last in range(STEVILO_LASTNOSTI):
                    vsota[last] += figura.lastnosti[last]
            if 0 in vsota or 4 in vsota:
                return True
        return False

    def igraj(self, figura, mesto):
        if figura not in self.figure:
            return ZASEDENA_FIGURA
        if self.plosca.get(mesto) is not None:
            return ZASEDENO_POLJE
        self.figure.remove(figura)
        self.plosca[mesto] = figura
        if self.zmaga(mesto):                
            return ZMAGA
    
    def figurce(self):
        fig = self.figure.copy()
        while len(fig) != velikost_plosce ** 2:
            fig.append(1)
        figure = []
        for i in range(velikost_plosce):
            figure.append(fig[velikost_plosce * i : velikost_plosce * i + velikost_plosce])
        return figure


def nova_igra(k=False):
    return Igra(kvadrat=k)

def preveri_input(f, m):
    if len(f) != STEVILO_LASTNOSTI:
        return NAPACNA_FIGURA
    for st in f:
        if st not in "01":
            return NAPACNA_FIGURA
    if len(m) != 2:
        return NAPACNO_POLJE
    for koord in m:
        if int(koord) >= velikost_plosce:
            return NAPACNO_POLJE


class Stiri_v_vrsto:
    def __init__(self) -> None:
        self.igre = {}

    def prost_id_igre(self):
        if not self.igre:
            return 0
        else:
            return max(self.igre.keys()) + 1
    
    def nova_igra(self, k=False):
        i = self.prost_id_igre()
        igra = nova_igra(k)
        self.igre[i] = (igra, ZACETEK)
        return i
    
    def igraj(self, i, f, m):
        igra, stanje = self.igre[i]
        s = preveri_input(f, m)
        if s:
            stanje = s
        else:
            barva, oblika, luknja, ozadje = (int(st) for st in f)
            figura = Figura(barva, oblika, luknja, ozadje)
            mesto = tuple(int(st) for st in m)
            stanje = igra.igraj(figura, mesto)
        self.igre[i] = (igra, stanje)