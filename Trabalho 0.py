import control

# Definindo as funções de transferência
# G1(s) = 10 / (s^2 + 2s + 10)
# G2(s) = 5 / (s^2 + 5)

# Criando as funções de transferência
s = control.TransferFunction.s
G1 = 10 / (s**2 + 2*s + 10)
G2 = 5 / (s**2 + 5)

# 1. Sistema em cascata (série)
G_cascata = control.series(G1, G2)

# 2. Sistema em paralelo
G_paralelo = control.parallel(G1, G2)

# 3. Sistema com realimentação (malha fechada)
G_feedback = control.feedback(G1, G2)

# Resultados finais
print("1. SISTEMA EM CASCATA:")
print(G_cascata)
print()

print("2. SISTEMA EM PARALELO:")
print(G_paralelo)
print()

print("3. SISTEMA COM REALIMENTACAO:")
print(G_feedback)