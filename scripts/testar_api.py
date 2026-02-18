#!/usr/bin/env python3
"""Script de teste completo da API SINAPI.

Inicia o servidor com dados de amostra e testa todos os endpoints,
mostrando os resultados de forma clara no terminal.

Uso:
    python scripts/testar_api.py
"""

import io
import json
import os
import sys
import time

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import uvicorn

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

BASE_URL = "http://127.0.0.1:8777"
API_KEY = "teste-local"


def colored(text: str, color: str) -> str:
    """Aplica cor ANSI ao texto."""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def print_header(title: str):
    print(f"\n{colored('=' * 60, 'cyan')}")
    print(f"{colored(f'  {title}', 'bold')}")
    print(f"{colored('=' * 60, 'cyan')}")


def print_result(name: str, passed: bool, detail: str = ""):
    icon = colored("✓", "green") if passed else colored("✗", "red")
    status = colored("OK", "green") if passed else colored("FALHOU", "red")
    print(f"  {icon} {name}: {status}")
    if detail and not passed:
        print(f"    {colored(detail, 'yellow')}")


def pretty_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_upload(client: httpx.Client) -> bool:
    """Testa upload de dados SINAPI."""
    from tests.sample_data import create_sample_sinapi_xlsx

    xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")

    resp = client.post(
        f"{BASE_URL}/upload",
        params={"estado": "SP", "referencia": "2026-01"},
        files={"file": ("sinapi_sp.xlsx", xlsx.getvalue(), "application/octet-stream")},
    )

    if resp.status_code != 200:
        return False

    data = resp.json()
    print(f"    Carregados: {data.get('insumos', 0)} insumos, "
          f"{data.get('composicoes', 0)} composições, "
          f"{data.get('analitico', 0)} analíticos")
    return data.get("insumos", 0) > 0


def test_auth_sem_chave(client: httpx.Client) -> bool:
    """Testa que requisição sem API key é rejeitada."""
    resp = client.get(f"{BASE_URL}/estados")
    return resp.status_code == 401


def test_auth_chave_invalida(client: httpx.Client) -> bool:
    """Testa que API key inválida é rejeitada."""
    resp = client.get(
        f"{BASE_URL}/estados",
        headers={"X-API-Key": "chave-errada"},
    )
    return resp.status_code == 401


def test_insumos_busca(client: httpx.Client) -> bool:
    """Testa busca de insumos por nome."""
    resp = client.get(
        f"{BASE_URL}/insumos",
        params={"nome": "cimento", "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    print(f"    Encontrados: {data.get('total', 0)} insumos")
    if data.get("data"):
        item = data["data"][0]
        print(f"    Exemplo: {item.get('codigo')} - {item.get('descricao')} "
              f"= R$ {item.get('preco_mediano')}/{item.get('unidade')}")
    return data.get("total", 0) > 0


def test_insumos_codigo(client: httpx.Client) -> bool:
    """Testa busca de insumo por código."""
    resp = client.get(
        f"{BASE_URL}/insumos",
        params={"codigo": 370, "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("total", 0) >= 1 and data["data"][0]["codigo"] == 370


def test_insumos_regime(client: httpx.Client) -> bool:
    """Testa filtro de insumos por regime."""
    resp = client.get(
        f"{BASE_URL}/insumos",
        params={"codigo": 370, "estado": "SP", "regime": "DESONERADO"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return (data.get("total", 0) >= 1
            and data["data"][0].get("regime") == "DESONERADO")


def test_composicoes_busca(client: httpx.Client) -> bool:
    """Testa busca de composições por nome."""
    resp = client.get(
        f"{BASE_URL}/composicoes",
        params={"nome": "argamassa", "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    print(f"    Encontradas: {data.get('total', 0)} composições")
    return data.get("total", 0) > 0


def test_composicao_detalhe(client: httpx.Client) -> bool:
    """Testa detalhamento de composição."""
    resp = client.get(
        f"{BASE_URL}/composicao",
        params={"codigo": 87316, "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    print(f"    Composição: {data.get('codigo')} - {data.get('descricao')}")
    print(f"    Itens: {len(data.get('itens', []))}")
    return data.get("codigo") == 87316 and "itens" in data


def test_composicao_explode(client: httpx.Client) -> bool:
    """Testa explosão de composição."""
    resp = client.get(
        f"{BASE_URL}/composicao_explode",
        params={"codigo": 87316, "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("total_itens", 0) >= 1


def test_historico(client: httpx.Client) -> bool:
    """Testa histórico de preços."""
    resp = client.get(
        f"{BASE_URL}/historico",
        params={"codigo": 370, "item": "insumo", "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("codigo") == 370 and "historico" in data


def test_comparar(client: httpx.Client) -> bool:
    """Testa comparação entre estados."""
    resp = client.get(
        f"{BASE_URL}/comparar",
        params={"codigo": 370, "item": "insumo", "estados": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("codigo") == 370 and "comparacao" in data


def test_previsao(client: httpx.Client) -> bool:
    """Testa previsão de preço."""
    resp = client.get(
        f"{BASE_URL}/previsao",
        params={"codigo": 370, "item": "insumo", "estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("previsao") is not None


def test_estados(client: httpx.Client) -> bool:
    """Testa listagem de estados."""
    resp = client.get(
        f"{BASE_URL}/estados",
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    total = len(data.get("estados", []))
    print(f"    Estados: {total}")
    return total == 27


def test_estados_filtro(client: httpx.Client) -> bool:
    """Testa filtro de estados por UF."""
    resp = client.get(
        f"{BASE_URL}/estados",
        params={"estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    estados = data.get("estados", [])
    return len(estados) == 1 and estados[0]["uf"] == "SP"


def test_orcamento(client: httpx.Client) -> bool:
    """Testa geração de orçamento."""
    resp = client.get(
        f"{BASE_URL}/orcamento",
        params={
            "itens": "C:87316@2.0,I:370@100",
            "estado": "SP",
            "regime": "NAO_DESONERADO",
        },
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    print(f"    Itens: {len(data.get('itens', []))}")
    print(f"    Subtotal: R$ {data.get('subtotal', 0):.2f}")
    print(f"    Total: R$ {data.get('total', 0):.2f}")
    return data.get("total", 0) > 0


def test_orcamento_bdi(client: httpx.Client) -> bool:
    """Testa orçamento com BDI."""
    resp = client.get(
        f"{BASE_URL}/orcamento",
        params={
            "itens": "I:370@100",
            "estado": "SP",
            "regime": "NAO_DESONERADO",
            "bdi": 25,
        },
        headers={"X-API-Key": API_KEY},
    )
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("bdi_valor", 0) > 0 and data.get("total", 0) > data.get("subtotal", 0)


def test_encargos(client: httpx.Client) -> bool:
    """Testa endpoint de encargos."""
    resp = client.get(
        f"{BASE_URL}/encargos",
        params={"estado": "SP"},
        headers={"X-API-Key": API_KEY},
    )
    return resp.status_code == 200


def test_indicadores(client: httpx.Client) -> bool:
    """Testa endpoint de indicadores."""
    resp = client.get(
        f"{BASE_URL}/indicadores",
        headers={"X-API-Key": API_KEY},
    )
    return resp.status_code == 200


def test_swagger_docs(client: httpx.Client) -> bool:
    """Testa acesso ao Swagger UI."""
    resp = client.get(f"{BASE_URL}/docs")
    return resp.status_code == 200 and "swagger" in resp.text.lower()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_tests():
    """Executa todos os testes contra o servidor."""
    import os
    import threading

    # Configura API key para aceitar 'teste-local'
    os.environ["API_KEYS"] = API_KEY

    # Inicia o servidor em thread separada
    print(colored("\n🚀 Iniciando servidor API SINAPI na porta 8777...", "cyan"))

    config = uvicorn.Config(
        "api.app:app",
        host="127.0.0.1",
        port=8777,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Aguarda servidor ficar pronto
    client = httpx.Client(timeout=10)
    for _ in range(30):
        try:
            client.get(f"{BASE_URL}/docs")
            break
        except httpx.ConnectError:
            time.sleep(0.2)
    else:
        print(colored("✗ Servidor não iniciou!", "red"))
        sys.exit(1)

    print(colored("✓ Servidor pronto!\n", "green"))

    results = []

    # ---- Upload ----
    print_header("1. Upload de Dados SINAPI")
    ok = test_upload(client)
    print_result("Upload XLSX com dados de amostra", ok)
    results.append(ok)

    # ---- Autenticação ----
    print_header("2. Autenticação (X-API-Key)")
    ok = test_auth_sem_chave(client)
    print_result("Rejeita requisição sem chave", ok)
    results.append(ok)

    ok = test_auth_chave_invalida(client)
    print_result("Rejeita chave inválida", ok)
    results.append(ok)

    # ---- Insumos ----
    print_header("3. Insumos (/insumos)")
    ok = test_insumos_busca(client)
    print_result("Buscar por nome", ok)
    results.append(ok)

    ok = test_insumos_codigo(client)
    print_result("Buscar por código", ok)
    results.append(ok)

    ok = test_insumos_regime(client)
    print_result("Filtrar por regime", ok)
    results.append(ok)

    # ---- Composições ----
    print_header("4. Composições (/composicoes, /composicao, /composicao_explode)")
    ok = test_composicoes_busca(client)
    print_result("Buscar composições", ok)
    results.append(ok)

    ok = test_composicao_detalhe(client)
    print_result("Detalhar composição", ok)
    results.append(ok)

    ok = test_composicao_explode(client)
    print_result("Explodir composição", ok)
    results.append(ok)

    # ---- Histórico / Comparar / Previsão ----
    print_header("5. Histórico, Comparar e Previsão")
    ok = test_historico(client)
    print_result("Histórico de preço", ok)
    results.append(ok)

    ok = test_comparar(client)
    print_result("Comparar entre estados", ok)
    results.append(ok)

    ok = test_previsao(client)
    print_result("Previsão de preço", ok)
    results.append(ok)

    # ---- Estados ----
    print_header("6. Estados (/estados)")
    ok = test_estados(client)
    print_result("Listar todos os estados", ok)
    results.append(ok)

    ok = test_estados_filtro(client)
    print_result("Filtrar por UF", ok)
    results.append(ok)

    # ---- Orçamento ----
    print_header("7. Orçamento (/orcamento)")
    ok = test_orcamento(client)
    print_result("Gerar orçamento", ok)
    results.append(ok)

    ok = test_orcamento_bdi(client)
    print_result("Orçamento com BDI", ok)
    results.append(ok)

    # ---- Extras ----
    print_header("8. Outros Endpoints")
    ok = test_encargos(client)
    print_result("Encargos", ok)
    results.append(ok)

    ok = test_indicadores(client)
    print_result("Indicadores", ok)
    results.append(ok)

    ok = test_swagger_docs(client)
    print_result("Swagger UI (/docs)", ok)
    results.append(ok)

    # ---- Resultado final ----
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"\n{colored('=' * 60, 'cyan')}")
    if failed == 0:
        print(colored(f"  ✓ TODOS OS {total} TESTES PASSARAM!", "green"))
    else:
        print(colored(f"  {passed}/{total} testes passaram, {failed} falharam", "red"))
    print(colored('=' * 60, 'cyan'))

    # Encerra o servidor
    server.should_exit = True
    client.close()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    run_tests()
