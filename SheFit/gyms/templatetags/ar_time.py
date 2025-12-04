from django import template
from datetime import datetime, timezone

register = template.Library()

@register.filter
def ar_naturaltime(value):
    """
    صياغة عربية لوقت التعليق مثل:
    منذ دقيقة – منذ ساعتين – أمس – منذ أسبوع
    """

    if not value:
        return ""

    now = datetime.now(timezone.utc)
    diff = now - value

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = diff.days

    # ثواني
    if seconds < 60:
        return "منذ ثوانٍ"

    # دقائق
    if minutes < 60:
        m = int(minutes)
        if m == 1:
            return "منذ دقيقة"
        elif m == 2:
            return "منذ دقيقتين"
        elif m <= 10:
            return f"منذ {m} دقائق"
        else:
            return f"منذ {m} دقيقة"

    # ساعات
    if hours < 24:
        h = int(hours)
        if h == 1:
            return "منذ ساعة"
        elif h == 2:
            return "منذ ساعتين"
        elif h <= 10:
            return f"منذ {h} ساعات"
        else:
            return f"منذ {h} ساعة"

    # أيام
    if days == 1:
        return "أمس"
    if days == 2:
        return "منذ يومين"
    if days <= 10:
        return f"منذ {days} أيام"
    return f"منذ {days} يوم"
