from io import BytesIO

import pandas as pd

from app.models import Avaliacao, Paciente


def patients_workbook(db, profissional_id):
    rows = (
        db.query(Paciente)
        .filter(Paciente.profissional_id == profissional_id)
        .order_by(Paciente.criado_em.desc())
        .all()
    )

    data = []
    for paciente in rows:
        ultima = max(paciente.avaliacoes, key=lambda avaliacao: avaliacao.realizado_em, default=None)
        data.append({
            "ID": paciente.id,
            "Nome": paciente.nome,
            "Sexo": "Feminino" if paciente.sexo.value == "feminino" else "Masculino",
            "Data de nascimento": paciente.data_nascimento,
            "Idade": paciente.idade,
            "Data de cadastro": paciente.criado_em,
            "Último score": round(ultima.score_calculado, 2) if ultima else None,
            "Última recomendação": _recommendation(ultima.encaminhar) if ultima else None,
        })

    columns = [
        "ID",
        "Nome",
        "Sexo",
        "Data de nascimento",
        "Idade",
        "Data de cadastro",
        "Último score",
        "Última recomendação",
    ]
    return _xlsx_response(pd.DataFrame(data, columns=columns), "Pacientes")


def assessments_workbook(db, profissional_id):
    rows = (
        db.query(Avaliacao)
        .filter(Avaliacao.profissional_id == profissional_id)
        .order_by(Avaliacao.realizado_em.desc())
        .all()
    )

    data = []
    for avaliacao in rows:
        paciente = avaliacao.paciente
        sintomas_presentes = [
            item.sintoma.descricao
            for item in avaliacao.sintomas
            if item.presente
        ]
        data.append({
            "ID": avaliacao.id,
            "Paciente": paciente.nome,
            "Sexo": "Feminino" if paciente.sexo.value == "feminino" else "Masculino",
            "Score": round(avaliacao.score_calculado, 2),
            "Limiar": round(avaliacao.limiar_decisao.valor, 2),
            "Recomendação": _recommendation(avaliacao.encaminhar),
            "Sintomas presentes": ", ".join(sintomas_presentes),
            "Observação": avaliacao.observacao,
            "Data da avaliação": avaliacao.realizado_em,
        })

    columns = [
        "ID",
        "Paciente",
        "Sexo",
        "Score",
        "Limiar",
        "Recomendação",
        "Sintomas presentes",
        "Observação",
        "Data da avaliação",
    ]
    return _xlsx_response(pd.DataFrame(data, columns=columns), "Histórico de Avaliações")


def _xlsx_response(frame, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes = "A2"

        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 48)

    output.seek(0)
    return output


def _recommendation(should_refer):
    return "Encaminhar" if should_refer else "Não prioritário"
