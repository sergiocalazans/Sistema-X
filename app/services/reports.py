import json

import pandas as pd
import plotly.express as px

from app.models import Avaliacao, AvaliacaoSintoma, Paciente, Sintoma


def build_reports(db, profissional_id, include_all=False):
    assessments = _assessments_frame(db, profissional_id, include_all)
    symptoms = _symptoms_frame(db, profissional_id, include_all)

    return {
        "indicators": _indicators(assessments, symptoms),
        "analyses": _analyses(assessments, symptoms),
        "tables": {
            "bySex": _by_sex_table(assessments),
            "byAgeGroup": _by_age_group_table(assessments),
            "topSymptoms": _top_symptoms_table(symptoms),
        },
        "charts": _charts(assessments, symptoms),
    }


def _assessments_frame(db, profissional_id, include_all):
    query = (
        db.query(
            Avaliacao.id,
            Avaliacao.score_calculado,
            Avaliacao.encaminhar,
            Avaliacao.resultado_exame,
            Avaliacao.realizado_em,
            Paciente.nome,
            Paciente.sexo,
            Paciente.data_nascimento,
        )
        .join(Paciente, Paciente.id == Avaliacao.paciente_id)
    )
    if not include_all:
        query = query.filter(Avaliacao.profissional_id == profissional_id)
    rows = query.all()

    data = []
    for row in rows:
        age = _age(row.data_nascimento)
        data.append({
            "id": row.id,
            "score": float(row.score_calculado),
            "recommendation": "Encaminhar" if row.encaminhar else "Não prioritário",
            "encaminhar": bool(row.encaminhar),
            "date": row.realizado_em,
            "month": pd.Period(row.realizado_em, freq="M"),
            "patient": row.nome,
            "sex": "Masculino" if row.sexo.value == "masculino" else "Feminino",
            "age": age,
            "ageGroup": _age_group(age),
            "examResult": _exam_result_label(row.resultado_exame),
        })

    return pd.DataFrame(data)


def _symptoms_frame(db, profissional_id, include_all):
    query = (
        db.query(Sintoma.descricao, Sintoma.categoria)
        .join(AvaliacaoSintoma, AvaliacaoSintoma.sintoma_id == Sintoma.id)
        .join(Avaliacao, Avaliacao.id == AvaliacaoSintoma.avaliacao_id)
        .filter(AvaliacaoSintoma.presente.is_(True))
    )
    if not include_all:
        query = query.filter(Avaliacao.profissional_id == profissional_id)
    rows = query.all()

    return pd.DataFrame([{
        "symptom": row.descricao,
        "category": row.categoria,
    } for row in rows])


def _age(birth_date):
    today = pd.Timestamp.today().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _age_group(age):
    if age <= 5:
        return "0 a 5"
    if age <= 11:
        return "6 a 11"
    if age <= 17:
        return "12 a 17"
    return "18+"


def _exam_result_label(value):
    labels = {
        "aguardando": "Aguardando",
        "positivo": "Positivo",
        "negativo": "Negativo",
        "inconclusivo": "Inconclusivo",
    }
    return labels.get(value or "aguardando", "Aguardando")


def _indicators(assessments, symptoms):
    total_assessments = len(assessments)
    total_referrals = int(assessments["encaminhar"].sum()) if total_assessments else 0
    referral_rate = (total_referrals / total_assessments * 100) if total_assessments else 0
    positive_results = int((assessments["examResult"] == "Positivo").sum()) if total_assessments else 0

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
        "positiveResults": positive_results,
        "mostFrequentSymptom": _most_frequent_symptom(symptoms),
    }


def _analyses(assessments, symptoms):
    if assessments.empty:
        return [{
            "title": "Base insuficiente",
            "value": "Sem avaliações",
            "description": "Cadastre avaliações para gerar análises automáticas.",
        }]

    # Os cards abaixo sintetizam padrões relevantes para apoiar a decisão clínica e a apresentação dos dados.
    return [
        _highest_referral_age_group(assessments),
        _symptoms_per_assessment(assessments, symptoms),
        _score_dispersion(assessments),
        _exam_result_analysis(assessments),
    ]


def _highest_referral_age_group(assessments):
    grouped = (
        assessments
        .groupby("ageGroup")
        .agg(total=("id", "count"), referrals=("encaminhar", "sum"))
        .reset_index()
    )
    grouped["rate"] = grouped["referrals"] / grouped["total"] * 100
    top = grouped.sort_values(["rate", "total"], ascending=[False, False]).iloc[0]
    return {
        "title": "Faixa com maior encaminhamento",
        "value": f"{top.ageGroup} anos",
        "description": f"{round(float(top.rate), 1)}% das avaliações dessa faixa indicaram encaminhamento.",
    }


def _symptoms_per_assessment(assessments, symptoms):
    average = len(symptoms) / len(assessments) if len(assessments) else 0
    return {
        "title": "Sintomas por avaliação",
        "value": round(average, 1),
        "description": "Média de sintomas presentes marcados nos checklists clínicos.",
    }


def _score_dispersion(assessments):
    minimum = _round_or_zero(assessments["score"].min())
    maximum = _round_or_zero(assessments["score"].max())
    return {
        "title": "Amplitude dos scores",
        "value": f"{minimum} a {maximum}",
        "description": "Ajuda a comparar casos leves, intermediários e prioritários.",
    }


def _exam_result_analysis(assessments):
    completed = assessments[assessments["examResult"].isin(["Positivo", "Negativo", "Inconclusivo"])]
    if completed.empty:
        return {
            "title": "Resultados de exame",
            "value": "Aguardando",
            "description": "Ainda não há exames concluídos para medir desfechos.",
        }
    positives = int((completed["examResult"] == "Positivo").sum())
    rate = positives / len(completed) * 100
    return {
        "title": "Positividade entre exames",
        "value": f"{round(rate, 1)}%",
        "description": f"{positives} de {len(completed)} exames concluídos tiveram resultado positivo.",
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


def _by_age_group_table(assessments):
    if assessments.empty:
        return []

    grouped = (
        assessments
        .groupby("ageGroup")
        .agg(
            total=("id", "count"),
            referrals=("encaminhar", "sum"),
            averageScore=("score", "mean"),
            positiveResults=("examResult", lambda values: int((values == "Positivo").sum())),
        )
        .reset_index()
    )
    grouped["referralRate"] = grouped["referrals"] / grouped["total"] * 100

    return [{
        "ageGroup": row.ageGroup,
        "total": int(row.total),
        "referrals": int(row.referrals),
        "referralRate": round(float(row.referralRate), 1),
        "averageScore": round(float(row.averageScore), 2),
        "positiveResults": int(row.positiveResults),
    } for row in grouped.itertuples()]


def _charts(assessments, symptoms):
    return {
        "recommendations": _figure_json(_recommendations_chart(assessments)),
        "scoreBySex": _figure_json(_score_by_sex_chart(assessments)),
        "assessmentsByMonth": _figure_json(_assessments_by_month_chart(assessments)),
        "topSymptoms": _figure_json(_top_symptoms_chart(symptoms)),
        "ageDistribution": _figure_json(_age_distribution_chart(assessments)),
        "referralsByAge": _figure_json(_referrals_by_age_chart(assessments)),
        "examResults": _figure_json(_exam_results_chart(assessments)),
        "scoreTrend": _figure_json(_score_trend_chart(assessments)),
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

    monthly_counts = assessments.groupby("month").size()
    months = pd.period_range(monthly_counts.index.min(), monthly_counts.index.max(), freq="M")
    monthly = (
        monthly_counts
        .reindex(months, fill_value=0)
        .rename_axis("month_period")
        .reset_index(name="total")
    )
    monthly["month"] = monthly["month_period"].dt.strftime("%m/%Y")

    fig = px.bar(
        monthly,
        x="month",
        y="total",
        labels={"month": "Mês", "total": "Avaliações"},
    )
    fig.update_traces(marker_color="#2563EB")
    fig.update_layout(
        xaxis={
            "categoryorder": "array",
            "categoryarray": monthly["month"].tolist(),
        },
        yaxis={"dtick": 1, "rangemode": "tozero"},
    )
    return _style_figure(fig)


def _top_symptoms_chart(symptoms):
    if symptoms.empty:
        return _empty_figure("Sem sintomas marcados")

    top = symptoms["symptom"].value_counts().head(8).reset_index()
    top.columns = ["symptom", "total"]
    fig = px.bar(top, x="total", y="symptom", orientation="h", labels={"total": "Ocorrências", "symptom": "Sintoma"})
    fig.update_traces(marker_color="#7C3AED")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _style_figure(fig)


def _age_distribution_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem idades para exibir")

    fig = px.histogram(
        assessments,
        x="age",
        nbins=8,
        labels={"age": "Idade", "count": "Avaliações"},
    )
    fig.update_traces(marker_color="#0891B2")
    fig.update_layout(yaxis={"dtick": 1, "rangemode": "tozero"})
    return _style_figure(fig)


def _referrals_by_age_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem encaminhamentos por idade")

    grouped = assessments.groupby(["ageGroup", "recommendation"]).size().reset_index(name="total")
    fig = px.bar(
        grouped,
        x="ageGroup",
        y="total",
        color="recommendation",
        barmode="group",
        labels={"ageGroup": "Faixa etária", "total": "Avaliações", "recommendation": "Recomendação"},
        color_discrete_map={"Encaminhar": "#D97706", "Não prioritário": "#16A34A"},
    )
    fig.update_layout(yaxis={"dtick": 1, "rangemode": "tozero"})
    return _style_figure(fig)


def _exam_results_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem resultados de exame")

    counts = assessments["examResult"].value_counts().reset_index()
    counts.columns = ["examResult", "total"]
    fig = px.pie(
        counts,
        names="examResult",
        values="total",
        color="examResult",
        color_discrete_map={
            "Aguardando": "#64748B",
            "Positivo": "#DC2626",
            "Negativo": "#16A34A",
            "Inconclusivo": "#D97706",
        },
        hole=0.45,
    )
    return _style_figure(fig)


def _score_trend_chart(assessments):
    if assessments.empty:
        return _empty_figure("Sem tendência de score")

    # Compara score médio e taxa de encaminhamento no mesmo eixo para destacar meses fora do padrão.
    monthly = (
        assessments
        .groupby("month")
        .agg(averageScore=("score", "mean"), referralRate=("encaminhar", "mean"))
        .reset_index()
    )
    monthly["monthLabel"] = monthly["month"].dt.strftime("%m/%Y")
    monthly["referralRate"] = monthly["referralRate"] * 100

    fig = px.line(
        monthly,
        x="monthLabel",
        y=["averageScore", "referralRate"],
        markers=True,
        labels={"monthLabel": "Mês", "value": "Valor", "variable": "Indicador"},
    )
    fig.for_each_trace(lambda trace: trace.update(name={
        "averageScore": "Score médio",
        "referralRate": "Taxa de encaminhamento (%)",
    }.get(trace.name, trace.name)))
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
