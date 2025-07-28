from flask import Blueprint

test_imports = Blueprint('test_imports', __name__, url_prefix='/api/import')

@test_imports.route('/test', methods=['GET'])  
def test_import():
    return {'message': 'Import test endpoint working'}, 200
