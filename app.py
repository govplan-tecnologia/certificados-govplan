from flask import Flask, render_template, request
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__)

PALAVRA_CHAVE_CORRETA = "govplan"

MINISTRANTE_FIXO = "Renato Fenili e Viviane Mafissoni"
DATA_EVENTO_FIXA = "12 de maio de 2026"
CARGA_HORARIA_FIXA = "4"

# ── Google Sheets ──────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
    """Retorna a primeira aba da planilha configurada."""
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("Variável de ambiente GOOGLE_CREDENTIALS_JSON não definida.")

    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise RuntimeError("Variável de ambiente SPREADSHEET_ID não definida.")

    return client.open_by_key(spreadsheet_id).sheet1


CABECALHO = [
    "data_hora_resposta", "nome", "orgao", "uf",
    "pca_estruturado", "planejamento_atual", "desafios",
    "ferramenta_pca", "receber_proposta", "palavra_chave_informada",
    "avaliacao", "codigo_certificado",
]

def salvar_no_sheets(dados: dict) -> None:
    """Adiciona uma linha na planilha. Cria cabeçalho se a aba estiver vazia."""
    sheet = get_sheet()

    # Se a planilha estiver vazia, insere o cabeçalho primeiro
    if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
        sheet.append_row(CABECALHO)

    linha = [dados.get(col, "") for col in CABECALHO]
    sheet.append_row(linha)
# ──────────────────────────────────────────────────────────────


@app.route("/")
def formulario():
    return render_template("formulario.html", erro=None)


@app.route("/certificado", methods=["POST"])
def certificado():
    nome = request.form.get("nome", "").strip()
    orgao = request.form.get("orgao", "").strip()
    uf = request.form.get("uf", "").strip()

    pca_estruturado = request.form.get("pca_estruturado", "").strip()
    planejamento_atual = request.form.get("planejamento_atual", "").strip()

    desafios = request.form.getlist("desafios")
    desafios_str = ", ".join(desafios)

    ferramenta_pca = request.form.get("ferramenta_pca", "").strip()
    receber_proposta = request.form.get("receber_proposta", "").strip()

    avaliacao = request.form.get("avaliacao", "").strip()
    palavra_chave = request.form.get("palavra_chave", "").strip()

    if palavra_chave.lower() != PALAVRA_CHAVE_CORRETA.lower():
        return render_template(
            "formulario.html",
            erro="Palavra-chave incorreta. Verifique a informação passada no evento e tente novamente."
        )

    codigo_certificado = datetime.now().strftime("CERT-GOVPLAN-DAY-SP-2026-%Y%m%d%H%M%S")

    dados_resposta = {
        "data_hora_resposta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "orgao": orgao,
        "uf": uf,
        "pca_estruturado": pca_estruturado,
        "planejamento_atual": planejamento_atual,
        "desafios": desafios_str,
        "ferramenta_pca": ferramenta_pca,
        "receber_proposta": receber_proposta,
        "palavra_chave_informada": palavra_chave,
        "avaliacao": avaliacao,
        "codigo_certificado": codigo_certificado,
    }

    salvar_no_sheets(dados_resposta)

    return render_template(
        "certificado.html",
        NOME_COMPLETO=nome,
        DATA_EVENTO=DATA_EVENTO_FIXA,
        CARGA_HORARIA=CARGA_HORARIA_FIXA,
        MINISTRANTE=MINISTRANTE_FIXO,
        CODIGO_CERTIFICADO=codigo_certificado
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)