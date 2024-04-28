from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from flask import jsonify

from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)




@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    incoming_content = incoming_payload.get('content')

    # Check if content is null
    if incoming_content is None:
        return jsonify({'error': 'Bad Request', 'message': 'Content cannot be null'}), 400

    assignment = AssignmentSchema().load(incoming_payload)
    assignment.student_id = p.student_id

    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)

    # Check if the assignment with the given ID exists
    assignment = Assignment.query.filter_by(id=submit_assignment_payload.id, student_id=p.student_id).first()
    if not assignment:
        return jsonify({'error': 'Bad Request', 'message': 'Assignment not found'}), 400
    
    # Set the assignment state from the payload

    # Check if the assignment is in 'DRAFT' state
    if assignment.state != 'DRAFT':
        return jsonify({'error': 'FyleError', 'message': 'only a draft assignment can be submitted'}), 400

    # Assuming Assignment.submit() handles the submission process correctly
    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p
    )
    db.session.commit()
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)



