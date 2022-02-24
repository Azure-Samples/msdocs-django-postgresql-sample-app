from django import template

register = template.Library()


@register.inclusion_tag('restaurant_review/star_rating.html')
def star_rating(avg_rating, review_count):    
    stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
    return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}