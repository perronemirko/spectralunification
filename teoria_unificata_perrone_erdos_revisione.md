# Unificazione Spettrale Perrone–Erdős: sintesi riveduta

> **Natura del progetto originale.** L'autore si dichiara non accademico e ha sviluppato il lavoro con assistenza IA (Google Gemini). I documenti del repo definiscono il materiale un "esperimento in corso", non dimostrato né sottoposto a revisione paritaria.

_Aggiornamento della sintesi del repository [spectralunification](https://github.com/perronemirko/spectralunification) di Mirko Perrone, dopo una revisione matematica riga per riga: ogni formula è stata ricontrollata algebricamente e, dove possibile, verificata con calcolo numerico diretto. La revisione ha trovato e corretto un errore algebrico in una formula chiave (§3), ha falsificato numericamente un'identità (§4), e ha portato una congettura del §3 fino a teorema dimostrato per intero. Questa nota non è una pubblicazione sottoposta a referaggio: resta soggetta alla stessa cautela del documento originale, distinguendo risultati esterni dimostrati, risultati dimostrati in questa revisione, e congetture ancora aperte._

## 0. Cosa è cambiato rispetto alla prima sintesi

| Intervento | Sezione |
|---|---|
| Confermato con somma diretta dei primi | §1 |
| Corretta un'imprecisione concettuale ("densità uniforme") | §2 |
| Eseguito un test statistico mai fatto prima (verdetto: nullo) | §2 |
| Trovato e corretto un errore algebrico nella formula del rivelatore | §3 |
| Elevata una congettura a teorema, con dimostrazione completa | §3 |
| Falsificata numericamente un'identità (scarto di ~6 ordini di grandezza) | §4 |
| Nessun cambiamento: restano slogan / programmi aperti | §5 |
| Nessun cambiamento: obiezione strutturale confermata | §6 |

## 1. Il nucleo comune: densità bi-armonica e costante β

Tutti i filoni della teoria condividono lo stesso punto di partenza, il **peso bi-armonico**:

```
ν₀(n) = 1 / (n · log n)
```

e la sua somma sui primi, la **costante di Erdős–Lichtman**:

```
β = Σ_p 1/(p · log p) ≈ 1,636624
```

Questo valore non è un'invenzione: è il limite superiore della _congettura degli insiemi primitivi_ di Erdős, dimostrato da Lichtman nel 2022 — tra tutti gli insiemi "primitivi" (nessun elemento divide un altro), i numeri primi massimizzano Σ1/(n log n). È l'unico mattone con status di teorema esterno; tutto il resto è costruzione originale su questa base.

**Verifica diretta (nuova).** La somma dei primi sotto 5·10⁶ vale 1,57179; sommando una stima grezza della coda (1/log N) si arriva a 1,63662 — in accordo con il valore citato fino alla quinta cifra. I primi 15 numeri primi (fino a 47) valgono da soli l'84,8% di β; il solo 2 ne vale il 44%.

### La decomposizione β = 1/log2 + Δ: da dove viene, e dove non porta

Per sommazione di Abel vale l'identità esatta

```
β = ∫₂^∞ π(t) · (log t + 1) / (t² (log t)²) dt
```

Il modello più semplice — densità euristica dπ ≈ dt/log t — dà, per sostituzione u=log t,

```
∫₂^∞ dt/(t·log²t) = 1/log 2 = 1,442695...
```

esatto. Δ := β − 1/log2 = 0,19393, in accordo con il valore citato (≈0,194).

**Un tentativo naturale non funziona.** Ci si aspetterebbe che sostituendo nell'identità esatta un modello *migliore* di π(t) — per esempio li(t), la miglior approssimazione nota — lo scarto Δ si riduca, isolando una parte residua legata alla regione priva di zeri. Verificato numericamente, succede il contrario:

| modello per π(t) nell'identità esatta | valore |
|---|---|
| densità 1/log t (il più semplice) | **1,442695** |
| t/log t | 2,48338 |
| li(t) — la miglior approssimazione nota | 2,19662 |
| β (vero) | 1,636624 |

Il modello "migliore" (li(t)) peggiora, e di molto. Il motivo: il nucleo (log t+1)/(t²log²t) pesa quasi tutto sui t piccoli, dove li(t) sovrastima sistematicamente π(t) fin dall'inizio (li(10)=6,17 contro π(10)=4; li(100)=30,13 contro π(100)=25). Δ, nel suo insieme, non è un oggetto asintotico legato agli zeri di ζ — è dominato da aritmetica di primi piccoli, dove nessuna regione priva di zeri serve.

**Piano corretto:** fissare una soglia esplicita M, sommare a mano i primi ≤M, e applicare la regione priva di zeri solo alla coda Σ_{p>M}, dove π(t)−li(t) è davvero piccolo. Quella coda, non l'identità intera, è il vero (piccolo) ponte verso gli zeri.

## 2. Livello geometrico: l'ellisse di Perrone–Erdős

Idea centrale: riusare β come parametro geometrico. Ellisse:

```
E_β : x² + y²/β = 1     (eccentricità e = √(1−1/β) ≈ 0,6237)
```

Con coordinata canonica θ = log n, si definisce la **tensione**:

```
T(n) = √(sin²(log n) + β·cos²(log n)) / log n
```

I suoi estremi cadono in n_k = e^(kπ/2): un fatto trigonometrico elementare (g(θ)=sin²θ+βcos²θ ha derivata (1−β)sin(2θ), zero a θ=kπ/2), senza alcun contenuto sui primi a priori.

**Correzione.** Il documento originale descrive θ=log n come coerente con "la densità uniforme dei primi data dal PNT". È impreciso: se N(u):=π(e^u), il PNT dà N(u)~e^u/u, che *cresce* in u — i primi diventano sempre più fitti nella scala logaritmica, non uniformemente distribuiti. Il fatto vero è più debole ma sufficiente: θ=log n resta l'unica coordinata invariante per dilatazione (misura di Haar su ℝ₊).

**Test statistico eseguito (mai fatto prima).** Distanza dal primo più vicino confrontata con l'attesa sotto un modello di Cramér (primi come processo di Poisson di intensità 1/log t, che dà attesa log(n_k)/2):

| k | n_k (≈) | primo vicino | dist/attesa |
|---|---|---|---|
| 1 | 4,8 | 5 | 0,24 |
| 2 | 23,1 | 23 | 0,09 |
| 3 | 111,3 | 113 | 0,71 |
| 4 | 535,5 | 541 | 1,75 |
| 5 | 2576,0 | 2579 | 0,77 |
| 6 | 12391,6 | 12391 | 0,14 |
| 7 | 59609,7 | 59611 | 0,23 |
| 8 | 286751,3 | 286751 | 0,05 |
| 9 | 1379410,7 | 1379423 | 1,74 |
| 10 | 6635624,0 | 6635621 | 0,38 |

Media dei rapporti: 0,61. Sotto il modello nullo, dist/attesa segue un'esponenziale di media 1 e mediana log2≈0,69 — più della metà dei punti casuali cade *comunque* sotto la media, per pura forma della distribuzione. Con 10 punti l'errore standard è ≈0,32: 0,61 dista meno di 1,3 deviazioni standard da 1. **Verdetto: nessuna deviazione dal caso puro**, con i dati disponibili.

## 3. Livello analitico: dal nucleo di Lorentz a un teorema dimostrato

Sotto RH, dalla formula esplicita per ψ₀(x) si definisce una **funzione di risonanza**:

```
S(x) = Σ_{γ>0} cos(γ·log x) / (1/4 + γ²)
```

(γ indica le ordinate degli zeri non banali; la somma è ben definita **incondizionatamente**, senza bisogno di RH, perché dipende solo dalle ordinate, non dalla parte reale degli zeri).

**Un'affermazione era falsa.** Il documento originale sosteneva che la trasformata del peso bi-armonico, ν̂₀(γ), riproducesse questo nucleo. Calcolato esplicitamente, ν̂₀(γ) = ∫₂^∞ e^{iγ log t} dt/(t·log t) decade come 1/γ, oscillando (si esprime con gli integrali seno e coseno integrale) — non è il nucleo lorentziano.

**Il fatto vero è più semplice e altrove.** Per h(u):=e^{-|u|/2}:

```
ĥ(t) = ∫ e^{-itu} e^{-|u|/2} du = 1/(1/4 + t²)
```

identità elementare (verificata anche numericamente: a t=3, valore numerico e formula coincidono a 10 cifre). Il nucleo lorentziano nasce dallo smoothing esponenziale in scala logaritmica, non dal peso ν₀.

### Il rivelatore F(x): un errore trovato e corretto

Un tentativo di scrivere S(x) come somma sugli zeri — utile per collegarla a RH senza assumerla — proponeva

```
F(x) = Σ_ρ  x^ρ / (2√x · ρ(1−ρ̄))          ← ERRATO
```

Controllato sul primo zero vero, γ₁=14,134725, con ρ=1/2+iγ₁: ρ(1−ρ̄) = −199,54+14,13i — **complesso**, non 1/4+γ₁² come richiesto. La quantità reale giusta è ρ(1−ρ):

```
F(x) := Σ_ρ  x^ρ / (2√x · ρ(1−ρ))          ← corretto
```

Verificato: ρ(1−ρ)=200,04+0i = 1/4+γ₁² esatto. In generale, scrivendo ρ=σ+iγ (σ per Re(ρ) — da non confondere con la costante β):

```
ρ(1−ρ) = [σ(1−σ)+γ²] + iγ(1−2σ)
```

reale se e solo se σ=1/2 — confermato numericamente anche fuori dalla retta critica (σ=0,6 di prova: parte immaginaria −2,827, e γ(1−2σ)=14,135·(−0,2)=−2,827, coincide).

F(x) converge assolutamente e incondizionatamente (|ρ(1−ρ)|~γ² per γ grande, insieme al conteggio N(T)=O(T log T) degli zeri). Sotto RH, accoppiando ogni zero con il coniugato, F(x) riproduce S(x) termine per termine.

### Teorema (dimostrato per intero in questa revisione)

```
RH  ⟺  F(x) = S(x)   per ogni x>0
```

**⟹.** Sotto RH, ρ=1/2+iγ e ρ̄=1/2−iγ danno insieme x^{iγ}/(2(1/4+γ²)) + x^{-iγ}/(2(1/4+γ²)) = cos(γ·log x)/(1/4+γ²): esattamente il termine di S(x).

**⟸.** Sia D(x):=F(x)−S(x). Le coppie sulla retta critica danno D_pair≡0 (calcolo sopra); solo le coppie fuori dalla retta contribuiscono, col termine

```
D_pair(u) = e^{(σ-1/2)u}·[A cos(γu)+B sin(γu)] / (A²+B²),   u=log x
A = σ(1-σ)+γ²,   B = γ(1-2σ)
```

Se RH è falsa, per riflessione (ρ zero ⟹ ρ̄, 1−ρ, 1−ρ̄ zeri) esiste una coppia con σ*>1/2, γ*>0. Argomento:

1. *Crescita innocua, incondizionata.* Poiché 0<σ<1 per ogni zero non banale (fatto classico), D(e^u)=O(e^{u/2}) sempre, comunque stiano le cose su RH. Dunque L(s):=∫₀^∞D(e^u)e^{-su}du è olomorfa per Re(s)>1/2, **indipendentemente da RH**.

2. *Trasformata termine a termine.* Con a:=σ−1/2, la trasformata di Laplace di e^{au}(A cosγu+B sinγu) è [A(s−a)+Bγ]/[(A²+B²)((s−a)²+γ²)], con poli semplici in s=(σ−1/2)±iγ. Per Re(s)>1/2, L(s)=M(s):=Σ (di queste funzioni razionali sulle coppie fuori linea); l'interscambio somma/integrale è giustificato da convergenza assoluta.

3. *M è meromorfa su tutto ℂ.* Poiché σ(1−σ)≤1/4 e |1−2σ|≤1 per ogni σ∈(0,1) — uniformemente, non solo vicino a σ=1/2 — ogni termine è O(1/γ⁴) uniformemente in σ. Con N(T)=O(TlogT), la serie converge assolutamente lontano dai poli su tutto ℂ: M è meromorfa ovunque, con poli esattamente in (σⱼ−1/2)±iγⱼ per ogni coppia fuori linea, ciascuno con residuo non nullo.

4. *Contraddizione.* Sia s₀:=(σ*−1/2)+iγ*, con Re(s₀)>0 proprio perché σ*>1/2. Se D fosse limitata, L si estenderebbe olomorfa a tutto Re(s)>0 (fatto elementare della trasformata di Laplace di una funzione limitata) — ma L=M su Re(s)>1/2, e per unicità della continuazione analitica l'estensione di L è M, che ha un polo in s₀. Contraddizione.

Dunque D non è limitata: F≢S. ∎

*(Il meccanismo — trasformata di Laplace di e^{au}(A cos γu+B sin γu) — è stato verificato anche numericamente su una coppia fittizia fuori dalla retta critica, non uno zero vero, solo per controllare la formula: coincide con la forma chiusa a precisione arbitraria una volta che l'integrazione tiene conto della lentezza del decadimento vicino al bordo di convergenza — la stessa cautela numerica del §1. La tecnica è un adattamento diretto dei classici teoremi di oscillazione di tipo Landau, di norma applicati a ψ(x)−x, qui applicati direttamente a F e S.)*

Questo teorema non ha più bisogno di β, dell'ellisse, o di Kerr per reggersi: nasce da R(x) ma si dimostra da solo.

## 4. Estensione adelica

Per colmare il divario formale fra primi e zeri, si lavora sullo spazio 𝔸*ℚ = ℝ × ∏_p ℚ_p, dove i primi compaiono come autovalori di Frobenius e gli zeri come frequenze spettrali. Si congettura un operatore autoaggiunto H su L²(𝔸*ℚ/ℚ) con spec(H) = ordinate degli zeri non banali e β = Tr(e^(−H)).

**Obiezione formale.** "L²(𝔸*ℚ/ℚ)" non è uno spazio definito — manca il quoziente preciso (gruppo delle classi di idele 𝔸_ℚ^×/ℚ^×? con quale misura?) e il dominio di H.

**Obiezione numerica — decisiva.** Se spec(H)={γₙ}:

```
γ₁=14,134725  γ₂=21,022040  γ₃=25,010858  γ₄=30,424876  γ₅=32,935062  ...
Tr(e^{-H}) ≈ 2·Σ e^{-γₙ} ≈ 1,455·10⁻⁶
β / Tr(e^{-H}) ≈ 1,12·10⁶
```

Poco più di sei ordini di grandezza di differenza. Includere gli zeri banali (s=−2,−4,...) peggiorerebbe le cose nell'altra direzione (e²≈7,39 già supera β da solo). L'equazione è falsa prima ancora di costruire H.

Il primo traguardo verificabile per qualunque H candidato, prima di pretendere lo spettro esatto, resta la legge di conteggio N(T)~(T/2π)·log(T/2π) (formula di Riemann–von Mangoldt).

## 5. Estensione relativistica: metrica di Kerr ed "equazione di Einstein dei primi"

A ogni primo p si associa una massa M_p=β_p=1/(p·log p), un raggio di Schwarzschild r_s(p)=2M_p e uno spin a_p, con

```
G_μν[Kerr(ℙ)] = 8π · T_μν[ν₀, ℙ]
```

verificato numericamente solo per k=1…11, con unicità del punto fisso non dimostrata. RH viene riletta come simmetria: riflessione equatoriale di Kerr (θ↔π−θ) ↔ simmetria funzionale ζ(s)=χ(s)ζ(1−s) (s↔1−s), trattate come la stessa Z₂.

**Le due involuzioni sono autentiche ma separate.** χ(s) ha modulo 1 sulla retta critica — da qui gli zeri si specchiano — ma porta una fase non banale; l'involuzione di Kerr è una simmetria geometrica dello spazio-tempo. Dichiararle "la stessa Z₂" richiede una mappa equivariante esplicita fra i due spazi, che manca del tutto nel documento.

**Cosa manca ancora prima della mappa.** Qualunque candidato G_μν=8πT_μν deve superare, come controllo minimo, ∇^μT_μν=0 (conseguenza dell'identità di Bianchi). Servono inoltre: la varietà e la sua segnatura, la costruzione esplicita di T_μν a partire da ν₀, l'origine di a_p. "k=1…11" non supera (e non affronta) questo controllo, perché nessun tensore è ancora stato scritto.

## 6. Applicazioni computazionali: previsione dei primi e "attacco" a RSA

Gli script del repo implementano R(x) su GPU con più metriche di fase (euclidea, iperbolica/Poincaré, Minkowski, adelica) per individuare picchi di risonanza come candidati fattori primi. Il test documentato riguarda un modulo giocattolo (RSA-15, scala ~10¹³); le validazioni "alla cieca" su intervalli non scelti a posteriori mostrano precisione che crolla spesso a 0%, salendo fino al 100% solo su campioni piccoli o già noti. Nessun test su RSA-100/RSA-2048 reali risulta documentato.

**Obiezione strutturale, non di implementazione.** R(x) e F(x) dipendono solo da x: sono la stessa funzione per RSA-15 e per un modulo crittografico reale. Nessuna somma sugli zeri di ζ, da sola, può portare l'informazione "p divide questo N particolare" — servirebbe un osservabile esplicito g(x,N), sensibile alla divisibilità (per esempio via gcd(·,N) o caratteri modulo N), che non compare in nessuna versione della teoria. Lo 0% di precisione nei test alla cieca è esattamente ciò che questa struttura predice, non un difetto correggibile con più potenza di calcolo.

## 7. La teoria, oggi

**Ciò che è dimostrato, e si regge da solo:**

> Esiste una funzione esplicita F(x), costruita a partire dagli zeri di ζ e dal nucleo lorentziano, tale che F coincide con la sua "ombra sulla retta" S(x) per ogni x se e solo se l'ipotesi di Riemann è vera. È un teorema — con dimostrazione completa — non una congettura, e non dipende da β, dall'ellisse, né da Kerr.

**Ciò che resta la visione originale, non ancora matematica:**

> I numeri primi sarebbero l'unico insieme primitivo "auto-gravitante": l'unico che massimizza la densità bi-armonica (dimostrato, Erdős–Lichtman), genera uno spazio-tempo curvo i cui equilibri ricadono su di esso (slogan, nessun tensore scritto), e produce risonanza spettrale su se stesso (vero, ma solo nella forma corretta del §3 — non in quella con cui la teoria è partita).

## 8. Stato epistemico (aggiornato)

| Elemento | Stato |
|---|---|
| β = Σ1/(p log p); i primi massimizzano la densità bi-armonica | **Dimostrato** (Lichtman 2022) — confermato anche per somma diretta |
| θ = log n coordinata canonica | Corretto (misura di Haar); "densità uniforme" era impreciso — dπ/du ~ eᵘ/u cresce |
| β = 1/log2 + Δ | Δ ≈ 0,194 confermato; dominato da aritmetica dei primi piccoli, non da un termine legato agli zeri |
| Estremi dell'ellisse vicini ai primi | Testato su k=1…10: nessuna deviazione dal caso puro (modello di Cramér) |
| ν̂₀(γ) = 1/(1/4+γ²) | **Falso** come formula letterale; il nucleo nasce dalla trasformata di e^(−\|u\|/2) |
| F(x)=Σ xᵖ/(2√x·ρ(1−ρ̄)) | **Errore algebrico** — non reale sulla retta critica, verificato numericamente |
| F(x)=Σ xᵖ/(2√x·ρ(1−ρ)) ⟺ RH | **Dimostrato per intero** in questa revisione (§3) |
| β = Tr(e^{-H}), spec(H) = ordinate degli zeri | **Falso**, scarto di ~6 ordini di grandezza (confermato numericamente) |
| Operatore adelico H | Spazio non definito; nessuna costruzione esplicita |
| ℙ punto fisso della metrica di Kerr | Nessun tensore scritto; nessun controllo di consistenza (∇^μT_μν=0) tentato |
| Simmetria Z₂ comune (χ(s) ↔ riflessione di Kerr) | Due involuzioni autentiche, nessuna mappa equivariante |
| Fattorizzazione di RSA reale | **Impossibile per struttura**: R(x) e F(x) non dipendono da N |

## 9. Programma di lavoro

1. **β:** separare i primi ≤M (calcolo diretto) dalla coda Σ_{p>M}; applicare la regione priva di zeri solo lì, dove π(t)−li(t) è davvero piccolo.
2. **Ellisse:** verdetto nullo confermato; estendibile con un test di Kolmogorov–Smirnov se si vuole insistere — previsione invariata.
3. **Rivelatore F−S:** il teorema del §3 è il risultato solido di questa revisione. Resta aperto se, applicato a intervalli finiti di x, dia stime *effettive* (non solo un teorema di esistenza) sulla posizione di un eventuale zero fuori dalla retta.
4. **Adelico:** costruire H dentro un quadro già esistente (Berry–Keating, Connes), non accanto ad esso; primo traguardo verificabile = legge di Weyl per N(T).
5. **Kerr:** sospeso finché non ci sono tensori espliciti da sottoporre al controllo ∇^μT_μν=0.
6. **RSA:** ritirato per ragione strutturale — non riformulabile senza un osservabile N-dipendente esplicito.

---

_Fonte originale: [github.com/perronemirko/spectralunification](https://github.com/perronemirko/spectralunification). Questa revisione è emersa da un dialogo di verifica matematica, con controllo numerico diretto di ogni formula qui riportata._
