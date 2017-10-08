import multiprocessing
import uuid

from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from explorer.ftp import FtpShared, FtpApiException
from indexer import serializers
from indexer.models import Files, Indexed
from rest_framework import generics


class Indexer(APIView):
    # url -> http://127.0.0.1:8000/indexer/index-it/
    TAG = "indexer.Indexer"
    currently_indexing = []

    def get(self, request):
        print(request.query_params)
        ftp_id = request.query_params["ftp_id"]
        try:
            ftp = FtpShared.cxn_dict[ftp_id]
            ftp.cancel()
            Indexer.currently_indexing.remove(ftp_id)
        except (KeyError, ValueError):
            return Response()
        return Response()

    def post(self, request):
        current_path = request.data["current_path"]
        host = request.data["host"]
        username = request.data.get("username", "Anonymous")
        password = request.data.get("password", None)
        cxn_id = request.data["ftp_id"]
        r = Response(content_type='application/json; charset=utf-8')
        try:
            f = FtpShared(cxn_id, current_path, host, username, password)
            if cxn_id in Indexer.currently_indexing:
                raise FtpApiException("El ftp %s@%s esta siendo indexado en estos momentos." % (host, username))
            Indexer.currently_indexing.append(cxn_id)
            indexed_dict = f.ftp.index_it()
            # esta linea debe ir primero q la de abajo, asi si se cancela la op se pueda mostrar cuanto se indexo hasta el momento de cancelar
            r.data = indexed_dict
            # lanza un ValueError cuando se cancela pq al cancelar tb se elimina de la lista el ftp_id
            Indexer.currently_indexing.remove(cxn_id)
            return r
        except ValueError:
            return r
        except FtpApiException as e:
            r.data = e.message
            r.status_code = status.HTTP_400_BAD_REQUEST
            return r
            # todo: separar este put para una nueva clase dedicada a upd y cancelar el upd
            # def put(self, request):
            #     """
            #     upd_id = {
            #         indexed_id = {
            #             cxn_id = str
            #             ftp = object
            #         },
            #         indexed_id = {
            #             cxn_id = str
            #             ftp = object
            #         },
            #         indexed_id = {
            #             cxn_id = str
            #             ftp = object
            #         }
            #         currently_updating = str->indexed_id
            #     },
            #     upd_id = {...}
            #     """
            #     print(request.data)
            #     upd_id = request.data["upd_id"]
            #     Indexer.currently_updating[upd_id] = {"currently_updating": str}
            #     for indexed_id in request.data["indexedSelected"]:
            #         #     print(Indexed.TAG, indexed_id)
            #         indexed = Indexed.objects.get(id=indexed_id)
            #         ftp_params = indexed.get_indexed_params()  # ->{"host": host, "init_indexing_path": init_indexing_path, "miuser": ftp_user}
            #         host = ftp_params["host"]
            #         init_indexing_path = ftp_params["init_indexing_path"]
            #         ftp_user = ftp_params["ftp_user"]
            #         #     print(host, init_indexing_path, ftp_user, indexed.ftp_passw)
            #         cxn_id = uuid.uuid1()
            #         f = FtpShared(cxn_id, init_indexing_path, host, ftp_user, indexed.ftp_passw)
            #         Indexer.currently_updating[upd_id][indexed_id] = {"cxn_id": cxn_id, "ftp": f}
            #     # print(Indexer.currently_updating[upd_id])
            #     for key, value in Indexer.currently_updating[upd_id].items():
            #         if key is "currently_updating": continue
            #         Indexer.currently_updating[upd_id]["currently_updating"] = key
            #         f = value["ftp"]
            #         f.ftp.index_it()
            #     return Response()


class UpdateIndexed(APIView):
    TAG = 'indexer.UpdateIndexed'
    currently_updating = {}

    def get(self, request):
        """
        obtener estado en q esta el proceso de updating. se estara haciendo peticion cada 5s.
        ex->{
            'currently_updating': 'ftp://localhost@doc',
            'ftp://localhost@Anonymous': {
                'ftp': <explorer.ftp.FtpShared object at 0x0000000004384630>,
                'done': True,
                'cxn_id': UUID('96aa69ac-b0da-11e6-b554-f8a963d28ac4')
            },
            'ftp://localhost@doc': {
                'ftp': <explorer.ftp.FtpShared object at 0x0000000004384CC0>,
                'done': False,
                'cxn_id': UUID('97465d38-b0da-11e6-b669-f8a963d28ac4')
            }
        }
        """
        try:
            client_id = request.query_params['client_id']
            currently_updating = UpdateIndexed.currently_updating[client_id]['currently_updating']
            # obtener todos los indexed_id que ya estan actualizados (done=True)
            # done = [key
            #         for key, value in UpdateIndexed.currently_updating[client_id].items()
            #         if value["done"]] --> da error pq la key 'currently_updating' no tiene otro dict de value
            done = []
            for key, value in UpdateIndexed.currently_updating[client_id].items():
                if key is 'currently_updating': continue
                if value["done"]: done.append(key)
            print(UpdateIndexed.TAG, "done_", done)
            return Response(content_type='application/json; charset=utf-8',
                            data={'currently_updating': currently_updating, 'done': done})
        except KeyError:
            return Response()

    def post(self, request):
        """
        client_id = {
            indexed_id = {
                cxn_id = str
                ftp = object
                done = False
            },
            indexed_id = {
                cxn_id = str
                ftp = object
                done = False
            },
            indexed_id = {
                cxn_id = str
                ftp = object
                done = False
            }
            currently_updating = str->indexed_id
        },
        client_id = {...}
        """
        r = Response()
        print(UpdateIndexed.TAG, '-post data-', request.data)
        client_id = request.data["upd_id"]
        UpdateIndexed.currently_updating[client_id] = {"currently_updating": ''}
        for indexed_id in request.data["indexedSelected"]:
            indexed = Indexed.objects.get(id=indexed_id)
            ftp_params = indexed.get_indexed_params()
            """
            ex ->{
                "host": 'mi.ftp.com',
                "init_indexing_path": 'init/indexing.path',
                "ftp_user": 'pepito'
            }
            """
            host = ftp_params["host"]
            init_indexing_path = ftp_params["init_indexing_path"]
            ftp_user = ftp_params["ftp_user"]
            cxn_id = uuid.uuid1()
            try:
                f = FtpShared(cxn_id, init_indexing_path, host, ftp_user, indexed.ftp_passw)
                updating_data = {
                    "cxn_id": cxn_id,
                    "ftp": f,
                    "done": False,
                    "files_count": 0,
                    "dirs_count": 0
                }
                UpdateIndexed.currently_updating[client_id][indexed_id] = updating_data
            except FtpApiException as e:
                r.data = e.message
                r.status_code = status.HTTP_400_BAD_REQUEST
                return r
        response_dict = {}
        for indexed_id, value in UpdateIndexed.currently_updating[client_id].items():
            if indexed_id is "currently_updating": continue
            updating_done = UpdateIndexed.currently_updating[client_id][indexed_id]["done"]
            if not updating_done:
                UpdateIndexed.currently_updating[client_id]["currently_updating"] = indexed_id
                f = value["ftp"]
                f.ftp.index_it()
                UpdateIndexed.currently_updating[client_id][indexed_id]["done"] = True
                print(UpdateIndexed.TAG, "terminando un job:", indexed_id,
                      UpdateIndexed.currently_updating[client_id][indexed_id])
            indexed = Indexed.objects.get(id=indexed_id)
            response_dict[indexed_id] = {'files_count': indexed.files_count, 'dirs_count': indexed.dirs_count}
        r.data = response_dict
        return r

    def put(self, request):
        """
        cancelar un proceso updating
        """
        client_id = request.data["client_id"]
        indexed_id = request.data["indexed_id"]
        currently_updating = UpdateIndexed.currently_updating[client_id]["currently_updating"]
        print(currently_updating == indexed_id, currently_updating, indexed_id)
        if currently_updating == indexed_id:  # -> ftp://localhost@doc == ftp://localhost@adri
            f = UpdateIndexed.currently_updating[client_id][indexed_id]["ftp"]
            f.ftp.cancel()
        else:
            UpdateIndexed.currently_updating[client_id][indexed_id]["done"] = True
        return Response()


class Search(APIView):
    # url -> http://127.0.0.1:8000/indexer/search/
    TAG = "indexer.Search"

    def get(self, format=None):
        q = Indexed.objects.all()
        s = serializers.IndexedSerializer(q, many=True)
        return Response(content_type='application/json; charset=utf-8', data=s.data)

    def post(self, request):
        # ex: request.data -> {'search': 'fra', 'indexedSelected': ['ftp://localhost@Anonymous', 'ftp://localhost/A@api']}
        search = request.data["search"]
        indexed_selected = request.data["indexedSelected"]
        if indexed_selected:
            q = Files.objects.filter(name__icontains=search, indexed__in=indexed_selected)
        else:
            q = Files.objects.filter(name__icontains=search)
        # html_as_str = render_to_string('partials/search_results.html', {"found": q})
        s = serializers.FilesSerializer(q, many=True)
        return Response(content_type='application/json; charset=utf-8', data=s.data)


class RemoveIndexedFtp(APIView):
    TAG = "Remove"

    def post(self, request):
        to_remove = request.data["toRemove"]
        if to_remove:
            Indexed.objects.filter(
                id__in=to_remove).delete()  # borra en cascada y por lo tanto todos los ficheros y directorios indexados q tengan relacion con estos obj
        # print(RemoveIndexedFtp.TAG, 72,request.data)
        else:
            print(RemoveIndexedFtp.TAG, "eliminar todo")
            Indexed.objects.all().delete()
        return Response()
