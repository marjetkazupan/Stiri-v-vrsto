<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Štiri v vrsto</title>

    <link rel="stylesheet" href="normalize.css">
    <link rel="stylesheet" href="oblikovanje.css">
</head>

<body>

  <h1>Štiri v vrsto</h1>

  Pred Vami je igra za dva igralca, a to ni igra *štiri v vrsto*, ki ste je vajeni. Cilj igre pa je tudi tu postaviti štiri podobne figure v vrsto.
  
  
  <h2>Navodila za igro</h2>
  
  Igra se prične s prazno igralno površino velikosti 4×4, na katero igralca izmenično postavljata figure.
  Te se razlikujejo v štirih lastnostih - vsaka figura je:
  
  <ul>
    <li> svetla ali temna </li>
    <li> z ozadjem ali brez </li>
    <li> kvadratna ali okrogla </li>
    <li> polna ali z luknjo </li>
  </ul>

  Ko je igralec na potezi, izbere eno izmed še neizbranih figur in jo poda nasprotniku.
  Ta jo nato postavi na igralno ploščo. Če pri tem doseže, da se štiri figure v vrsti (v stolpcu, vrstici ali na diagonali) ujemajo v eni izmed lastnosti (barva, velikost, oblika ali luknja), zmaga.
  
  Igro lahko igramo tudi tako, da je za zmago dovolj, če se figure v poljubnem kvadratku velikosti 2×2
  ujemajo v eni izmed prej naštetih lastnosti (izbirno pravilo).

  <br> </br>

  <form action="/igra/" method="post">
    <button type="submit">Igraj</button>
  </form>
</body>

</html>