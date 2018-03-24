import json
import logging.config
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from na3x.utils.json import ExtJSONEncoder
from logic.constants import RestConstants
from logic.entities import Sprint, Backlog, SprintTimeline, ComponentList, GroupList, EmployeeList, Group, \
    AssignmentList, SubtaskList, Assignment, AssignmentValidation, GanttTasks, GanttLinks, ActualStatusDate, \
    PlanVsActualDiscrepencies
from na3x.cfg import init

CFG_LOG_API = './cfg/log/api-logging-config.json'
CFG_NA3X = './cfg/na3x.json'

app = Flask(__name__)
app.json_encoder = ExtJSONEncoder
with open(CFG_LOG_API) as log_cfg_file:
    logging.config.dictConfig(json.load(log_cfg_file, strict=False))
with open(CFG_NA3X) as na3x_cfg_file:
    init(json.load(na3x_cfg_file, strict=False))

api = Api(app)
CORS(app)

api.add_resource(Sprint, RestConstants.ROUTE_SPRINT)
api.add_resource(SprintTimeline, RestConstants.ROUTE_SPRINT_TIMELINE)
api.add_resource(Backlog, RestConstants.ROUTE_BACKLOG)
api.add_resource(SubtaskList, '{}/<task_key>{}'.format(RestConstants.ROUTE_TASK, RestConstants.ROUTE_SUBTASKS))
api.add_resource(ComponentList, RestConstants.ROUTE_COMPONENTS)
api.add_resource(GroupList, RestConstants.ROUTE_TEAM)
api.add_resource(EmployeeList, RestConstants.ROUTE_EMPLOYEES)
api.add_resource(Group, RestConstants.ROUTE_GROUP, '{}/<group>'.format(RestConstants.ROUTE_GROUP))
api.add_resource(AssignmentList, RestConstants.ROUTE_ASSIGNMENTS)
api.add_resource(Assignment, RestConstants.ROUTE_ASSIGNMENT,
                 '{}/<key>,<date>,<group>,<employee>'.format(RestConstants.ROUTE_ASSIGNMENT))
api.add_resource(AssignmentValidation, RestConstants.ROUTE_ASSIGNMENT_VALIDATION)
api.add_resource(GanttTasks, RestConstants.ROUTE_GANTT_TASKS)
api.add_resource(GanttLinks, RestConstants.ROUTE_GANTT_LINKS)
api.add_resource(ActualStatusDate, RestConstants.ROUTE_ACTUAL_DATE)
api.add_resource(PlanVsActualDiscrepencies, RestConstants.ROUTE_ACTUAL_DISCREPENCIES)

