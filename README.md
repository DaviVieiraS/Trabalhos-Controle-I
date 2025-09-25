# Control Systems Analysis - Controle I

Trabalhos da disciplina de Controle I - Análise de sistemas de controle e funções de transferência.

## Arquivos

### `Trabalho 0.py`
Script básico que demonstra três tipos de associações de sistemas:
- **Série**: G(s) = G1(s) × G2(s)
- **Paralelo**: G(s) = G1(s) + G2(s)  
- **Realimentação**: G(s) = G1(s) / (1 + G1(s) × G2(s))

### `Trabalho 0.1.py`
Interface gráfica com PyQt5 para análise interativa de funções de transferência.

**Funcionalidades:**
- Interface para entrada de funções de transferência
- Suporte a diferentes notações matemáticas
- Três tipos de conexão (série, paralelo, realimentação)
- Conversão automática de notação (^ para **)

## Como usar

1. Instalar dependências:
```bash
pip install PyQt5 control numpy matplotlib
```

2. Executar a interface gráfica:
```bash
python "Trabalho 0.1.py"
```

## Exemplos de entrada
- `10 / (s^2 + 2*s + 10)`
- `5 / (s^2 + 5)`
- `1 / (s + 1)`

## Autor
**Davi Vieira dos Santos** - Controle I
