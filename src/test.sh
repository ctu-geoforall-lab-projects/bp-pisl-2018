#!/bin/bash

curl "http://localhost:5000/wps?request=execute&service=WPS&identifier=process-no-output&datainputs=name=%27ciao%27&version=1.0.0"

curl "http://localhost:5000/wps?request=execute&service=WPS&identifier=processoneoutput&version=1.0.0&datainputs=db_section=db;poly_in=@xlink:href=http://localhost:5000/static/data/points.gml;buffer=10"
