from flask import Flask, render_template, request
from datetime import datetime
import csv
import os

app = Flask(__name__)

PALAVRA_CHAVE_CORRETA = "govplan"

MINISTRANTE_FIXO = "Renato Fenili e Viviiane Mafissoni"
DATA_EVENTO_FIXA = "12 de maio de 2026"
CARGA_HORARIA_FIXA = "4"

ARQUIVO_CSV = "respostas.csv"


def salvar_resposta_csv(dados: dict) -> None:
    arquivo_existe = os.path.isfile(ARQUIVO_CSV)

    with open(ARQUIVO_CSV, mode="a", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=dados.keys())

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(dados)


@app.route("/")
def formulario():
    return render_template("formulario.html", erro=None)


@app.route("/certificado", methods=["POST"])
def certificado():
    nome = request.form.get("nome", "").strip()
    orgao = request.form.get("orgao", "").strip()
    uf = request.form.get("uf", "").strip()
    pca = request.form.get("pca", "").strip()
    publicou = request.form.get("publicou", "").strip()
    primeira_vez = request.form.get("primeira_vez", "").strip()
    gestao = request.form.get("gestao", "").strip()
    interesse = request.form.get("interesse", "").strip()
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
        "ja_fez_pca": pca,
        "publicou_pca_2026": publicou,
        "primeira_vez_oficina": primeira_vez,
        "gestao_pca": gestao,
        "interesse_govplan": interesse,
        "palavra_chave_informada": palavra_chave,
        "avaliacao": avaliacao,
        "codigo_certificado": codigo_certificado,
    }

    salvar_resposta_csv(dados_resposta)

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