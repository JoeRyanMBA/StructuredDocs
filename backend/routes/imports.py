from flask import Blueprint

imports = Blueprint('imports', __name__, url_prefix='/api/import')

@imports.route('/test', methods=['GET'])
def test_import():
    return {'message': 'Import test endpoint working'}, 200