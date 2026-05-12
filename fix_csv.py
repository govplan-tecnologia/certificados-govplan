import csv
import os

ARQUIVO_ENTRADA = "respostas.csv"
ARQUIVO_SAIDA = "respostas_corrigido.csv"
DELIMITADOR_SAIDA = ';'

# Mapeamento de campos antigos para novos (se necessário) ou apenas garantir todos os campos
# Baseado no app.py atualizado
CAMPOS_FINAIS = [
    "data_hora_resposta", "nome", "orgao", "uf", 
    "pca_estruturado", "planejamento_atual", "desafios", 
    "ferramenta_pca", "receber_proposta", "palavra_chave_informada", 
    "avaliacao", "codigo_certificado"
]

# Mapeamento de campos que mudaram de nome entre as versões
MAPEAMENTO = {
    "ja_fez_pca": "pca_estruturado",
    "publicou_pca_2026": "planejamento_atual",
    "primeira_vez_oficina": "desafios", # Aproximação se não houver exato
    "gestao_pca": "ferramenta_pca",
    "interesse_govplan": "receber_proposta"
}

def fix_csv():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Arquivo {ARQUIVO_ENTRADA} não encontrado.")
        return

    linhas_corrigidas = []

    with open(ARQUIVO_ENTRADA, mode='r', encoding='utf-8-sig') as f:
        content = f.readlines()

    for i, linha in enumerate(content):
        linha = linha.strip()
        if not linha:
            continue
        
        # Detectar delimitador
        if ';' in linha:
            parts = linha.split(';')
        else:
            # Tentar vírgula, mas ignorar vírgulas dentro de aspas se houver
            reader = csv.reader([linha], delimiter=',')
            parts = next(reader)

        if i == 0:
            # É o cabeçalho original
            cabecalho_original = [p.strip() for p in parts]
            continue
        
        # Criar dicionário da linha original
        dados_originais = {}
        for j, valor in enumerate(parts):
            if j < len(cabecalho_original):
                dados_originais[cabecalho_original[j]] = valor.strip()

        # Criar nova linha com campos finais
        nova_linha = {}
        for campo in CAMPOS_FINAIS:
            # 1. Tentar nome direto
            valor = dados_originais.get(campo)
            
            # 2. Tentar via mapeamento se não achou
            if valor is None:
                for antigo, novo in MAPEAMENTO.items():
                    if novo == campo:
                        valor = dados_originais.get(antigo)
                        break
            
            nova_linha[campo] = valor if valor is not None else ""
        
        linhas_corrigidas.append(nova_linha)

    # Salvar o novo arquivo
    with open(ARQUIVO_SAIDA, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_FINAIS, delimiter=DELIMITADOR_SAIDA)
        writer.writeheader()
        writer.writerows(linhas_corrigidas)

    print(f"Sucesso! Arquivo corrigido salvo como: {ARQUIVO_SAIDA}")
    print(f"Total de registros processados: {len(linhas_corrigidas)}")

if __name__ == "__main__":
    fix_csv()
