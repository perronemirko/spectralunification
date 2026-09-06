# Teorema del Perrone

_Nome di lavoro per un risultato emerso dalla revisione critica della "Unificazione Spettrale Perrone–Erdős" di Mirko Perrone: nasce dal suo tentativo di costruire un rivelatore spettrale per l'ipotesi di Riemann, ma si dimostra indipendentemente da ogni altra parte di quella teoria._

## Enunciato, a parole

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
