import json

import pandas as pd
import plotly.express as px

from app.models import Avaliacao, AvaliacaoSintoma, Paciente, Sintoma


def build_reports(db, profissional_id):
    assessments = _assessments_frame(db, profissional_id)
    symptoms = _symptoms_frame(db, profissional_id)

    return {
        "indicators": _indicators(assessments, symptoms),
        "tables": {
            "bySex": _by_sex_table(assessments),
            "topSymptoms": _top_symptoms_table(symptoms),
        },
        "charts": _charts(assessments, symptoms),
    }


def _assessments_frame(db, profissional_id):
    rows = (
        db.query(
            Avaliacao.id,
            Avaliacao.score_calculado,
            Avaliacao.encaminhar,
            Avaliacao.realizado_em,
            Paciente.nome,
            Paciente.sexo,
            Paciente.data_nascimento,
        )
        .join(Paciente, Paciente.id == Avaliacao.paciente_id)
        .filter(Avaliacao.profissional_id == profissional_id)
        .all()
    )

    data = [{
        "id": row.id,
        "score": float(row.score_calculado),
        "recommendation": "Encaminhar" if row.encaminhar else "Não prioritário",
        "encaminhar": bool(row.encaminhar),
        "date": row.realizado_em,
        "month": row.realizado_em.strftime("%Y-%m"),
        "patient": row.nome,
        "sex": "Masculino" if row.sexo.value == "masculino" else "Feminino",
        "age": _age(row.data_nascimento),
    } for row in rows]

    return pd.DataFrame(data)


def _symptoms_frame(db, profissional_id):
    rows = (
        db.query(Sintoma.descricao, Sintoma.categoria)
        .join(AvaliacaoSintoma, AvaliacaoSintoma.sintoma_id == Sintoma.id)
        .join(Avaliacao, Avaliacao.id == AvaliacaoSintoma.avaliacao_id)
        .filter(Avaliacao.profissional_id == profissional_id, AvaliacaoSintoma.presente.is_(True))
        .all()
    )

    return pd.DataFrame([{
        "symptom": row.descricao,
        "category": row.categoria,
    } for row in rows])


def _age(birth_date):
    today = pd.Timestamp.today().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _indicators(assessments, symptoms):
    total_assessments = len(assessments)
    total_referrals = int(assessments["encaminhar"].sum()) if total_assessments else 0
    referral_rate = (total_referrals / total_assessments * 100) if total_assessments else 0

    return {
        "totalAssessments": total_assessments,
        "totalReferrals": total_referrals,
        "nonPriority": total_assessments - total_referrals,
        "referralRate": round(referral_rate, 1),
        "averageScore": _round_or_zero(assessments["score"].mean() if total_assessments else 0),
        "medianScore": _round_or_zero(assessments["score"].median() if total_assessments else 0),
        "maxScore": _round_or_zero(assessments["score"].max() if total_assessments else 0),
        "averageAge": _round_or_zero(assessments["age"].mean() if total_assessments else 0),
        "symptomsMarked": len(symptoms),
        "mostFrequentSymptom": _most_frequent_symptom(symptoms),
    }


def _round_or_zero(value):
    if pd.isna(value):
        return 0
    return round(float(value), 2)


def _most_frequent_symptom(symptoms):
    if symptoms.empty:
        return "Sem dados"
    return str(symptoms["symptom"].value_counts().idxmax())


def _by_sex_table(assessments):
    if assessments.empty:
        return []

    grouped = (
        assessments
        .groupby("sex")
        .agg(
            total=("id", "count"),
            referrals=("encaminhar", "sum"),
            averageScore=("score", "mean"),
            averageAge=("age", "mean"),
        )
        .reset_index()
    )
    grouped["referralRate"] = grouped["referrals"] / grouped["total"] * 100
    grouped["referrals"] = grouped["referrals"].astype(int)

    return [{
        "sex": row.sex,
        "total": int(row.total),
        "referrals": int(row.referrals),
        "referralRate": round(float(row.referralRate), 1),
        "averageScore": round(float(row.averageScore), 2),
        "averageAge": round(float(row.averageAge), 1),
    } for row in grouped.itertuples()]


def _top_symptoms_table(symptoms):
    if symptoms.empty:
        return []

    counts = symptoms.value_counts(["symptom", "category"]).reset_index(name="count").head(8)
    return [{
        "symptom": row.symptom,
        "category": row.category,
        "count": int(row.count),
    } for row in counts.itertuples()]


def _charts(assessments, symptoms):
    return {
        "recommendations": _figure_json(_recommendations_chart(assessments)),
        "scoreBySex": _figure_json(_score_by_sex_chart(assessments)),
        "assessmentsByMonth": _figure_json(_assessments_by_month_chart(assessments)),
        "topSymptoms": _figure_json(_top_symptoms_chart(symptoms)),
    }


def _recommendations_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem avaliações para exibir")

    counts = assessments["recommendation"].value_counts().reset_index()
    counts.columns = ["recommendation", "total"]
    fig = px.pie(
        counts,
        names="recommendation",
        values="total",
        color="recommendation",
        color_discrete_map={"Encaminhar": "#D97706", "Não prioritário": "#16A34A"},
        hole=0.45,
    )
    return _style_figure(fig)


def _score_by_sex_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem scores para exibir")

    fig = px.box(
        assessments,
        x="sex",
        y="score",
        color="sex",
        points="all",
        color_discrete_map={"Masculino": "#2563EB", "Feminino": "#DB2777"},
        labels={"sex": "Sexo", "score": "Score"},
    )
    return _style_figure(fig)


def _assessments_by_month_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem avaliações por período")

    monthly = assessments.groupby("month").size().reset_index(name="total")
    fig = px.bar(monthly, x="month", y="total", labels={"month": "Mês", "total": "Avaliações"})
    fig.update_traces(marker_color="#2563EB")
    return _style_figure(fig)


def _top_symptoms_chart(symptoms):
    if symptoms.empty:
        return _empty_figure("Sem sintomas marcados")

    top = symptoms["symptom"].value_counts().head(8).reset_index()
    top.columns = ["symptom", "total"]
    fig = px.bar(top, x="total", y="symptom", orientation="h", labels={"total": "Ocorrencias", "symptom": "Sintoma"})
    fig.update_traces(marker_color="#7C3AED")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _style_figure(fig)


def _style_figure(fig):
    fig.update_layout(
        margin={"l": 24, "r": 16, "t": 20, "b": 24},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"family": "DM Sans, sans-serif", "color": "#0F172A"},
        showlegend=True,
    )
    return fig


def _empty_figure(message):
    fig = px.scatter()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font={"size": 14, "color": "#64748B"})
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style_figure(fig)


def _figure_json(fig):
    return json.loads(fig.to_json())
