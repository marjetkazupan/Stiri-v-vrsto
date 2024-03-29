from dataclasses import dataclass
from datetime import date
import json
from typing import List

ZMAGA = "w"
NEODLOCENO = "t"
PORAZ = "l"
TOCKE_ZMAGA = 3
TOCKE_NEODLOCENO = 1
TOCKE_PORAZ = -1


@dataclass
class Dvoboj:
    nasprotnik: str
    zmaga: str
    # v atribut zmaga bomo vnašali konstante zmaga, poraz in neodloceno
    poteza: int
    datum: date
    zacel: bool

    def tocke(self):
        if self.zmaga == ZMAGA:
            return TOCKE_ZMAGA
        if self.zmaga == NEODLOCENO:
            return TOCKE_NEODLOCENO
        if self.zmaga == PORAZ:
            return TOCKE_PORAZ

    def v_slovar(self):
        return {
            "nasprotnik": self.nasprotnik,
            "zmaga": self.zmaga,
            "poteza": self.poteza,
            "datum": self.datum.isoformat(),
            "zacel": self.zacel
        }

    @classmethod
    def iz_slovarja(cls, slovar):
        return cls(
                nasprotnik=slovar["nasprotnik"],
                zmaga=slovar["zmaga"],
                poteza=slovar["poteza"],
                datum=date.fromisoformat(slovar["datum"]),
                zacel=slovar["zacel"]
            )

@dataclass
class Igralec:
    dvoboji: List[Dvoboj]

    def rating(self):
        return sum(dvoboj.tocke() for dvoboj in self.dvoboji)

    def odigrane_igre(self):
        return len(self.dvoboji)

    def __lt__(self, other):
        return self.rating() < other.rating() or (self.rating() == other.rating() and self.odigrane_igre() < other.odigrane_igre())

    def dodaj_igro(self, nasprotnik, zmaga, poteza, datum, zacel):
        dvoboj = Dvoboj(nasprotnik, zmaga, poteza, datum, zacel)
        self.dvoboji.append(dvoboj)

    def prestej(self, k):
        return [dvoboj.zmaga for dvoboj in self.dvoboji].count(k)

    def v_slovar(self):
        return {
            "dvoboji": [dvoboj.v_slovar() for dvoboj in self.dvoboji]
        }

    @classmethod
    def iz_slovarja(cls, slovar):
        return cls(
            dvoboji=[Dvoboj.iz_slovarja(sl) for sl in slovar["dvoboji"]]
        )

@dataclass
class Uporabnik:
    uporabnisko_ime: str
    zasifrirano_geslo: str
    zgodovina: Igralec

    @staticmethod
    def zasifriraj_geslo(geslo_v_cistopisu):
        return geslo_v_cistopisu[::-1]

    def preveri_geslo(self, geslo_v_cistopisu):
        return self.zasifriraj_geslo(geslo_v_cistopisu) == self.zasifrirano_geslo

    def v_slovar(self):
        return {
            "uporabnisko_ime": self.uporabnisko_ime,
            "zasifrirano_geslo": self.zasifrirano_geslo,
            "zgodovina": self.zgodovina.v_slovar()
        }

    @classmethod
    def iz_slovarja(cls, slovar):
        return cls(
            uporabnisko_ime=slovar["uporabnisko_ime"],
            zasifrirano_geslo=slovar["zasifrirano_geslo"],
            zgodovina=Igralec.iz_slovarja(slovar["zgodovina"])
        )

@dataclass
class VseSkupaj:
    uporabniki: List[Uporabnik]

    def poisci_uporabnika(self, uporabnisko_ime, geslo=None):
        for uporabnik in self.uporabniki:
            if uporabnik.uporabnisko_ime == uporabnisko_ime:
                if geslo == None or uporabnik.preveri_geslo(geslo):
                    return uporabnik

    def v_slovar(self):
        return {
            "uporabniki": [uporabnik.v_slovar() for uporabnik in self.uporabniki],
        }

    @classmethod
    def iz_slovarja(cls, slovar):
        return cls(
            uporabniki=[Uporabnik.iz_slovarja(sl) for sl in slovar["uporabniki"]]
        )
    
    def v_datoteko(self, ime_datoteke):
        with open(ime_datoteke, "w") as d:
            json.dump(self.v_slovar(), d, ensure_ascii=False, indent=4)

    @classmethod
    def iz_datoteke(cls, ime_datoteke):
        with open(ime_datoteke) as d:
            return cls.iz_slovarja(json.load(d))

    def vpisi_igro(self, i1, i2, zmaga, turn):
        if i1 == "igralec 1" or i2 == "igralec 2":
            return
        if zmaga:
            z1 = ZMAGA if turn % 2 == 0 else PORAZ
            z2 = PORAZ if turn % 2 == 0 else ZMAGA
        else:
            z1 = NEODLOCENO
            z2 = NEODLOCENO
        self.poisci_uporabnika(i1).zgodovina.dodaj_igro(nasprotnik=i2, zmaga=z1, poteza=turn, datum=date.today(), zacel=True)
        self.poisci_uporabnika(i2).zgodovina.dodaj_igro(nasprotnik=i1, zmaga=z2, poteza=turn, datum=date.today(), zacel=False)