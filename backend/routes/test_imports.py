from flask import Blueprint

# This module defines a Flask route and is not a pytest test module.
# Prevent pytest from collecting it by setting __test__ = False.
__test__ = False

test_imports = Blueprint('test_imports', __name__, url_prefix='/api/import')

@test_imports.route('/test', methods=['GET'])
def import_test():
    return {'message': 'Import test endpoint working'}, 200
