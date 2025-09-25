# Control Systems Analysis - Trabalhos Controle I

Este repositório contém trabalhos e projetos relacionados à disciplina de Controle I, focados na análise de sistemas de controle e funções de transferência.

## 📁 Estrutura do Projeto

### `Trabalho 0.py`
Script básico em Python que demonstra diferentes tipos de associações de sistemas de controle:

- **Sistema em Cascata (Série)**: `G_resultado(s) = G1(s) × G2(s)`
- **Sistema em Paralelo**: `G_resultado(s) = G1(s) + G2(s)`
- **Sistema com Realimentação**: `G_resultado(s) = G1(s) / (1 + G1(s) × G2(s))`

**Funções de Transferência de Exemplo:**
- G₁(s) = 10 / (s² + 2s + 10)
- G₂(s) = 5 / (s² + 5)

### `Trabalho 0.1.py`
Interface gráfica completa desenvolvida com PyQt5 para análise interativa de funções de transferência:

#### 🎯 Funcionalidades
- **Interface Intuitiva**: Interface moderna e profissional para entrada de funções de transferência
- **Múltiplos Formatos de Entrada**: Suporte para diferentes notações matemáticas
- **Três Tipos de Conexão**:
  - Série (Cascata)
  - Paralelo
  - Realimentação (Malha Fechada)
- **Processamento Inteligente**: Conversão automática de notação matemática (^ para **, etc.)
- **Resultados Limpos**: Exibição clara e organizada dos resultados

#### 🛠️ Tecnologias Utilizadas
- **Python 3.x**
- **PyQt5**: Interface gráfica
- **Control Library**: Processamento de funções de transferência
- **NumPy**: Cálculos numéricos
- **Matplotlib**: Visualização (preparado para futuras implementações)

#### 📋 Dependências
```bash
pip install PyQt5 control numpy matplotlib
```

#### 🚀 Como Executar
```bash
python "Trabalho 0.1.py"
```

## 🎓 Conceitos de Controle Abordados

### Funções de Transferência
As funções de transferência são representações matemáticas que descrevem a relação entrada-saída de sistemas lineares invariantes no tempo (LTI).

### Tipos de Associação

1. **Cascata (Série)**
   - Saída do primeiro sistema é entrada do segundo
   - Multiplicação das funções de transferência

2. **Paralelo**
   - Entrada comum, saídas somadas
   - Soma das funções de transferência

3. **Realimentação (Malha Fechada)**
   - Saída realimentada para a entrada
   - Fórmula clássica de malha fechada

## 📊 Exemplos de Uso

### Entrada de Funções
A interface aceita diferentes formatos:
- `10 / (s^2 + 2*s + 10)`
- `5 / (s^2 + 5)`
- `1 / (s + 1)`
- `s / (s^2 + 3*s + 2)`

### Resultados
O sistema calcula e exibe a função de transferência resultante para cada tipo de associação, mostrando:
- Fórmula utilizada
- Tipo de conexão
- Função de transferência final simplificada

## 🔧 Desenvolvimento

### Estrutura do Código
- **Interface Principal**: Classe `InterfaceControle` com PyQt5
- **Processamento**: Método `processar_expressao()` para conversão de notação
- **Cálculos**: Integração com a biblioteca `control` do Python
- **Interface**: Design responsivo e profissional

### Melhorias Futuras
- [ ] Gráficos de resposta temporal
- [ ] Análise de estabilidade
- [ ] Diagramas de Bode
- [ ] Exportação de resultados
- [ ] Histórico de cálculos

## 📚 Referências
- Ogata, K. - "Engenharia de Controle Moderno"
- Nise, N.S. - "Sistemas de Controle para Engenharia"
- Python Control Systems Library Documentation

## 👨‍💻 Autor
**Davi Vieira Silva**
- Disciplina: Controle I
- Repositório: [Trabalhos-Controle-I](https://github.com/DaviVieiraS/Trabalhos-Controle-I)

---

*Este projeto faz parte dos trabalhos da disciplina de Controle I, demonstrando conceitos fundamentais de sistemas de controle através de implementações práticas em Python.*
