"""
Dados de exemplo para a API SINAPI.

Em um ambiente de produção, estes dados viriam de um banco de dados
alimentado com as tabelas oficiais do SINAPI/Caixa Econômica Federal.
"""

ESTADOS = [
    {"nome": "Acre", "sigla": "ac", "ibge": 12, "regiao": "norte"},
    {"nome": "Alagoas", "sigla": "al", "ibge": 27, "regiao": "nordeste"},
    {"nome": "Amapá", "sigla": "ap", "ibge": 16, "regiao": "norte"},
    {"nome": "Amazonas", "sigla": "am", "ibge": 13, "regiao": "norte"},
    {"nome": "Bahia", "sigla": "ba", "ibge": 29, "regiao": "nordeste"},
    {"nome": "Ceará", "sigla": "ce", "ibge": 23, "regiao": "nordeste"},
    {"nome": "Distrito Federal", "sigla": "df", "ibge": 53, "regiao": "centro-oeste"},
    {"nome": "Espírito Santo", "sigla": "es", "ibge": 32, "regiao": "sudeste"},
    {"nome": "Goiás", "sigla": "go", "ibge": 52, "regiao": "centro-oeste"},
    {"nome": "Maranhão", "sigla": "ma", "ibge": 21, "regiao": "nordeste"},
    {"nome": "Mato Grosso", "sigla": "mt", "ibge": 51, "regiao": "centro-oeste"},
    {"nome": "Mato Grosso do Sul", "sigla": "ms", "ibge": 50, "regiao": "centro-oeste"},
    {"nome": "Minas Gerais", "sigla": "mg", "ibge": 31, "regiao": "sudeste"},
    {"nome": "Pará", "sigla": "pa", "ibge": 15, "regiao": "norte"},
    {"nome": "Paraíba", "sigla": "pb", "ibge": 25, "regiao": "nordeste"},
    {"nome": "Paraná", "sigla": "pr", "ibge": 41, "regiao": "sul"},
    {"nome": "Pernambuco", "sigla": "pe", "ibge": 26, "regiao": "nordeste"},
    {"nome": "Piauí", "sigla": "pi", "ibge": 22, "regiao": "nordeste"},
    {"nome": "Rio de Janeiro", "sigla": "rj", "ibge": 33, "regiao": "sudeste"},
    {"nome": "Rio Grande do Norte", "sigla": "rn", "ibge": 24, "regiao": "nordeste"},
    {"nome": "Rio Grande do Sul", "sigla": "rs", "ibge": 43, "regiao": "sul"},
    {"nome": "Rondônia", "sigla": "ro", "ibge": 11, "regiao": "norte"},
    {"nome": "Roraima", "sigla": "rr", "ibge": 14, "regiao": "norte"},
    {"nome": "Santa Catarina", "sigla": "sc", "ibge": 42, "regiao": "sul"},
    {"nome": "São Paulo", "sigla": "sp", "ibge": 35, "regiao": "sudeste"},
    {"nome": "Sergipe", "sigla": "se", "ibge": 28, "regiao": "nordeste"},
    {"nome": "Tocantins", "sigla": "to", "ibge": 17, "regiao": "norte"},
]

INSUMOS = [
    {"codigo": 370, "nome": "Areia media - posto jazida/fornecedor (retirada na jazida, sem transporte)", "unidade": "m3", "preco": {"sp": 75.50, "rj": 82.30, "mg": 70.10, "pb": 65.40}, "referencia": "2025-01-01"},
    {"codigo": 1379, "nome": "Cimento Portland composto CP II-32", "unidade": "kg", "preco": {"sp": 0.62, "rj": 0.68, "mg": 0.59, "pb": 0.55}, "referencia": "2025-01-01"},
    {"codigo": 1106, "nome": "Brita 1 - posto pedreira/fornecedor, sem transporte", "unidade": "m3", "preco": {"sp": 89.90, "rj": 95.20, "mg": 85.00, "pb": 78.50}, "referencia": "2025-01-01"},
    {"codigo": 4750, "nome": "Aco CA-50, 10,0 mm, vergalhao", "unidade": "kg", "preco": {"sp": 6.85, "rj": 7.10, "mg": 6.50, "pb": 6.20}, "referencia": "2025-01-01"},
    {"codigo": 4491, "nome": "Aco CA-60, 5,0 mm, vergalhao", "unidade": "kg", "preco": {"sp": 7.20, "rj": 7.45, "mg": 6.90, "pb": 6.55}, "referencia": "2025-01-01"},
    {"codigo": 21127, "nome": "Tijolo ceramico macico *5 x 10 x 20* cm", "unidade": "un", "preco": {"sp": 0.78, "rj": 0.85, "mg": 0.72, "pb": 0.68}, "referencia": "2025-01-01"},
    {"codigo": 10567, "nome": "Tubo PVC, serie normal, esgoto predial, DN 100 mm", "unidade": "m", "preco": {"sp": 18.50, "rj": 19.80, "mg": 17.30, "pb": 16.20}, "referencia": "2025-01-01"},
    {"codigo": 20083, "nome": "Fio de cobre, rigido, classe 1, isolacao em PVC/A, 2,5 mm2", "unidade": "m", "preco": {"sp": 2.45, "rj": 2.60, "mg": 2.30, "pb": 2.15}, "referencia": "2025-01-01"},
    {"codigo": 34794, "nome": "Servente com encargos complementares", "unidade": "h", "preco": {"sp": 18.92, "rj": 19.50, "mg": 17.80, "pb": 16.30}, "referencia": "2025-01-01"},
    {"codigo": 34796, "nome": "Pedreiro com encargos complementares", "unidade": "h", "preco": {"sp": 24.15, "rj": 25.00, "mg": 22.80, "pb": 21.50}, "referencia": "2025-01-01"},
]

COMPOSICOES = [
    {"codigo": 87316, "nome": "Argamassa traço 1:3 (cimento e areia media) para chapisco convencional", "unidade": "m3", "preco": {"sp": 425.80, "rj": 450.20, "mg": 400.50, "pb": 380.10}, "referencia": "2025-01-01"},
    {"codigo": 87365, "nome": "Alvenaria de vedação de blocos cerâmicos furados, e=14 cm", "unidade": "m2", "preco": {"sp": 68.50, "rj": 72.30, "mg": 64.20, "pb": 60.80}, "referencia": "2025-01-01"},
    {"codigo": 92263, "nome": "Lançamento, adensamento e acabamento de concreto em estruturas", "unidade": "m3", "preco": {"sp": 28.45, "rj": 30.10, "mg": 26.80, "pb": 25.20}, "referencia": "2025-01-01"},
    {"codigo": 94964, "nome": "Concreto fck=25 mpa para pilar, FCK = 25MPA", "unidade": "m3", "preco": {"sp": 520.30, "rj": 545.60, "mg": 495.00, "pb": 470.20}, "referencia": "2025-01-01"},
    {"codigo": 96546, "nome": "Pintura látex acrílica premium, duas demãos", "unidade": "m2", "preco": {"sp": 15.80, "rj": 16.90, "mg": 14.70, "pb": 13.90}, "referencia": "2025-01-01"},
    {"codigo": 96114, "nome": "Revestimento cerâmico para piso com placas tipo porcelanato", "unidade": "m2", "preco": {"sp": 98.50, "rj": 103.20, "mg": 93.80, "pb": 88.60}, "referencia": "2025-01-01"},
]

INDICADORES = [
    {"nome": "incc", "valor": 0.44, "referencia": "2025-01-01"},
    {"nome": "incc_acumulado", "valor": 7.52, "referencia": "2025-01-01"},
    {"nome": "ipca", "valor": 0.52, "referencia": "2025-01-01"},
    {"nome": "igpm", "valor": 0.27, "referencia": "2025-01-01"},
    {"nome": "selic", "valor": 13.25, "referencia": "2025-01-01"},
    {"nome": "dolar", "valor": 5.85, "referencia": "2025-01-01"},
]

ENCARGOS = {
    "sp": {"estado": "sp", "horista": 118.73, "mensalista": 84.95, "referencia": "2025-01-01"},
    "rj": {"estado": "rj", "horista": 119.50, "mensalista": 85.30, "referencia": "2025-01-01"},
    "mg": {"estado": "mg", "horista": 117.80, "mensalista": 83.60, "referencia": "2025-01-01"},
    "pb": {"estado": "pb", "horista": 116.90, "mensalista": 82.80, "referencia": "2025-01-01"},
}

HISTORICO_PRECOS = {
    "insumo": {
        370: [
            {"referencia": "2024-07-01", "preco": {"sp": 72.00, "rj": 78.50}},
            {"referencia": "2024-08-01", "preco": {"sp": 72.80, "rj": 79.20}},
            {"referencia": "2024-09-01", "preco": {"sp": 73.10, "rj": 79.80}},
            {"referencia": "2024-10-01", "preco": {"sp": 73.50, "rj": 80.30}},
            {"referencia": "2024-11-01", "preco": {"sp": 74.20, "rj": 81.00}},
            {"referencia": "2024-12-01", "preco": {"sp": 74.90, "rj": 81.70}},
            {"referencia": "2025-01-01", "preco": {"sp": 75.50, "rj": 82.30}},
        ],
        1379: [
            {"referencia": "2024-07-01", "preco": {"sp": 0.58, "rj": 0.64}},
            {"referencia": "2024-08-01", "preco": {"sp": 0.59, "rj": 0.65}},
            {"referencia": "2024-09-01", "preco": {"sp": 0.59, "rj": 0.65}},
            {"referencia": "2024-10-01", "preco": {"sp": 0.60, "rj": 0.66}},
            {"referencia": "2024-11-01", "preco": {"sp": 0.61, "rj": 0.67}},
            {"referencia": "2024-12-01", "preco": {"sp": 0.61, "rj": 0.67}},
            {"referencia": "2025-01-01", "preco": {"sp": 0.62, "rj": 0.68}},
        ],
    },
    "composicao": {
        87316: [
            {"referencia": "2024-07-01", "preco": {"sp": 410.00, "rj": 435.00}},
            {"referencia": "2024-08-01", "preco": {"sp": 413.50, "rj": 438.20}},
            {"referencia": "2024-09-01", "preco": {"sp": 415.20, "rj": 440.50}},
            {"referencia": "2024-10-01", "preco": {"sp": 418.00, "rj": 443.10}},
            {"referencia": "2024-11-01", "preco": {"sp": 420.50, "rj": 445.80}},
            {"referencia": "2024-12-01", "preco": {"sp": 423.00, "rj": 448.00}},
            {"referencia": "2025-01-01", "preco": {"sp": 425.80, "rj": 450.20}},
        ],
    },
}
