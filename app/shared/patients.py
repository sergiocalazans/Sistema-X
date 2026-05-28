from app.models import Paciente, Profissional


def professional_patient_query(db, profissional_id):
    return (
        db.query(Paciente)
        .join(Paciente.profissionais)
        .filter(Profissional.id == profissional_id)
    )
