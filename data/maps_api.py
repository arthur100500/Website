from flask import Blueprint, jsonify
from data import db_session
from data.maps import Maps

blueprint = Blueprint('maps_api', __name__,
                      template_folder='templates')


@blueprint.route('/api/textures', methods=['GET'])
def get_maps():
    session = db_session.create_session()
    maps = session.query(Maps).all()
    return jsonify(
        {
            'textures':
                [item.to_dict() for item in maps]
        }
    )
