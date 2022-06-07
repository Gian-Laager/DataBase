import datetime
import json
from json import JSONEncoder

import django.db
from django.db import models, OperationalError

from django.db import connection


# Create your models here.

class NoElementFound(Exception):
    def __init__(self, table, id):
        self.table = table
        self.id = id

    def __str__(self):
        return f"No element with id=\"{self.id}\" found in table: \"{self.table}\""


class TableFormatNotMatching(Exception):
    pass


def isInitialized(table: str):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT 1 FROM %s", table)
            return True
        except django.db.ProgrammingError:
            return False


def initTable(sqlQuery):
    try:
        with connection.cursor() as cursor:
            cursor.execute("create " + sqlQuery)
    except OperationalError as err:
        if err.args[0] == 1050:
            return
        else:
            raise err


class ResultType:
    def __init__(self, id: int, result_type: str, unit):
        self.id = id
        self.result_type = result_type
        self.unit = unit

    def __str__(self):
        return f"ResultType{{id: {self.id}, result_type: {self.result_type}, unit: {self.unit}}}"

    @staticmethod
    def init():
        Unit.init()

        sqlQuery = """table ResultType
(
    id          int auto_increment,
    result_type varchar(512) null,
    unit        int          null,
    constraint ResultType_pk
        primary key (id),
    constraint ResultType_Unit_id_fk
        foreign key (unit) references Unit (id)
);
"""
        initTable(sqlQuery)

    @staticmethod
    def get(requestedId: int):
        ResultType.init()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id as '_id', result_type as '_result_type', unit as '_unit' FROM ResultType where id=%s",
                str(requestedId))
            result = cursor.fetchone()
            requestedUnit = Unit.get(result[2])

            if result is None:
                raise NoElementFound("ResultType", str(requestedId))

            if len(result) < 3:
                raise TableFormatNotMatching()

            return ResultType(result[0], result[1], requestedUnit)

    @staticmethod
    def make(type, unit):
        return ResultType(None, type, Unit.get(unit))

    def insert(self):
        ResultType.init()
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO ResultType (result_type, unit) VALUES ('{self.result_type}', {self.unit.id})")


class Unit:
    def __init__(self, id: int, unit: str):
        self.id = id
        self.unit = unit

    def __str__(self):
        return f"Unit{{id: {self.id}, unit: {self.unit}}}"

    @staticmethod
    def init():
        # if not Person.isInitialized():
        sqlQuery = """table Unit
(
    `id`       int auto_increment,
    `unit`     varchar(512),
    constraint unit_pk
        primary key (id)
);
"""
        initTable(sqlQuery)

    @staticmethod
    def get(requestedId: int):
        Unit.init()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id as '_id', unit as '_unit' FROM Unit where id=%s",
                           str(requestedId))
            result = cursor.fetchone()

            if result is None:
                raise NoElementFound("Unit", str(requestedId))

            if len(result) < 2:
                raise TableFormatNotMatching()

            return Unit(result[0], result[1])

    @staticmethod
    def make(unit):
        return Unit(None, unit)

    def insert(self):
        Unit.init()
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO Unit(unit) VALUES ('{self.unit}')")


class MeasurementType:
    def __init__(self, id: int, unit: Unit, type: str):
        self.id = id
        self.unit = unit
        self.type = type

    def __str__(self):
        return f"MeasurementType{{id: {self.id}, unit: {self.unit.id}, type: {self.type}}}"

    @staticmethod
    def init():
        Unit.init()

        sqlQuery = """table MeasurementType
        (
            id          int auto_increment,
            type varchar(512) null,
            unit        int   null,
            constraint MeasurementType_pk
                primary key (id),
            constraint MeasurementType_Unit_id_fk
                foreign key (unit) references Unit (id)
        );
        """
        initTable(sqlQuery)

    @staticmethod
    def get(requestedId: int):
        MeasurementType.init()

        with connection.cursor() as cursor:
            cursor.execute("SELECT id as '_id', unit as '_unit', type as '_type' FROM MeasurementType where id=%s",
                           str(requestedId))
            result = cursor.fetchone()

            if result is None:
                raise NoElementFound("MeasurementType", str(requestedId))

            if len(result) < 3:
                raise TableFormatNotMatching()

            return MeasurementType(result[0], Unit.get(result[1]), result[2])

    @staticmethod
    def make(type, unit):
        return MeasurementType(None, Unit.get(unit), type)

    def insert(self):
        MeasurementType.init()
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO MeasurementType (`type`, unit) VALUES ('{self.type}', {self.unit.id})")


class Measurement:
    def __init__(self, id: int, bunch: int, type: MeasurementType, measurement: float, timestamp):
        self.id = id
        self.bunch = bunch
        self.type = type
        self.measurement = measurement
        self.timestamp = timestamp

    def __str__(self):
        return f"Measurement{{id: {self.id}, bunch: {self.bunch}, type: {self.type}, measurement: {self.measurement}, " \
               f"timestamp: {self.timestamp}}}"

    @staticmethod
    def init():
        MeasurementType.init()

        sqlQuery = """table Measurement
        (
            id          int auto_increment,
            bunch       int,
            type        int,
            measurement double,
            `timestamp` timestamp,
            constraint Measurement_pk
                primary key (id),
            constraint Measurement_MeasurementType_id_fk
                foreign key (type) references Unit (id)
        );
        """
        initTable(sqlQuery)

    @staticmethod
    def get(requestedId: int):
        MeasurementType.init()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id as '_id', bunch as '_bunch', type as '_type', measurement as '_measurement', "
                "`timestamp` as '_timestamp' FROM MeasurementType where id=%s",
                str(requestedId))
            result = cursor.fetchone()

            if result is None:
                raise NoElementFound("Measurement", str(requestedId))

            if len(result) < 5:
                raise TableFormatNotMatching()

            return Measurement(result[0], result[1], MeasurementType.get(result[2]), result[3], result[4])

    @staticmethod
    def make(bunch, type, measurement, timestamp):
        return Measurement(None, bunch, type, measurement, timestamp)

    def insert(self):
        Measurement.init()
        with connection.cursor() as cursor:
            print(self.timestamp)
            cursor.execute(f"INSERT "
                           f"INTO "
                           f"loginProject.Measurement(bunch, `type`, measurement, `timestamp`) "
                           f"VALUES({str(self.bunch)}, {str(self.type.id)}, {str(self.measurement)}, '{self.timestamp}-00:00:00');"
                           )


class Result:
    def __init__(self, id: int, measurement_bunch, type: ResultType, timestamp, name: str,
                 comment: str, result: float):
        self.id = id
        self.measurement_bunch = measurement_bunch
        self.type = type
        self.timestamp = timestamp
        self.name = name
        self.comment = comment
        self.result = result

    def __str__(self):
        return f"Result{{id: {self.id}, measurement_bunch: [" + \
               ", ".join(map(lambda m: m.__str__(), self.measurement_bunch)) + \
               f"], type: {self.type}, timestamp: {self.timestamp}, name: {self.name}, " \
               f"comment: {self.comment}, result: {self.result}}}"

    @staticmethod
    def init():
        Measurement.init()
        ResultType.init()

        sqlQuery = """table Result
        (
            id                  int auto_increment,
            measurement_bunch   int,
            type                int,
            `timestamp`         timestamp,
            name                varchar(512) null,
            comment             varchar(4096) null,
            result              double null,
            
            constraint Result_pk
                primary key (id),
            constraint Result_ResultType_id_fk
                foreign key (type) references ResultType (id)
        );
        """
        initTable(sqlQuery)

    @staticmethod
    def get(requestedId: int):
        Result.init()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Result where id=%s",
                str(requestedId))
            result = cursor.fetchone()

            if result is None:
                raise NoElementFound("Result", str(requestedId))

            if len(result) < 7:
                raise TableFormatNotMatching()

            cursor.execute(
                "SELECT * from Measurement where bunch=%s",
                str(result[2])
            )

            measurements = list(cursor.fetchall())
            measurements = list(
                map(lambda m: Measurement(m[0], m[1], MeasurementType.get(m[2]), m[3], m[4]), measurements))

            return Result(result[0], list(measurements), ResultType.get(result[2]), result[3], result[4],
                          result[5], result[6])

    @staticmethod
    def make(measurement_bunch, type: ResultType, timestamp, name: str,
             comment: str, result: float):
        return Result(None, measurement_bunch, type, timestamp, name, comment, result)

    def insert(self):
        Result.init()
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT "
                           f"INTO "
                           f"loginProject.Result(measurement_bunch, type, timestamp, name, comment, result) "
                           f"VALUES({self.measurement_bunch}, {self.type.id}, '{self.timestamp}-00:00:00', '{self.name}', '{self.comment}', {self.result}); "
                           )

    @staticmethod
    def getAll():
        Result.init()

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM Result")

            result = []

            for cid in cursor.fetchall():
                print(Result.get(cid[0]))
                result.append(Result.get(cid[0]))

            return result


class DefaultJsonEncode(JSONEncoder):
    def default(self, o):
        if type(o) is datetime.datetime:
            return o.__str__()

        return o.__dict__
