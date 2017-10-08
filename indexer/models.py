from django.core.urlresolvers import resolve
from django.db import models
import os

from django.utils.encoding import filepath_to_uri
from django.utils.http import urlsafe_base64_encode, urlencode


class Indexed(models.Model):
    """
    All hosts indexed
    """
    TAG = "models.Indexed"
    id = models.CharField(max_length=255, primary_key=True)
    # ftp_user = models.CharField(max_length=255)
    ftp_passw = models.CharField(max_length=255, null=True)
    # host = models.CharField(max_length=255)
    # init_indexing_path = models.CharField(max_length=255)
    dirs_count = models.IntegerField(default=0)
    files_count = models.IntegerField(default=0)

    def __str__(self):
        return self.id

    def update_cant_found(self, dirs_new_count, files_new_count, completed=True):
        if completed is True:  # si se completo el indexing, actualiza los datos actuales en db con los nuevos indexados
            self.dirs_count = dirs_new_count
            self.files_count = files_new_count
        if completed is False:  # no se completo el indexing
            # si la cant nueva indexada es mayor q la actual en db entonces se actualiza
            if files_new_count > self.files_count:
                self.files_count = files_new_count
            if dirs_new_count > self.dirs_count:
                self.dirs_count = dirs_new_count
        print(Indexed.TAG, "-upd to-", self.dirs_count, self.files_count)
        self.save()

    def get_indexed_params(self):
        """
        un id cotidiano puede ser: ftp://host/init/path@miuser
        aqui debemos diseccionar eso para obt los datos
        :return: {"host":host, "init_indexing_path":/init/path, "miuser":miuser}
        """
        url, ftp_user = self.id.split("@", maxsplit=1)
        url = url.replace("ftp://", "")
        try:
            host, init_indexing_path = url.split("/", maxsplit=1)
        except ValueError:
            host = url.split("/", maxsplit=1)[0]
            init_indexing_path = "/"
        return {"host": host, "init_indexing_path": init_indexing_path, "ftp_user": ftp_user}


class Files(models.Model):
    indexed = models.ForeignKey(Indexed)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    is_file = models.BooleanField()

    def __str__(self):
        return self.name

    def full_url(self):
        enc = filepath_to_uri(os.path.join(self.host, self.path, self.name))
        url = "ftp://%s" % enc
        return url
