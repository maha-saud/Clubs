from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def validate_password_ar(password):
    try:
        validate_password(password)
    except ValidationError as e:
        errors = []

        for msg in e.messages:
            if "too short" in msg:
                errors.append("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
            elif "too common" in msg:
                errors.append("كلمة المرور ضعيفة أو شائعة.")
            elif "numeric" in msg:
                errors.append("لا يمكن أن تكون كلمة المرور أرقام فقط.")

        raise ValidationError(errors)
