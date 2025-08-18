from flask import Blueprint

print("Creating reviews blueprint...")
reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
print("Blueprint created successfully!")

@reviews_bp.route('/')
def test_route():
    return "Reviews working"
