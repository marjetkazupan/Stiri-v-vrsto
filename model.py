STEVILO_LASTNOSTI = 4
ZMAGA = "W"
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
        self.lastnosti = (self.barva, self.oblika, self.luknja, self.ozadje)
    # Lastnosti figur bomo pisali z 0 in 1 - Figura(0, 0, 0, 0) je svetla okrogla figura brez luknje in brez ozadja.

    def __repr__(self) -> str:
        return f"Figura{self.lastnosti}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Figura):
            return self.lastnosti == other.lastnosti
        else:
            return False

from itertools import product
vse_figure = [Figura(c, s, h, b) for (c, s, h, b) in list(product([0, 1], repeat=STEVILO_LASTNOSTI))]

class Igra:

    def __init__(self, plosca=None, figure=None) -> None:
        if plosca is not None:
            self.plosca = plosca
        else:
            self.plosca = {}
        if figure is not None:
            self.figure = figure
        else:
            self.figure = vse_figure.copy()

    def zmaga(self, mesto):
        # Preveri zmago; podamo še mesto spremembe (kam smo postavili figuro), da se izognemo nepotrebnim preverjanjem.
        i, j = mesto[0], mesto[1]

        # S seznamom vsote bomo preverjali, ali se figure v vrstici, stolpcu ali na diagonali 
        # ujemajo v kateri izmed lastnosti. Ker imajo lastnosti številsko vrednost 0 ali 1, 
        # lahko te vrednosti seštejemo. Figure se v eni izmed lastnosti ujemajo natanko tedaj, 
        # ko je ustrezna vsota enaka 0 (vse lastnosti so 0) ali 4 (vse lastnosti so 1).
        # Na prva štiri mesta bomo zapisali vsota lastnosti v stolpcu, na naslednja štiri v vrstici,
        # na zadnja štiri pa v diagonali (če se figura nahaja na kazteri izmed diagonal).
        vsote = [0 for _ in range(3 * velikost_plosce)]

        # Definiramo spremenljivke st, vr in diag, ki poskrbijo za to, da se funkcija 
        # predčasno prekine, če v stolpcu/vrstici/na diagonali sploh ni štirih figur.
        st, vr, diag = True, True, False

        for x in range(velikost_plosce):

            fig_st = self.plosca.get((x, j))
            fig_vr = self.plosca.get((i, x))

            # Če figure na ustreznem mestu ni, st oz. vr spremenimo na vrednost False.
            if fig_st == None:
                st = False
            if fig_vr == None:
                vr = False

            # Preverimo, ali je bila figura postavljena na diagonalo (v nasprotnem primeru zmage
            # na diagonali sploh ni treba preverjati).
            if i == j or i == 3 - j:
                diag = True
                if i == j:
                    fig_diag = self.plosca.get((x, x))
                if i == 3 - j:
                    fig_diag = self.plosca.get((x, 3 - x))
                if fig_diag == None:
                    diag = False

            # Ustavimo funkcijo, če niti v stolpcu niti v vrstici niti na diagonali ni štirih figur.
            if not(vr or st or diag):
                return False

            # Za vsako izmed lastnosti ustreznemu elementu seznama vsote pristejemo njeno vrednost.
            # Dodamo še 1, saj je 0 enota za seštevanje in tako ne bi opazili spremembe.
            for last in range(STEVILO_LASTNOSTI):
                if st:
                    vsote[last] += fig_st.lastnosti[last] + 1
                if vr:
                    vsote[3 + last] += fig_vr.lastnosti[last] + 1
                if diag:
                    vsote[7 + last] += fig_diag.lastnosti[last] + 1
        return 4 in vsote or 8 in vsote

    def zmaga_kvadrat(self):
        for i in range(3):
            for j in range(3):
                for last in range(4):
                    vsota = self.plosca.get((i, j)).lastnosti[last] + self.plosca.get((i + 1, j)).lastnosti[last] + self.plosca.get((i, j + 1)).lastnosti[last] + self.plosca.get((i + 1, j + 1)).lastnosti[last]
                    if vsota == 0 or vsota == 4:
                        return True
        return False

    def igraj(self, figura, mesto):
        self.figure.remove(figura)
        self.plosca[mesto] = figura
        if self.zmaga(mesto):
            return ZMAGA


def nova_igra():
    return Igra()


igra0 = Igra()

igra1 = Igra()
igra1.igraj(Figura(0, 0, 0, 0), (2, 1))

igra2 = Igra()
igra2.igraj(Figura(0, 0, 0, 0), (2, 1))
igra2.igraj(Figura(0, 1, 1, 1), (0, 1))
igra2.igraj(Figura(0, 1, 1, 0), (3, 1))
igra2.igraj(Figura(0, 1, 0, 1), (1, 1))

igra3 = Igra()
igra3.igraj(Figura(0, 0, 0, 0), (1, 1))
igra3.igraj(Figura(0, 1, 1, 1), (0, 0))
igra3.igraj(Figura(0, 1, 1, 0), (3, 3))
igra3.igraj(Figura(0, 1, 0, 1), (2, 2))

igra4 = Igra()
igra4.igraj(Figura(1, 1, 0, 0), (1, 1))
igra4.igraj(Figura(0, 1, 1, 1), (0, 0))
igra4.igraj(Figura(0, 1, 1, 0), (0, 1))
igra4.igraj(Figura(0, 1, 0, 1), (1, 0))


class Statistika:
    pass


class Igralec:

    def __init__(self, ime) -> None:
        self.ime = ime