from flask import Blueprint, jsonify
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core import db  # Import the db instance

from .schema import AssignmentSchema, AssignmentGradeSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """
    Returns list of assignments.
    """
    assignments = Assignment.get_assignments_by_teacher(p.user_id)
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """
    Grade an assignment.
    """
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    assignment = Assignment.query.get(grade_assignment_payload.id)
    if not assignment:
        return jsonify({'error': 'Bad Request', 'message': 'Assignment not found'}), 400

    if assignment.state == AssignmentStateEnum.DRAFT:
        return jsonify({'error': 'Bad Request', 'message': 'Draft assignment cannot be graded'}), 400

    if assignment.teacher_id != p.user_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to grade this assignment'}), 403

    assignment.grade = grade_assignment_payload.grade
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()

    graded_assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=graded_assignment_dump)


@principal_assignments_resources.route('/assignments/regrade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p, incoming_payload):
    """
    Regrade an assignment.
    """
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    assignment = Assignment.query.get(grade_assignment_payload.id)
    if not assignment:
        return jsonify({'error': 'Bad Request', 'message': 'Assignment not found'}), 400

    if assignment.state != AssignmentStateEnum.GRADED:
        return jsonify({'error': 'Bad Request', 'message': 'Only graded assignments can be regraded'}), 400

    if assignment.teacher_id != p.user_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to regrade this assignment'}), 403

    assignment.grade = grade_assignment_payload.grade
    db.session.commit()

    graded_assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=graded_assignment_dump)


# You can add more routes and API endpoints as needed
