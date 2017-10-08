import ftputil
import multiprocessing
from django.db import IntegrityError
from ftputil.error import FTPOSError, PermanentError, FTPError
from indexer.models import Files, Indexed


class FtpApiException(Exception):
    def __init__(self, message):
        self.message = message


class FTP(ftputil.FTPHost):
    TAG = "FTP"

    def __init__(self, current_path, host, user="Anonymous", passw=None):
        try:
            print("auntenticar en ftp", host, current_path, user, passw)
            ftputil.FTPHost.__init__(self, host, user, passw)
        except PermanentError:
            raise FtpApiException('Not logged in, user or password incorrect!')
        except FTPOSError:
            raise FtpApiException('Se ha intentado una operación de socket en un host no accesible')
        except FTPError:
            raise FtpApiException('Un error de conexion al ftp')
        except Exception as e:
            raise FtpApiException('Un error de conexion al ftp')
        print(user + " ha sido autenticado")
        self.host = host
        self.user = user
        self.root = current_path
        self.current_path = current_path
        self.cancel_indexing = False
        self.passw = passw
        self.indexed_dict = {"files_count": 0, "dirs_count": 0}

    def ls(self):
        try:
            # print("FTP - ls - listar dir en %s@%s:%s" % (self.current_path, self.user, self.passw))
            res = self.listdir(self.current_path)
            # print("ls",res)
            return res
        except WindowsError:
            raise FtpApiException("Se ha anulado una conexión establecida por el software en su equipo host")
        except (TimeoutError, FTPOSError) as e:
            error = "Se produjo un error durante el intento de conexión"
            print(e)
            print(error)
            raise FtpApiException(error)

    def dir_n_files(self):
        res = self.ls()
        dir_n_files_dict = {'dirs': [], 'files': []}
        for r in res:
            current_elem = self.current_path + r
            key = 'dirs' if self.path.isdir(current_elem) else 'files'
            dir_n_files_dict[key].append(r)
        print(dir_n_files_dict)
        return dir_n_files_dict

    def index_it(self):
        dirs_to_scan = [self.current_path]
        # print("dirs_to_scan", dirs_to_scan)
        not_found = []
        # id_ compuesto por el directorio en el q se inicia la busq y el usuario q la hace
        # id_ = ftp://miftp@miuser
        id_ = "ftp://{0}@{1}".format(self.path.normpath("{0}/{1}".format(self.host, self.current_path)),
                                     self.user)
        indexed, created = Indexed.objects.get_or_create(id=id_,
                                                         ftp_passw=self.passw)
        self.indexed_dict = {"files_count": 0, "dirs_count": 0}  # resetear siempre antes de iniciar el indexing
        while dirs_to_scan:
            if self.cancel_indexing:
                self.cancel_indexing = False
                print(FTP.TAG, "-canceling-indexed_dict", self.indexed_dict)
                indexed.update_cant_found(self.indexed_dict["dirs_count"],
                                          self.indexed_dict["files_count"],
                                          completed=False)
                return self.indexed_dict
            try:
                self.current_path = dirs_to_scan.pop()
                # print("current_path ", self.current_path)
                try:
                    for dir_ in self.ls():
                        new_path = self.path.join(self.current_path, dir_)
                        if self.path.isdir(new_path):
                            dirs_to_scan.append(new_path)
                            is_file = False
                            self.indexed_dict["dirs_count"] += 1
                        else:
                            is_file = True
                            self.indexed_dict["files_count"] += 1
                        Files.objects.get_or_create(
                            indexed=indexed,
                            host=self.host,
                            path=self.current_path,
                            name=dir_,
                            is_file=is_file
                        )
                except FtpApiException:
                    continue
                    #     # file_or_dir_not_found = "No se encontró el fichero o directorio: " + current_url
                    #     not_found.append(new_path)
            except FTPOSError:
                # si se produjera una desconexion una vez empezado el escaneo.
                # "No se pudo conectar al servidor, revise la conexión."
                indexed.update_cant_found(self.indexed_dict["dirs_count"],
                                          self.indexed_dict["files_count"],
                                          completed=False)
                raise FtpApiException("No se pudo conectar al servidor, revise la conexión.")
            except UnicodeError:
                continue

        indexed.update_cant_found(self.indexed_dict["dirs_count"],
                                  self.indexed_dict["files_count"])
        return self.indexed_dict

    def cancel(self):
        self.cancel_indexing = True


class FtpShared:
    cxn_dict = {}

    def __init__(self, cxn_id, current_path, host, user="Anonymous", passw=None):
        try:
            self.ftp = FtpShared.cxn_dict[cxn_id]
            self.ftp.current_path = current_path
            print("conexion ya establecida", cxn_id)
        except KeyError:
            print("estableciendo conexion:",host,current_path,user,passw)
            self.ftp = FTP(current_path, host, user, passw)
        FtpShared.cxn_dict[cxn_id] = self.ftp
        print("dict", FtpShared.cxn_dict)
        print("conexiones establecidas:", len(FtpShared.cxn_dict))

    @staticmethod
    def del_cxn(cxn_id):
        del FtpShared.cxn_dict[cxn_id]
