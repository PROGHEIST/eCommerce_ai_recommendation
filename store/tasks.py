from celery import shared_task
from .recommendations import generate_recommendations

@shared_task
def update_ai_recommendations():
    generate_recommendations()
    return "AI Recommendations Updated"
