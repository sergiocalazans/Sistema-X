from app.models import Paciente, Profissional
from app.shared.auth import ROLE_ADMIN, current_user_role


def professional_patient_query(db, profissional_id):
    if current_user_role() == ROLE_ADMIN:
        return db.query(Paciente)

    return (
        db.query(Paciente)
        .join(Paciente.profissionais)
        .filter(Profissional.id == profissional_id)
    )
