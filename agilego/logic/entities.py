import json
from flask import jsonify
from flask_restful import Resource, request
from na3x.db.data import Accessor, AccessParams
from na3x.utils.converter import Converter, Types
from na3x.validation.validator import Validator
from logic.constants import DbConstants, ParamConstants, MatchConstants

CFG_ALLOC_VALIDATION = './cfg/validation/allocation.json' # ToDo: load on start up


class Backlog(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {
                 AccessParams.OPERATOR_OR: [{ParamConstants.PARAM_TYPE: MatchConstants.TYPE_STORY},
                                        {ParamConstants.PARAM_TYPE: MatchConstants.TYPE_BUG}]}}))


class Sprint(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE}))


class SprintTimeline(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_TIMELINE,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_TIMELINE in found) else jsonify(found[ParamConstants.PARAM_TIMELINE]))


class ComponentList(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_COMPONENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_COMPONENT in found) else found[ParamConstants.PARAM_COMPONENT])


class GroupList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})


class EmployeeList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_EMPLOYEES,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})


class Group(Resource):
    def delete(self, group):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).delete(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM, AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {ParamConstants.PARAM_GROUP: group}}), 204

    def post(self, group=None):
        obj_group = request.get_json()
        employees = obj_group[ParamConstants.PARAM_EMPLOYEES] if ParamConstants.PARAM_EMPLOYEES in obj_group else []
        for employee in employees:
            employee[ParamConstants.PARAM_CAPACITY] = Converter.convert(employee[ParamConstants.PARAM_CAPACITY], Types.TYPE_INT)
        match_params = {ParamConstants.PARAM_GROUP: group if group else obj_group[ParamConstants.PARAM_GROUP]}
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: obj_group,
             AccessParams.KEY_MATCH_PARAMS: match_params}), 201


class AllocationtList(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ALLOCATIONS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI}))


class Allocation(Resource):
    def get(self, key, date, group, employee):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ALLOCATIONS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: key,
                 ParamConstants.PARAM_DATE: Converter.convert(date, Types.TYPE_DATE),
                 ParamConstants.PARAM_GROUP: group,
                 ParamConstants.PARAM_EMPLOYEE: employee}}))

    def post(self):
        allocation_details = request.get_json()
        allocation_details[ParamConstants.PARAM_WHRS] = Converter.convert(allocation_details[ParamConstants.PARAM_WHRS],
                                                                          Types.TYPE_FLOAT)
        allocation_details[ParamConstants.PARAM_DATE] = Converter.convert(allocation_details[ParamConstants.PARAM_DATE],
                                                                          Types.TYPE_DATE)

        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ALLOCATIONS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: allocation_details,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: allocation_details[
                     ParamConstants.PARAM_ITEM_KEY],
                 ParamConstants.PARAM_DATE: allocation_details[
                     ParamConstants.PARAM_DATE],
                 ParamConstants.PARAM_GROUP: allocation_details[
                     ParamConstants.PARAM_GROUP],
                 ParamConstants.PARAM_EMPLOYEE: allocation_details[
                     ParamConstants.PARAM_EMPLOYEE]}}), 201

    def delete(self, key, date, group, employee):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).delete(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ALLOCATIONS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: key,
                 ParamConstants.PARAM_DATE: Converter.convert(date, Types.TYPE_DATE),
                 ParamConstants.PARAM_GROUP: group,
                 ParamConstants.PARAM_EMPLOYEE: employee}}), 204


class AllocationValidation(Resource):
    def post(self):
        allocation_details = request.get_json()
        allocation_details[ParamConstants.PARAM_WHRS] = float(allocation_details[ParamConstants.PARAM_WHRS])  # ToDo: move typecast into configuration ?
        allocation_details[ParamConstants.PARAM_DATE] = Converter.convert(allocation_details[ParamConstants.PARAM_DATE],
                                                                          Types.TYPE_DATE)
        with open(CFG_ALLOC_VALIDATION) as validation_cfg_file:
            res = Validator(json.load(validation_cfg_file, strict=False)).validate(allocation_details) # ToDo: load once on start-up api
        return res, 200 # ToDo: move cfg to constructor/cache


class GanttTasks(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.GANTT_TASKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI}))


class GanttLinks(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.GANTT_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI}))


class ActualStatusDate(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.ACTUAL_DATE,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE}))


class PlanVsActualDiscrepencies(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.ACTUAL_DISCREPENCIES,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI}))
