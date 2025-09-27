from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from Database_main.database import db

table_bp = Blueprint('table_bp', __name__)

@table_bp.route('/api/tables/distribute', methods=['POST'])
def distribute_data():
    try:
        data = request.get_json()
        parent_table_name = data.get('parent_table_name')

        if not parent_table_name:
            return jsonify({"error": "Parameter 'parent_table_name' is required."}), 400

        db.session.execute(
            text("CALL DistributeDataWithCursor(:parent_table_name)"),
            {"parent_table_name": parent_table_name}
        )
        db.session.commit()

        return jsonify({"message": f"Data from '{parent_table_name}' distributed successfully into new tables."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred.", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error occurred.", "details": str(e)}), 500

