"""
API Routes Module
Defines all REST API endpoints for the procurement system
"""

from flask import Blueprint, jsonify, request, current_app
from functools import wraps
from database.connection import get_db
from sqlalchemy import text

# Create API blueprint
api_bp = Blueprint('api', __name__)


# ============================================
# DECORATORS
# ============================================

def handle_errors(f):
    """Decorator to handle exceptions and return proper JSON responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"API Error: {str(e)}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500
    return decorated_function


def paginate(default_limit=20, max_limit=100):
    """Decorator to add pagination support to endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            limit = min(
                request.args.get('limit', default_limit, type=int),
                max_limit
            )
            offset = (page - 1) * limit

            kwargs['page'] = page
            kwargs['limit'] = limit
            kwargs['offset'] = offset
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================
# DOCUMENTATION ENDPOINT
# ============================================

@api_bp.route('/docs')
def api_docs():
    """API Documentation endpoint."""
    return jsonify({
        'api_version': 'v1',
        'base_url': '/api/v1',
        'endpoints': {
            'projects': {
                'list': 'GET /projects',
                'create': 'POST /projects',
                'get': 'GET /projects/<id>',
                'update': 'PUT /projects/<id>',
                'delete': 'DELETE /projects/<id>'
            },
            'vendors': {
                'list': 'GET /vendors',
                'create': 'POST /vendors',
                'get': 'GET /vendors/<id>',
                'update': 'PUT /vendors/<id>',
                'delete': 'DELETE /vendors/<id>',
                'approve': 'POST /vendors/<id>/approve'
            },
            'items': {
                'list': 'GET /items',
                'create': 'POST /items',
                'get': 'GET /items/<id>',
                'update': 'PUT /items/<id>',
                'delete': 'DELETE /items/<id>'
            },
            'rfqs': {
                'list': 'GET /rfqs',
                'create': 'POST /rfqs',
                'get': 'GET /rfqs/<id>',
                'update': 'PUT /rfqs/<id>',
                'delete': 'DELETE /rfqs/<id>',
                'items': 'GET /rfqs/<id>/items',
                'invite_vendors': 'POST /rfqs/<id>/invite',
                'close': 'POST /rfqs/<id>/close'
            },
            'quotations': {
                'list': 'GET /quotations',
                'create': 'POST /quotations',
                'get': 'GET /quotations/<id>',
                'update': 'PUT /quotations/<id>',
                'compare': 'GET /rfqs/<rfq_id>/quotations/compare'
            },
            'tbe_evaluations': {
                'list': 'GET /tbe-evaluations',
                'create': 'POST /tbe-evaluations',
                'get': 'GET /tbe-evaluations/<id>',
                'calculate': 'POST /tbe-evaluations/<id>/calculate',
                'finalize': 'POST /tbe-evaluations/<id>/finalize'
            },
            'purchase_orders': {
                'list': 'GET /purchase-orders',
                'create': 'POST /purchase-orders',
                'get': 'GET /purchase-orders/<id>',
                'update': 'PUT /purchase-orders/<id>',
                'approve': 'POST /purchase-orders/<id>/approve',
                'cancel': 'POST /purchase-orders/<id>/cancel'
            },
            'reports': {
                'dashboard': 'GET /reports/dashboard',
                'procurement_summary': 'GET /reports/procurement-summary',
                'vendor_performance': 'GET /reports/vendor-performance'
            }
        }
    }), 200


# ============================================
# PROJECT ENDPOINTS
# ============================================

@api_bp.route('/projects', methods=['GET'])
@handle_errors
@paginate()
def list_projects(page, limit, offset):
    """List all projects with pagination."""
    db = get_db()

    # Get total count
    count_result = db.execute(text("SELECT COUNT(*) FROM projects"))
    total = count_result.scalar()

    # Get paginated results
    result = db.execute(text("""
        SELECT id, project_number, name, client_name, status,
               start_date, end_date, budget, currency, created_at
        FROM projects
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """), {'limit': limit, 'offset': offset})

    projects = []
    for row in result:
        projects.append({
            'id': str(row[0]),
            'project_number': row[1],
            'name': row[2],
            'client_name': row[3],
            'status': row[4],
            'start_date': str(row[5]) if row[5] else None,
            'end_date': str(row[6]) if row[6] else None,
            'budget': float(row[7]) if row[7] else None,
            'currency': row[8],
            'created_at': str(row[9])
        })

    return jsonify({
        'data': projects,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200


@api_bp.route('/projects', methods=['POST'])
@handle_errors
def create_project():
    """Create a new project."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    db = get_db()

    # Generate project number
    result = db.execute(text("SELECT generate_sequence_number('project')"))
    project_number = result.scalar()

    # Insert project
    result = db.execute(text("""
        INSERT INTO projects (project_number, name, description, client_name,
                             status, start_date, end_date, budget, currency)
        VALUES (:project_number, :name, :description, :client_name,
                :status, :start_date, :end_date, :budget, :currency)
        RETURNING id, project_number, created_at
    """), {
        'project_number': project_number,
        'name': data['name'],
        'description': data.get('description'),
        'client_name': data.get('client_name'),
        'status': data.get('status', 'active'),
        'start_date': data.get('start_date'),
        'end_date': data.get('end_date'),
        'budget': data.get('budget'),
        'currency': data.get('currency', 'USD')
    })

    row = result.fetchone()
    db.commit()

    return jsonify({
        'message': 'Project created successfully',
        'data': {
            'id': str(row[0]),
            'project_number': row[1],
            'created_at': str(row[2])
        }
    }), 201


@api_bp.route('/projects/<project_id>', methods=['GET'])
@handle_errors
def get_project(project_id):
    """Get a specific project by ID."""
    db = get_db()

    result = db.execute(text("""
        SELECT id, project_number, name, description, client_name,
               status, start_date, end_date, budget, currency,
               location, is_iso_compliant, metadata, created_at, updated_at
        FROM projects WHERE id = :id
    """), {'id': project_id})

    row = result.fetchone()

    if not row:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({
        'data': {
            'id': str(row[0]),
            'project_number': row[1],
            'name': row[2],
            'description': row[3],
            'client_name': row[4],
            'status': row[5],
            'start_date': str(row[6]) if row[6] else None,
            'end_date': str(row[7]) if row[7] else None,
            'budget': float(row[8]) if row[8] else None,
            'currency': row[9],
            'location': row[10],
            'is_iso_compliant': row[11],
            'metadata': row[12],
            'created_at': str(row[13]),
            'updated_at': str(row[14])
        }
    }), 200


# ============================================
# VENDOR ENDPOINTS
# ============================================

@api_bp.route('/vendors', methods=['GET'])
@handle_errors
@paginate()
def list_vendors(page, limit, offset):
    """List all vendors with pagination."""
    db = get_db()

    # Filter parameters
    is_approved = request.args.get('is_approved')
    search = request.args.get('search')

    # Build query
    where_clauses = []
    params = {'limit': limit, 'offset': offset}

    if is_approved is not None:
        where_clauses.append("is_approved = :is_approved")
        params['is_approved'] = is_approved.lower() == 'true'

    if search:
        where_clauses.append(
            "(company_name ILIKE :search OR vendor_code ILIKE :search)"
        )
        params['search'] = f'%{search}%'

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Get total count
    count_result = db.execute(
        text(f"SELECT COUNT(*) FROM vendors {where_clause}"),
        params
    )
    total = count_result.scalar()

    # Get paginated results
    result = db.execute(text(f"""
        SELECT id, vendor_code, company_name, contact_person, email,
               phone, city, country, is_approved, rating, created_at
        FROM vendors
        {where_clause}
        ORDER BY company_name
        LIMIT :limit OFFSET :offset
    """), params)

    vendors = []
    for row in result:
        vendors.append({
            'id': str(row[0]),
            'vendor_code': row[1],
            'company_name': row[2],
            'contact_person': row[3],
            'email': row[4],
            'phone': row[5],
            'city': row[6],
            'country': row[7],
            'is_approved': row[8],
            'rating': float(row[9]) if row[9] else None,
            'created_at': str(row[10])
        })

    return jsonify({
        'data': vendors,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200


@api_bp.route('/vendors', methods=['POST'])
@handle_errors
def create_vendor():
    """Create a new vendor."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['company_name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    db = get_db()

    # Generate vendor code
    result = db.execute(text("SELECT generate_sequence_number('vendor')"))
    vendor_code = result.scalar()

    # Insert vendor
    result = db.execute(text("""
        INSERT INTO vendors (vendor_code, company_name, trade_name, contact_person,
                            email, phone, address, city, country, website,
                            tax_id, payment_terms, vendor_type, notes)
        VALUES (:vendor_code, :company_name, :trade_name, :contact_person,
                :email, :phone, :address, :city, :country, :website,
                :tax_id, :payment_terms, :vendor_type, :notes)
        RETURNING id, vendor_code, created_at
    """), {
        'vendor_code': vendor_code,
        'company_name': data['company_name'],
        'trade_name': data.get('trade_name'),
        'contact_person': data.get('contact_person'),
        'email': data['email'],
        'phone': data.get('phone'),
        'address': data.get('address'),
        'city': data.get('city'),
        'country': data.get('country'),
        'website': data.get('website'),
        'tax_id': data.get('tax_id'),
        'payment_terms': data.get('payment_terms'),
        'vendor_type': data.get('vendor_type'),
        'notes': data.get('notes')
    })

    row = result.fetchone()
    db.commit()

    return jsonify({
        'message': 'Vendor created successfully',
        'data': {
            'id': str(row[0]),
            'vendor_code': row[1],
            'created_at': str(row[2])
        }
    }), 201


# ============================================
# RFQ ENDPOINTS
# ============================================

@api_bp.route('/rfqs', methods=['GET'])
@handle_errors
@paginate()
def list_rfqs(page, limit, offset):
    """List all RFQs with pagination."""
    db = get_db()

    status = request.args.get('status')
    project_id = request.args.get('project_id')

    where_clauses = []
    params = {'limit': limit, 'offset': offset}

    if status:
        where_clauses.append("r.status = :status")
        params['status'] = status

    if project_id:
        where_clauses.append("r.project_id = :project_id")
        params['project_id'] = project_id

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Get total count
    count_result = db.execute(
        text(f"SELECT COUNT(*) FROM rfqs r {where_clause}"),
        params
    )
    total = count_result.scalar()

    # Get paginated results with summary
    result = db.execute(text(f"""
        SELECT r.id, r.rfq_number, r.title, r.status, r.issue_date,
               r.closing_date, r.currency, r.estimated_value,
               p.project_number, p.name as project_name,
               (SELECT COUNT(*) FROM rfq_items ri WHERE ri.rfq_id = r.id) as item_count,
               (SELECT COUNT(*) FROM quotations q WHERE q.rfq_id = r.id) as quotation_count,
               r.created_at
        FROM rfqs r
        LEFT JOIN projects p ON r.project_id = p.id
        {where_clause}
        ORDER BY r.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)

    rfqs = []
    for row in result:
        rfqs.append({
            'id': str(row[0]),
            'rfq_number': row[1],
            'title': row[2],
            'status': row[3],
            'issue_date': str(row[4]) if row[4] else None,
            'closing_date': str(row[5]) if row[5] else None,
            'currency': row[6],
            'estimated_value': float(row[7]) if row[7] else None,
            'project_number': row[8],
            'project_name': row[9],
            'item_count': row[10],
            'quotation_count': row[11],
            'created_at': str(row[12])
        })

    return jsonify({
        'data': rfqs,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200


@api_bp.route('/rfqs', methods=['POST'])
@handle_errors
def create_rfq():
    """Create a new RFQ."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['title']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    db = get_db()

    # Generate RFQ number
    result = db.execute(text("SELECT generate_sequence_number('rfq')"))
    rfq_number = result.scalar()

    # Insert RFQ
    result = db.execute(text("""
        INSERT INTO rfqs (rfq_number, title, description, project_id,
                         status, rfq_type, priority, issue_date, closing_date,
                         validity_days, delivery_location, currency, estimated_value,
                         terms_and_conditions, special_instructions)
        VALUES (:rfq_number, :title, :description, :project_id,
                :status, :rfq_type, :priority, :issue_date, :closing_date,
                :validity_days, :delivery_location, :currency, :estimated_value,
                :terms_and_conditions, :special_instructions)
        RETURNING id, rfq_number, created_at
    """), {
        'rfq_number': rfq_number,
        'title': data['title'],
        'description': data.get('description'),
        'project_id': data.get('project_id'),
        'status': data.get('status', 'draft'),
        'rfq_type': data.get('rfq_type', 'standard'),
        'priority': data.get('priority', 'normal'),
        'issue_date': data.get('issue_date'),
        'closing_date': data.get('closing_date'),
        'validity_days': data.get('validity_days', 30),
        'delivery_location': data.get('delivery_location'),
        'currency': data.get('currency', 'USD'),
        'estimated_value': data.get('estimated_value'),
        'terms_and_conditions': data.get('terms_and_conditions'),
        'special_instructions': data.get('special_instructions')
    })

    row = result.fetchone()
    db.commit()

    return jsonify({
        'message': 'RFQ created successfully',
        'data': {
            'id': str(row[0]),
            'rfq_number': row[1],
            'created_at': str(row[2])
        }
    }), 201


# ============================================
# QUOTATION ENDPOINTS
# ============================================

@api_bp.route('/quotations', methods=['GET'])
@handle_errors
@paginate()
def list_quotations(page, limit, offset):
    """List all quotations with pagination."""
    db = get_db()

    rfq_id = request.args.get('rfq_id')
    vendor_id = request.args.get('vendor_id')

    where_clauses = []
    params = {'limit': limit, 'offset': offset}

    if rfq_id:
        where_clauses.append("q.rfq_id = :rfq_id")
        params['rfq_id'] = rfq_id

    if vendor_id:
        where_clauses.append("q.vendor_id = :vendor_id")
        params['vendor_id'] = vendor_id

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Get results
    result = db.execute(text(f"""
        SELECT q.id, q.quotation_number, q.status, q.submission_date,
               q.total_amount, q.currency, q.overall_score, q.rank,
               v.company_name as vendor_name, r.rfq_number
        FROM quotations q
        LEFT JOIN vendors v ON q.vendor_id = v.id
        LEFT JOIN rfqs r ON q.rfq_id = r.id
        {where_clause}
        ORDER BY q.submission_date DESC
        LIMIT :limit OFFSET :offset
    """), params)

    quotations = []
    for row in result:
        quotations.append({
            'id': str(row[0]),
            'quotation_number': row[1],
            'status': row[2],
            'submission_date': str(row[3]) if row[3] else None,
            'total_amount': float(row[4]) if row[4] else None,
            'currency': row[5],
            'overall_score': float(row[6]) if row[6] else None,
            'rank': row[7],
            'vendor_name': row[8],
            'rfq_number': row[9]
        })

    return jsonify({'data': quotations}), 200


# ============================================
# PURCHASE ORDER ENDPOINTS
# ============================================

@api_bp.route('/purchase-orders', methods=['GET'])
@handle_errors
@paginate()
def list_purchase_orders(page, limit, offset):
    """List all purchase orders with pagination."""
    db = get_db()

    status = request.args.get('status')
    vendor_id = request.args.get('vendor_id')

    where_clauses = []
    params = {'limit': limit, 'offset': offset}

    if status:
        where_clauses.append("po.status = :status")
        params['status'] = status

    if vendor_id:
        where_clauses.append("po.vendor_id = :vendor_id")
        params['vendor_id'] = vendor_id

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Get total count
    count_result = db.execute(
        text(f"SELECT COUNT(*) FROM purchase_orders po {where_clause}"),
        params
    )
    total = count_result.scalar()

    # Get results
    result = db.execute(text(f"""
        SELECT po.id, po.po_number, po.status, po.po_date, po.delivery_date,
               po.total_amount, po.currency, v.company_name as vendor_name,
               p.project_number, po.created_at
        FROM purchase_orders po
        LEFT JOIN vendors v ON po.vendor_id = v.id
        LEFT JOIN projects p ON po.project_id = p.id
        {where_clause}
        ORDER BY po.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)

    purchase_orders = []
    for row in result:
        purchase_orders.append({
            'id': str(row[0]),
            'po_number': row[1],
            'status': row[2],
            'po_date': str(row[3]) if row[3] else None,
            'delivery_date': str(row[4]) if row[4] else None,
            'total_amount': float(row[5]) if row[5] else None,
            'currency': row[6],
            'vendor_name': row[7],
            'project_number': row[8],
            'created_at': str(row[9])
        })

    return jsonify({
        'data': purchase_orders,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200


# ============================================
# TBE EVALUATION ENDPOINTS
# ============================================

@api_bp.route('/tbe-evaluations', methods=['GET'])
@handle_errors
@paginate()
def list_tbe_evaluations(page, limit, offset):
    """List all TBE evaluations with pagination."""
    db = get_db()

    rfq_id = request.args.get('rfq_id')

    where_clauses = []
    params = {'limit': limit, 'offset': offset}

    if rfq_id:
        where_clauses.append("t.rfq_id = :rfq_id")
        params['rfq_id'] = rfq_id

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    result = db.execute(text(f"""
        SELECT t.id, t.evaluation_number, t.title, t.status,
               t.evaluation_date, r.rfq_number, v.company_name as selected_vendor,
               t.created_at
        FROM tbe_evaluations t
        LEFT JOIN rfqs r ON t.rfq_id = r.id
        LEFT JOIN vendors v ON t.selected_vendor_id = v.id
        {where_clause}
        ORDER BY t.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)

    evaluations = []
    for row in result:
        evaluations.append({
            'id': str(row[0]),
            'evaluation_number': row[1],
            'title': row[2],
            'status': row[3],
            'evaluation_date': str(row[4]) if row[4] else None,
            'rfq_number': row[5],
            'selected_vendor': row[6],
            'created_at': str(row[7])
        })

    return jsonify({'data': evaluations}), 200


@api_bp.route('/tbe-evaluations/<evaluation_id>/calculate', methods=['POST'])
@handle_errors
def calculate_tbe(evaluation_id):
    """Calculate TBE scores for all quotations."""
    from api.utils.tbe_calculator import TBECalculator

    calculator = TBECalculator()
    result = calculator.calculate_scores(evaluation_id)

    return jsonify({
        'message': 'TBE calculation completed',
        'data': result
    }), 200


# ============================================
# REPORT ENDPOINTS
# ============================================

@api_bp.route('/reports/dashboard', methods=['GET'])
@handle_errors
def dashboard_report():
    """Get dashboard summary data."""
    db = get_db()

    # Get counts
    result = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM projects WHERE status = 'active') as active_projects,
            (SELECT COUNT(*) FROM rfqs WHERE status = 'open') as open_rfqs,
            (SELECT COUNT(*) FROM purchase_orders WHERE status IN ('approved', 'sent')) as active_pos,
            (SELECT COUNT(*) FROM vendors WHERE is_approved = true) as approved_vendors,
            (SELECT COALESCE(SUM(total_amount), 0) FROM purchase_orders
             WHERE status NOT IN ('cancelled', 'draft')) as total_po_value,
            (SELECT COUNT(*) FROM quotations WHERE status = 'submitted'
             AND submission_date >= CURRENT_DATE - INTERVAL '7 days') as recent_quotations
    """))

    row = result.fetchone()

    return jsonify({
        'data': {
            'active_projects': row[0],
            'open_rfqs': row[1],
            'active_pos': row[2],
            'approved_vendors': row[3],
            'total_po_value': float(row[4]) if row[4] else 0,
            'recent_quotations': row[5]
        }
    }), 200


@api_bp.route('/reports/procurement-summary', methods=['GET'])
@handle_errors
def procurement_summary():
    """Get procurement summary report."""
    db = get_db()

    # Get date range from params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    params = {}
    date_filter = ""

    if start_date and end_date:
        date_filter = "WHERE po.po_date BETWEEN :start_date AND :end_date"
        params = {'start_date': start_date, 'end_date': end_date}

    result = db.execute(text(f"""
        SELECT
            COUNT(*) as total_orders,
            SUM(total_amount) as total_value,
            AVG(total_amount) as average_order_value,
            COUNT(DISTINCT vendor_id) as unique_vendors
        FROM purchase_orders po
        {date_filter}
    """), params)

    row = result.fetchone()

    return jsonify({
        'data': {
            'total_orders': row[0],
            'total_value': float(row[1]) if row[1] else 0,
            'average_order_value': float(row[2]) if row[2] else 0,
            'unique_vendors': row[3]
        }
    }), 200


# ============================================
# UTILITY ENDPOINTS
# ============================================

@api_bp.route('/units-of-measure', methods=['GET'])
@handle_errors
def list_units():
    """List all units of measure."""
    db = get_db()

    result = db.execute(text("""
        SELECT id, code, name, description
        FROM units_of_measure
        WHERE is_active = true
        ORDER BY code
    """))

    units = []
    for row in result:
        units.append({
            'id': str(row[0]),
            'code': row[1],
            'name': row[2],
            'description': row[3]
        })

    return jsonify({'data': units}), 200


@api_bp.route('/currencies', methods=['GET'])
@handle_errors
def list_currencies():
    """List all currencies."""
    db = get_db()

    result = db.execute(text("""
        SELECT id, code, name, symbol
        FROM currencies
        WHERE is_active = true
        ORDER BY code
    """))

    currencies = []
    for row in result:
        currencies.append({
            'id': str(row[0]),
            'code': row[1],
            'name': row[2],
            'symbol': row[3]
        })

    return jsonify({'data': currencies}), 200
