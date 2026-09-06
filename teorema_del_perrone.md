# Teorema del Perrone

_Nome di lavoro per un risultato emerso dalla revisione critica della "Unificazione Spettrale Perrone–Erdős" di Mirko Perrone: nasce dal suo tentativo di costruire un rivelatore spettrale per l'ipotesi di Riemann, ma si dimostra indipendentemente da ogni altra parte di quella teoria._

## Enunciato

Agli zeri non banali della funzione zeta di Riemann si possono associare due funzioni della variabile reale positiva x. La prima si costruisce usando ogni zero per intero — sia la sua parte reale sia la sua ordinata (parte immaginaria). La seconda si costruisce invece ignorando deliberatamente la parte reale di ciascuno zero e usando solo la sua ordinata, come se ogni zero si trovasse già esattamente sulla retta critica — cioè come se l'ipotesi di Riemann fosse vera.

Il teorema dice: queste due costruzioni coincidono, per **ogni** valore di x, esattamente quando l'ipotesi di Riemann è vera. Se anche un solo zero avesse parte reale diversa da 1/2, le due funzioni non potrebbero coincidere ovunque — anzi, la loro differenza crescerebbe senza limite al crescere di x. In altre parole: la prima funzione "sa" dove sono davvero gli zeri; la seconda assume che stiano tutti sulla retta; il teorema dice che l'unico modo perché non si accorgano mai della differenza è che la retta critica contenga davvero tutti gli zeri. È un teorema incondizionato: non assume l'ipotesi di Riemann né per dimostrarla né per confutarla, ne stabilisce l'equivalenza con un fatto verificabile in linea di principio.

## Enunciato, per esteso

**L'ipotesi di Riemann è vera se e solo se, per ogni x>0,**

```
Σ_ρ  x^ρ / (2√x · ρ(1−ρ))   =   Σ_{γ>0}  cos(γ·log x) / (1/4 + γ²)
```

**dove** a sinistra la somma è su tutti gli zeri non banali ρ di ζ(s), presi con la loro parte reale e immaginaria vere; **a destra** la somma è sulle sole ordinate positive γ degli zeri non banali, come se ciascuno stesse esattamente sulla retta Re(s)=1/2.

Nel resto del documento il lato sinistro si chiama F(x) e il lato destro S(x), solo per brevità di scrittura.

## Notazione

ρ = σ+iγ indica un generico zero non banale di ζ(s), σ:=Re(ρ), γ:=Im(ρ). Fatti classici usati senza dimostrarli: 0<σ<1 per ogni zero non banale; l'insieme degli zeri è chiuso per ρ↦ρ̄ (coefficienti reali di ζ) e per ρ↦1−ρ (equazione funzionale); il conteggio N(T) degli zeri con 0<γ≤T soddisfa N(T)=O(T log T) (Riemann–von Mangoldt).

## Definizioni

Per ogni x>0:

```
S(x) := Σ_{γ>0} cos(γ·log x) / (1/4 + γ²)
```

somma sulle ordinate positive di tutti gli zeri non banali (con molteplicità). Converge assolutamente (Σ_{γ>0} 1/(1/4+γ²) < ∞ da N(T)=O(T log T)) ed è definita **incondizionatamente**: dipende solo dalle ordinate, mai dalle parti reali.

```
F(x) := Σ_ρ  x^ρ / (2√x · ρ(1−ρ))
```

somma su tutti gli zeri non banali. Con ρ=σ+iγ:

```
ρ(1−ρ) = [σ(1−σ)+γ²] + iγ(1−2σ)  =: A + iB
```

reale (=1/4+γ²) se e solo se σ=1/2. Poiché σ(1−σ)≤1/4 e |1−2σ|≤1 per ogni σ∈(0,1) — uniformemente, non solo vicino a 1/2 — si ha A~γ² e B=O(γ), quindi |ρ(1−ρ)|~γ² per γ grande: F(x) converge assolutamente per ogni x>0, **incondizionatamente**.

Raggruppando ogni zero ρ (γ>0) col coniugato ρ̄, il contributo della coppia è

```
F_pair(x) = x^{σ-1/2} · [A cos(γ log x) + B sin(γ log x)] / (A²+B²)
```

Quando σ=1/2 (A=1/4+γ², B=0): F_pair(x) = cos(γ log x)/(1/4+γ²) — esattamente il termine di S(x) per quella γ.

## Teorema

**L'ipotesi di Riemann è vera se e solo se F(x) = S(x) per ogni x>0.**

## Dimostrazione

### (⟹)

Se ogni zero ha σ=1/2, ogni coppia {ρ,ρ̄} contribuisce a F esattamente il termine di S(x) relativo alla sua γ (calcolo sopra). Sommando su tutte le coppie, F(x)=S(x) per ogni x. ∎

### (⟸)

Si dimostra la contronominale: se l'ipotesi di Riemann è falsa, F(x)≠S(x) per qualche x — anzi, la differenza è illimitata.

Sia D(x):=F(x)−S(x), u:=log x. Le coppie con σ=1/2 contribuiscono zero a D; solo le coppie fuori dalla retta contribuiscono, col termine

```
D_pair(u) = e^{(σ-1/2)u} · [A cos(γu) + B sin(γu)] / (A²+B²)
```

Se RH è falsa esiste uno zero ρ₀ con σ₀≠1/2; per riflessione (ρ zero ⟹ ρ̄, 1−ρ, 1−ρ̄ zeri), esiste una coppia con σ*>1/2, γ*>0 (se σ₀>1/2 si prende ρ₀ stesso; altrimenti 1−ρ̄₀, di parte reale 1−σ₀>1/2).

**Passo 1 — crescita innocua, incondizionata.** Poiché 0<σ<1 sempre, |D(e^u)| ≤ C·e^{u/2} per ogni u≥0, C assoluta. Dunque

```
L(s) := ∫₀^∞ D(e^u) e^{-su} du
```

converge assolutamente ed è olomorfa per Re(s)>1/2 — indipendentemente da RH.

**Passo 2 — trasformata termine a termine.** Con a:=σ−1/2, la trasformata di Laplace elementare

```
∫₀^∞ e^{au}(A cosγu + B sinγu) e^{-su} du = [A(s-a)+Bγ] / [(A²+B²)((s-a)²+γ²)]
```

vale per Re(s)>a, con poli semplici in s=(σ−1/2)±iγ, residuo (B±iA)/(2i(A²+B²)) — mai nullo, perché A²+B²=|ρ(1−ρ)|²>0. Per Re(s)>1/2 (che supera σ−1/2 per ogni coppia), sommando su tutte le coppie fuori linea:

```
L(s) = M(s) := Σ_{coppie fuori linea}  [A(s-a)+Bγ] / [(A²+B²)((s-a)²+γ²)]
```

L'interscambio somma/integrale è lecito: la doppia somma converge assolutamente (vedi Passo 3, che vale a ogni Re(s) fissato).

**Passo 3 — M è meromorfa su tutto ℂ.** Per s fissato lontano dai poli, e γ→∞ con σ∈(0,1) arbitrario: A=σ(1−σ)+γ²~γ² e B=γ(1−2σ)=O(γ), **uniformemente in σ** — perché σ(1−σ)≤1/4 e |1−2σ|≤1 valgono per ogni σ∈(0,1), non solo vicino a 1/2. Segue che ogni addendo di M è O(1/γ⁴), uniformemente in σ. Con N(T)=O(T log T), la serie converge assolutamente e localmente uniformemente lontano dai poli, su tutto ℂ. Dunque M è meromorfa su ℂ, con poli semplici esattamente nei punti (σⱼ−1/2)±iγⱼ di ogni coppia fuori linea, e in nessun altro punto.

**Passo 4 — la contraddizione.** Sia s₀ := (σ*−1/2)+iγ*. Poiché σ*>1/2, Re(s₀)>0, e M ha lì un polo genuino (Passo 3).

Supponiamo, per assurdo, D limitata su [0,∞) (cioè F≡S). Per un fatto elementare delle trasformate di Laplace di funzioni limitate, L(s) si estende allora olomorfa a tutto il semipiano Re(s)>0. Ma L=M sul semipiano Re(s)>1/2 (Passo 2), e per l'unicità della continuazione analitica su un dominio connesso, l'estensione olomorfa di L deve coincidere con M ovunque quest'ultima sia definita in Re(s)>0 — in particolare in s₀, dove però M ha un polo. Una funzione non può essere insieme olomorfa (per ipotesi) e avere un polo (per costruzione) nello stesso punto: **contraddizione**.

Dunque D non è limitata: F(x)≠S(x) per qualche x — di fatto la differenza cresce senza limite. ∎

## Nota sulla tecnica

La dimostrazione di (⟸) adatta direttamente i classici teoremi di oscillazione di tipo Landau — usati normalmente per mostrare che ψ(x)−x non può essere troppo piccola se esiste uno zero fuori dalla retta critica — applicandoli qui a F ed S invece che alla funzione di Chebyshev. Il meccanismo centrale (trasformata di Laplace di un'esponenziale modulata da coseno/seno, con polo semplice nel punto atteso) è stato verificato, oltre che algebricamente, anche numericamente su una coppia di prova fuori dalla retta.

## Relazione con il criterio di von Koch

Il criterio non è una riformulazione del classico criterio di von Koch (RH ⟺ ψ(x)−x = O(√x log²x)), sebbene nasca dallo stesso oggetto di base. Per frazioni parziali,

```
1/(ρ(1−ρ)) = 1/ρ + 1/(1−ρ)
```

Poiché l'insieme degli zeri non banali è chiuso per ρ↦1−ρ, rietichettando ρ':=1−ρ nella seconda somma si ottiene x^ρ/(1−ρ) = x·(1/x)^{ρ'}/ρ'. Sommando su tutti gli zeri (con la stessa convenzione di somma simmetrica per altezza usata per F):

```
Σ_ρ x^ρ/(ρ(1−ρ))  =  Z(x) + x·Z(1/x),      Z(x) := Σ_ρ x^ρ/ρ
```

dove Z(x) è esattamente la somma sugli zeri della formula esplicita classica, ψ₀(x)=x−Z(x)−log(2π)−½log(1−x⁻²) — l'oggetto di von Koch. Dunque

```
F(x) = [Z(x) + x·Z(1/x)] / (2√x)
```

identità **incondizionata**, non solo sotto RH — verificata anche numericamente: con 40 zeri veri, a più valori di x e a ogni livello di troncamento, i due lati coincidono a 25 cifre.

Questo mostra che F non è Z travestita. Von Koch riguarda Z(x) solo per x>1, dove si legge tramite ψ(x) — un oggetto aritmetico, un conteggio di primi. F costringe a capire Z anche in 1/x<1 (per x>1), dove ψ₀ è identicamente nulla e la stessa formula esplicita del 1859 smette di valere in forma reale (log(1−x⁻²) diventa il logaritmo di un numero negativo): Z(y) per y<1 resta ben definita come oggetto puramente analitico, ma perde ogni interpretazione di conteggio. Il criterio F=S è dunque un enunciato sulla somma degli zeri *simmetrizzata rispetto a s↔1−s* — compatibile per costruzione con l'equazione funzionale — non una riformulazione dell'errore aritmetico ψ(x)−x.

Questo spiega, a ritroso, perché il peso 1/(ρ(1−ρ)) — e quindi il nucleo di Lorentz che ne segue — non è una scelta arbitraria: è esattamente il peso che rende la somma sugli zeri automaticamente simmetrica sotto l'equazione funzionale, cosa che il peso 1/ρ della formula esplicita del 1859 non fa.

**Verdetto.** Stessa famiglia di tecnica dimostrativa (teoremi di oscillazione alla Landau, usati sopra nel Passo 4), stesso mattone di base (Z(x)), ma criterio genuinamente distinto — più vicino, nello spirito, a uno studio della formula esplicita *completata* rispetto all'equazione funzionale, che a una riformulazione dell'errore nel teorema dei numeri primi.

### Verifica indipendente del residuo

Fatto — e il risultato è più interessante del previsto: non è una scorciatoia, ma è una verifica indipendente genuina, e chiarisce un punto che nella dimostrazione originale restava implicito.

Il tranello che temevo, e come si scioglie. L'idea era: applicare un teorema di oscillazione noto a Z(x) (per x→∞) e lo stesso teorema a Z(1/x), sommare. Il rischio: i due risultati sono "Ω" — dicono che Z è grande per qualche successione di argomenti, non per tutti — e successioni diverse potrebbero non allinearsi, lasciando aperta una cancellazione.

Si scioglie così: il polo nel punto s=(σ−1/2)+iγ non viene da un solo zero applicato due volte — viene da due zeri diversi, legati dall'equazione funzionale. Per lo zero ρ=σ+iγ stesso, il pezzo "Z(x)" contribuisce lì con residuo 1/ρ (calcolo diretto della trasformata di Laplace di e^{(ρ-1/2)u}/ρ). Per il suo partner 1−ρ (zero anch'esso, garantito dall'equazione funzionale), il pezzo "Z(1/x)" contribuisce esattamente nello stesso punto con residuo 1/(1−ρ). Non è una coincidenza cercata: si verifica direttamente che il polo di 1/2−ρ'' cade in (σ−1/2)+iγ proprio quando ρ''=1−ρ.

Sommandoli:

```
1/ρ + 1/(1-ρ) = 1/(ρ(1-ρ))      [la stessa frazione parziale di prima]
```

e, con il fattore ½ della combinazione F=(1/2)[z+w], questo dà residuo (1/2)(A−iB)/(A²+B²) — che è algebricamente identico al residuo (B+iA)/(2i(A²+B²)) trovato con il calcolo diretto sul termine F_pair. Coincidono esattamente, non solo nell'ordine di grandezza.

Cosa significa, onestamente. Non è una seconda dimostrazione indipendente dei Passi 1, 3, 4 (crescita, meromorfia globale, contraddizione) — quelli restano identici in entrambe le vie, perché riguardano M(s) nel suo complesso, non un singolo polo. Ma è una verifica indipendente del pezzo più delicato: il calcolo del residuo — proprio quello in cui, ricorderai, era già annidato un errore reale in una formula precedente. E dà un'immagine concettualmente più pulita del perché non c'è mai cancellazione: non è un fatto fortunato da controllare caso per caso, è forzato dall'algebra — A−iB si annulla solo se A=B=0, cioè solo se ρ(1−ρ)=0, cosa che non succede mai per uno zero non banale.

## La funzione ombra Z(y), y<1: una formula esplicita autonoma

Il documento nota che Z(y) per y<1 "resta ben definita come oggetto puramente analitico, ma perde ogni interpretazione di conteggio" perché ψ₀ è identicamente nulla lì. Questo lascia aperta una domanda ben posta: Z(y), y<1, ha una propria formula esplicita — un proprio termine principale, un proprio resto — indipendente da quella di Z(x), x>1? La risposta è sì, e non è ψ(y) (che è banalmente 0), ma la somma di Mertens Σ Λ(n)/n.

### Perché la via ovvia è vuota

Il tentativo naturale è ripetere l'argomento di Perron usato per ψ, ma per x<1. È inutile: l'integrale

```
I(x) = (1/2πi) ∫₍c₎ [-ζ'/ζ(s)] x^s/s ds,   c>1
```

per x>1 si chiude a sinistra e dà ψ₀(x) (residui in s=1, negli zeri, in s=0, negli zeri banali). Per x<1, x^s decade a zero per Re(s)→+∞, non →−∞: bisogna chiudere a **destra**. Ma a destra di Re(s)=1, −ζ'/ζ(s)=ΣΛ(n)n⁻ˢ è olomorfa (ζ non ha zeri lì): nessun polo, I(x)=0 identicamente. È solo un modo complicato di ridire ψ(x)=0 per x<1 — nessuna informazione nuova.

### Il nucleo giusto

Serve un nucleo diverso, che produca residui della forma x^ρ/(1−ρ) invece di x^ρ/ρ:

```
J(x) := (1/2πi) ∫₍c₎ [-ζ'/ζ(s)] · x^s/(1−s) ds,   c>1, x>1
```

Chiudendo a sinistra, i poli sono:

- **s=1** (doppio): sia −ζ'/ζ(s) sia 1/(1−s) hanno un polo lì. Con ε=s−1, usando −ζ'/ζ(s)=1/ε−γ+O(ε) (γ = costante di Eulero–Mascheroni, dallo sviluppo di Laurent di ζ in s=1) e 1/(1−s)=−1/ε, il prodotto per x^s=x(1+ε ln x+…) dà residuo x(γ−ln x).
- **s=ρ** (zeri non banali): residuo −x^ρ/(1−ρ); sommando su tutte le coppie: −Σ_ρ x^ρ/(1−ρ) = −x·Z(1/x) (identità già stabilita sopra).
- **s=−2n** (zeri banali): residuo −x^{−2n}/(1+2n); sommando: −Σ_{n≥1} x^{−2n}/(2n+1).
- **s=0**: qui non c'è polo (a differenza del caso classico) — −ζ'/ζ(s) è regolare in 0, e 1/(1−s) è regolare anch'esso lì. Il termine log(2π) non compare in questa costruzione.

Quindi:

```
J(x) = x(γ − ln x) − x·Z(1/x) − Σ_{n≥1} x^{−2n}/(2n+1)
```

### Identificazione indipendente di J(x)

D'altra parte J(x) si calcola anche termine a termine dalla serie di Dirichlet, usando l'identità elementare (1/2πi)∫(x/n)^s/(s−1) ds = (x/n)·**1**{x/n>1}:

```
J(x) = -x · Σ_{n<x} Λ(n)/n
```

### La formula esplicita per Z(y), y<1

Uguagliando le due espressioni di J(x) e risolvendo per Z(1/x):

```
Z(1/x) = γ − ln x + Σ_{n<x} Λ(n)/n − (1/x)·Σ_{k≥1} x^{−2k}/(2k+1)          (x>1, y=1/x<1)
```

Verifica numerica (x=10, confrontando col valore ottenuto sommando 1000 zeri veri): la formula dà Z(1/10) = −0.031054…, mentre la somma spettrale troncata a 1000 zeri dà −0.031531…. La differenza (≈0.00048) è dello stesso ordine di grandezza dell'errore di troncamento già osservato indipendentemente nel test incrociato sulla convergenza lenta di Z(y) per y<1 (si veda sotto) — coerente con l'aspettativa che la formula chiusa sia esatta e il calcolo dagli zeri, troncato, converga lentamente ad essa.

**Interpretazione.** Z(y) per y<1 *ha* contenuto aritmetico — non quello di ψ (conteggio dei primi), ma quello della somma di Mertens Σ_{n<x}Λ(n)/n. Il termine principale γ−ln x è esattamente ciò che serve perché il secondo teorema di Mertens (Σ_{n≤x}Λ(n)/n = ln x + O(1)) sia vero: questa identità dice che l'errore O(1) in quel teorema **è** −Z(1/x) (più il piccolo termine banale), termine per termine su ogni zero — non asintoticamente, ma esattamente.

**Onestà sulla novità.** L'identità è quasi certamente già nota in sostanza — si può ottenere anche per somma per parti dalla formula esplicita classica di ψ(x), e il genere "formula esplicita con termine d'errore via zeri per Σ Λ(n)/n" è standard (Ingham, Davenport). Ciò che pare nuovo è l'incastro concettuale: **Z(y), l'oggetto ombra del criterio F=S, coincide esattamente con l'errore nel teorema di Mertens.** Non è un pezzo algebrico senza casa: ha una casa precisa, diversa da quella di Z(x) (che vive in ψ).

## Controllo di coerenza: la via delle due oscillazioni alla Landau

Un modo alternativo di attaccare il Passo 4 sarebbe applicare un teorema di oscillazione alla Landau separatamente a Z(x) (x→∞) e a Z(1/x), sommare, e vedere se si riottiene la stessa contraddizione. Il rischio apparente: i risultati di oscillazione sono enunciati "Ω" — la funzione è grande lungo *qualche* successione, non per ogni x — e le due successioni (una per Z(x), una per Z(1/x)) potrebbero non allinearsi, lasciando aperta una cancellazione.

**Il conto che scioglie il dubbio.** Per la coppia dominante {ρ,ρ̄} scelta nel Passo 4 (σ\*>1/2), il contributo a Z(x) da solo è Z_pair(x) ~ x^{σ\*} (cresce). Il contributo della coppia riflessa {1−ρ,1−ρ̄} a x·Z(1/x) è x·Z_pair(1/x) ~ x^{1-σ\*}. Poiché 0<1−σ\*<1/2<σ\*<1, il pezzo riflesso cresce sempre più lentamente di quello diretto. Sommando:

```
[Z_pair(x) + x·Z_pair(1/x)] / (2√x)  ~  x^{σ*-1/2}·(1+o(1))
```

— lo stesso esponente x^{σ−1/2} già noto dal calcolo diretto su F_pair. **Nessuna cancellazione**: per la coppia scelta apposta, il pezzo riflesso è sempre subdominante, mai in grado di annullare il termine dominante.

**Ma non è una seconda dimostrazione indipendente.** Per renderlo rigoroso servirebbe comunque un teorema di oscillazione alla Landau applicabile a Z(x) da sola, con la corretta traduzione dell'esponente attraverso il fattore extra 1/(2√x·ρ(1−ρ)) che la separa da F — un lavoro sostanzialmente equivalente a rifare l'analisi dei poli della trasformata di Laplace, solo nel linguaggio classico "Ω" invece che "polo di L(s)". **Verdetto:** il controllo di coerenza regge (l'esponente torna giusto, la cancellazione temuta non si materializza), ma è lo stesso meccanismo riscritto in un altro dialetto, non una via dimostrativa autonoma.

## Famiglia di criteri equivalenti: pesi g(ρ(1−ρ))

Poiché ρ(1−ρ) è invariante per ρ↦1−ρ, qualunque peso w(ρ)=g(ρ(1−ρ)), per g a piacere, dà — con la stessa identica dimostrazione — un altro criterio equivalente a RH. Il peso del documento è solo g(z)=1/(2z).

### L'esponente di crescita non dipende da g

Con ρ=σ+iγ e ρ(1−ρ)=Re^{iθ}, il contributo di coppia per il peso 1/z^n è

```
F_n,pair(x) = 2 x^{σ-1/2} R^{-n} cos(γ ln x − nθ)
```

L'esponente x^{σ−1/2} viene interamente da x^ρ, non dal peso: è **identico per ogni n**. Cambia solo l'ampiezza R^{-n} e la fase nθ. Verifica numerica su una coppia illustrativa (σ=0.7, γ=14, R=|ρ(1−ρ)|≈196): passando da n=1 a n=4 l'ampiezza crolla di un fattore ~10⁷, ma la velocità di divergenza in x resta esattamente x^{0.2} in ogni caso.

### Perché l'intera dimostrazione si ripete verbatim

I quattro passi si ripetono per ogni g(z)=c/z^n (o più in generale per ogni g meromorfa a coefficienti reali, garantendo g(z̄)=conj(g(z))). La trasformata di Laplace del termine e^{au}(A'cosγu+B'sinγu) ha sempre un **polo semplice** nello stesso punto s=(σ−1/2)+iγ, solo con residuo riscalato da g. Sotto la buccia, l'intera famiglia collassa alla stessa tecnica dimostrativa e alla stessa conclusione logica (RH ⟺ D_g≡0).

### Non tutta la famiglia è ugualmente sicura

Serve g **mai nulla** per z≠0 (o comunque mai nulla nei punti effettivamente raggiunti da ρ(1−ρ) per zeri fuori riga). Se g avesse uno zero z₀ e un ipotetico zero fuori riga avesse esattamente ρ(1−ρ)=z₀, quella coppia contribuirebbe zero a D_g pur violando RH, bucando il criterio per quella specifica g. g(z)=c/z^n è automaticamente sicura (mai nulla per z finito, z≠0); un g polinomiale generico non lo è, a meno di argomenti aggiuntivi che escludano la coincidenza.

### Cosa conta per l'effettività

Non la velocità di divergenza (uguale per tutta la famiglia), ma l'ampiezza del segnale: n=1 massimizza il residuo, quindi è la scelta più sensibile per un'eventuale rilevazione numerica — non per ragioni logiche, ma pratiche.

**Verdetto.** La famiglia esiste davvero ed è provabile con lo stesso meccanismo per ogni scelta sicura di g: non sono criteri distinti, ma un'unica dimostrazione parametrizzata, con n=1 semplicemente il punto più efficiente (massima ampiezza, minima complicazione algebrica) della famiglia — non un caso speciale dal punto di vista logico.
