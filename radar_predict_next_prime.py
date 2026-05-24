import numpy as np

def predict_next_prime(start_n, beta=1.6366):
    # Cerchiamo nel range immediato
    search_range = np.arange(start_n + 1, start_n + 50)
    
    # Calcolo della Tensione di Erdos per ogni punto
    tensions = []
    for n in search_range:
        # La tensione è massima quando la fase è in risonanza con l'ellissoide
        phase = np.log(n)
        # Cerchiamo il punto in cui la curvatura 'chiama' un nuovo nodo
        tension = np.sqrt(np.sin(phase)**2 + beta * np.cos(phase)**2)
        tensions.append(tension)
    
    # Il candidato è dove la tensione subisce una variazione brusca (gradiente)
    gradients = np.gradient(tensions)
    candidate = search_range[np.argmax(np.abs(gradients))]
    
    return candidate

# Esempio: Cerchiamo il prossimo primo dopo 333
prossimo_candidato = predict_next_prime(333)
print(f"Il radar di Erdos punta verso: {prossimo_candidato}")
