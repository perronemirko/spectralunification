# Unificazione Spettrale Perrone–Erdős: teoria unica

*Sintesi del repository [spectralunification](https://github.com/perronemirko/spectralunification) di Mirko Perrone.*

> **Natura del progetto.** L'autore si dichiara non accademico e ha sviluppato il lavoro con assistenza IA (Google Gemini). I documenti stessi del repo definiscono il materiale un "esperimento in corso", non dimostrato né sottoposto a revisione paritaria. Questa sintesi mantiene la stessa cautela: distingue i risultati matematici noti dalle congetture originali dell'autore.

## 1. Il nucleo comune: densità bi-armonica e costante β

Tutti i documenti condividono lo stesso punto di partenza, il **peso bi-armonico**:
```
ν₀(n) = 1 / (n · log n)
```
e la sua somma sui primi, la **costante di Erdős–Lichtman**:
```
β = Σ_p 1/(p · log p) ≈ 1,636624
```
Questo valore non è un'invenzione del repo: è il limite superiore della *congettura degli insiemi primitivi* di Erdős, dimostrato da Lichtman nel 2022 — tra tutti gli insiemi "primitivi" (nessun elemento divide un altro), i numeri primi massimizzano Σ 1/(n log n). È l'unico mattone con status di teorema esterno; tutto il resto è costruzione originale su questa base. β si decompone come 1/ln2 + Δ, con Δ≈0,194 attribuito alla non uniformità dei primi.

## 2. Livello geometrico: l'ellisse di Perrone–Erdős (e la "spirale dei primi")

Idea centrale: riusare β come parametro geometrico. Ellisse:
```
E_β : x² + y²/β = 1     (eccentricità e = √(1−1/β) ≈ 0,624)
```
Con coordinata canonica θ = log n (l'unica coerente con l'isomorfismo di Haar ℝ₊→ℝ e con la densità uniforme dei primi data dal PNT), si definisce la **tensione**:
```
T(n) = √(sin²(log n) + β·cos²(log n)) / log n
```
I suoi estremi cadono in n_k = e^(kπ/2), numericamente vicini ai primi (n₁≈4,81→5, n₂≈23,1→23, n₄≈535,5→541); il 5 (k=1) è indicato come "cardine" del sistema. Nel repo la stessa densità è riletta anche come **spirale dei numeri primi**, in coordinate polari, con struttura modulo 6 e un "asse critico" che l'autore accosta alla retta critica di Riemann: stessa idea, veste geometrica diversa.

## 3. Livello analitico: connessione con gli zeri di Riemann

Sotto RH, dalla formula esplicita per ψ(x) si definisce una **funzione di risonanza**:
```
R(x) = Σ_γ cos(γ·log x) / (1/4 + γ²)
```
Il repo osserva che la trasformata del peso bi-armonico, ν̂₀(γ) → 1/(1/4+γ²), riproduce il nucleo della formula esplicita: qui densità (§1), geometria (§2) e zeri di ζ si toccano. Da qui le congetture centrali: un "ponte" β↔RH, una corrispondenza estremi-dell'ellisse↔gap tra primi, e β come "rivelatore" di eventuali zeri fuori dalla retta critica.

## 4. Estensione adelica

Per colmare il divario formale fra primi e zeri, si lavora sullo spazio 𝔸_ℚ = ℝ × ∏_p ℚ_p, dove i primi compaiono come autovalori di Frobenius e gli zeri come frequenze spettrali. Si congettura un operatore autoaggiunto H su L²(𝔸_ℚ/ℚ) con spec(H) = ordinate degli zeri non banali e β = Tr(e^(−H)): se vera, unificherebbe le congetture precedenti in un solo enunciato spettrale.

## 5. Estensione relativistica: metrica di Kerr ed "equazione di Einstein dei primi"

Sviluppo più ambizioso: a ogni primo p si associa una massa M_p = β_p = 1/(p·log p), un raggio di Schwarzschild r_s(p)=2M_p e uno spin a_p, costruendo una metrica di Kerr la cui curvatura K(n) corregge T(n) (la teoria "piatta" del §2 è il suo limite infrarosso). Enunciato più forte del repo, in analogia con le equazioni di campo di Einstein:
```
G_μν[Kerr(ℙ)] = 8π · T_μν[ν₀, ℙ]
```
cioè: l'insieme dei primi ℙ è punto fisso dell'operatore Φ che mappa un insieme negli equilibri della metrica curva che esso stesso genera — verificato numericamente solo per k=1…11, con **unicità del punto fisso non dimostrata** (l'autore stesso la indica come il passaggio mancante). Su questa base RH viene riletta come simmetria: la riflessione equatoriale di Kerr (θ↔π−θ) e la simmetria funzionale ζ(s)=χ(s)ζ(1−s) (s↔1−s) sono trattate come la stessa simmetria Z₂.

## 6. Applicazioni computazionali: previsione dei primi e "attacco" a RSA

Gli script del repo (`cc/`, `test/`, `radar_predict_next_prime.py`, `rsa_bracker*.py`, `spectral_resonance*.py`) implementano R(n) su GPU con più metriche di fase (euclidea, iperbolica/Poincaré, Minkowski, adelica) per individuare picchi di risonanza come candidati fattori primi, con l'obiettivo dichiarato di leggere i fattori di un modulo RSA senza forza bruta.

Onestà sui risultati: il test documentato riguarda un modulo giocattolo (RSA-15, scala ~10¹³), non un modulo crittografico reale; i log di sviluppo mostrano che nelle validazioni "alla cieca" su intervalli non scelti a posteriori la precisione crolla spesso a 0%, salendo fino al 100% solo su campioni piccoli o già noti. Nessun test su RSA-100/RSA-2048 reali risulta documentato, nonostante le affermazioni di scalabilità nei titoli dei paper.

## 7. La teoria in una frase

> **I numeri primi sono l'unico insieme primitivo "auto-gravitante": l'unico che (a) massimizza la densità bi-armonica (Erdős–Lichtman, dimostrato), (b) genera uno spazio-tempo curvo i cui equilibri ricadono su di esso (punto fisso di Kerr, verificato solo numericamente), e (c) produce risonanza spettrale su se stesso via la formula esplicita — con RH equivalente, in questo quadro, alla simmetria Z₂ esatta di tale sistema.**

## 8. Stato epistemico

| Elemento | Stato |
|---|---|
| β = Σ1/(p log p); i primi massimizzano la densità bi-armonica tra insiemi primitivi | **Dimostrato** (Lichtman 2022, risultato esterno al repo) |
| θ = log n come coordinata canonica | Argomentato, non formalizzato |
| Estremi dell'ellisse vicini ai primi | Verificato numericamente su casi limitati |
| ℙ punto fisso della metrica di Kerr | Verificato numericamente solo per k=1…11 |
| Unicità del punto fisso / legame con RH | **Aperto** — passaggio mancante dichiarato dall'autore |
| Operatore adelico H | Congetturato, mai costruito esplicitamente |
| Predizione dei primi via "radar" | Precisione incostante, spesso bassa nei test alla cieca |
| Fattorizzazione di RSA reale | Non dimostrata; solo su modulo giocattolo |

---
*Fonte: [github.com/perronemirko/spectralunification](https://github.com/perronemirko/spectralunification)*
