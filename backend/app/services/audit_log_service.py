from app.utils.masking import mask_phi

class AuditLogService:
    def build(self, trace_id: str, patient_id: int | None, actor: str, action: str, input_meta: dict | None, output_meta: dict | None) -> dict:
        return {
            'trace_id': trace_id,
            'patient_id': patient_id,
            'actor': actor,
            'action': action,
            'input_meta_json': mask_phi(str(input_meta)) if input_meta else None,
            'output_meta_json': mask_phi(str(output_meta)) if output_meta else None,
        }
