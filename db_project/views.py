import json

from json2html import *
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
import db_project.models
from db_project.models import *


def toHtml(obj):
    return json2html.convert(json.dumps(obj, cls=db_project.models.DefaultJsonEncode))


def index(request):
    return HttpResponse(toHtml(
        Result.getAll()) + '<br><a href="/form">add new results</a><br><a href="/get">get result with id (add id "/get/*id*")</a>')


def get(request):
    id = int(request.path.split('/')[2])
    return HttpResponse(toHtml(Result.get(id)))


def form(request):
    return render(request, "form.html")


def addResult(request):
    print(request.body)
    if request.method == "POST":
        jsonResult = json.loads(request.body)

        measurements = []

        lastBunch = 0
        with connection.cursor() as cursor:
            cursor.execute("SELECT measurement_bunch FROM Result ORDER BY measurement_bunch DESC")
            m_bunch = cursor.fetchone()
            if not m_bunch[0] is None:
                lastBunch = m_bunch[0]

            cursor.execute("SELECT bunch FROM Measurement ORDER BY bunch DESC")
            bunch = cursor.fetchone()
            if not bunch[0] is None:
                lastBunch = max(bunch[0], lastBunch)

        for measurement in jsonResult["measurements"]:
            measurements.append(
                Measurement.make(lastBunch + 1, MeasurementType.get(measurement["type"]),
                                 measurement["measurement"], measurement["timestamp"]))

        for m in measurements:
            m.insert()

        result = Result.make(lastBunch + 1, ResultType.get(jsonResult["type"]), jsonResult["timestamp"],
                             jsonResult["name"], jsonResult["comment"], jsonResult["result"])

        result.insert()

        return HttpResponse("OK")
    return HttpResponse("This url only accepts POSTs", status=403)


def addUnit(request):
    jsonUnit = json.loads(request.body)
    if request.method == "POST":
        newUnit = Unit.make(jsonUnit["unit"])
        newUnit.insert()

        return HttpResponse("OK")
    return HttpResponse("This url only accepts POSTs", status=403)


def addResultType(request):
    jsonUnit = json.loads(request.body)
    if request.method == "POST":
        newType = ResultType.make(jsonUnit["type"], jsonUnit["unit"])
        newType.insert()

        return HttpResponse("OK")
    return HttpResponse("This url only accepts POSTs", status=403)


def addMeasurementType(request):
    jsonUnit = json.loads(request.body)
    if request.method == "POST":
        newType = MeasurementType.make(jsonUnit["type"], jsonUnit["unit"])
        newType.insert()

        return HttpResponse("OK")
    return HttpResponse("This url only accepts POSTs", status=403)
