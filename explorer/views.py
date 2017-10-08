from django.shortcuts import render
from django.utils.encoding import python_2_unicode_compatible
from ftputil.error import FTPOSError, PermanentError
from rest_framework.views import APIView
from rest_framework.response import Response
from .ftp import FTP, FtpApiException, FtpShared
from rest_framework import status
import json


class List(APIView):
    # url -> http://127.0.0.1:8000/explorer/list/
    def post(self, request, format=None):
        # print("request",request.META)
        print(request.data)
        current_path = request.data.get("current_path", "/")
        print("explorer.view.List - current_path", current_path)
        host = request.data["host"]
        username = request.data.get("username", "Anonymous")
        password = request.data.get("password", None)
        ftp_id = request.data["ftp_id"]
        r = Response(content_type='application/json; charset=utf-8')
        try:
            f = FtpShared(ftp_id, current_path, host, username, password)
            print("explorer.view.List - f.current_path", f.ftp.current_path)
            res = f.ftp.dir_n_files()
            r.data = res
            return r
        except FtpApiException as e:
            r.data = e.message
            r.status_code = status.HTTP_400_BAD_REQUEST
            return r
        except PermanentError:
            print("Directory not found.")
            r.data = "Directory not found."
            r.status_code = status.HTTP_400_BAD_REQUEST
            return r
