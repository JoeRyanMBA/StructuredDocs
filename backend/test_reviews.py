from flask import Blueprint

# Not a pytest test module; prevent pytest collection
__test__ = False

print("Creating reviews blueprint...")
reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
print("Blueprint created successfully!")

@reviews_bp.route('/')
def reviews_status():
    return "Reviews working"
