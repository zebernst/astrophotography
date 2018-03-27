import hashlib
import io
from pathlib import Path

from PIL import Image as PImage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify

from core.models import Commander, Location, Waypoint
from distantworlds2.settings.base import SITE_ROOT


# todo: make success_url go to the Location form that pre-populates from filename
class Image(LoginRequiredMixin, models.Model):

    def user_media_folder(self, filename):
        """return the media folder for a certain user"""
        self.orig_filename = filename
        if self.owner:
            return 'uploads/{}/{}'.format(slugify(self.owner.cmdr_name), filename)  # self.owner.cmdr_name
        else:
            return 'uploads/anonymous/{}'.format(filename)

    def waypoint_folder(self, filename):
        # save original filename
        self.orig_filename = filename

        # todo: parse filename for system info

        cmdr = slugify('Anonymous' if self.owner.cmdr_name is None else self.owner.cmdr_name)
        wp = slugify('Misc' if self.waypoint is None else self.waypoint.abbrev)

        return 'uploads/{wp}/{cmdr}_{f}'.format(wp=wp, cmdr=cmdr, f=filename)

    # id is automatic

    # utility fields
    sha1sum = models.CharField(unique=True, max_length=40, blank=True, editable=False)

    # filesystem
    image = models.ImageField(upload_to=waypoint_folder, height_field='img_height', width_field='img_width')  # todo: use django-imagekit for processing photos (https://github.com/matthewwithanm/django-imagekit/)

    orig_filename = models.CharField('original filename', max_length=768)
    upload_date = models.DateTimeField('date uploaded', auto_now_add=True)

    # image meta
    img_height = models.IntegerField('image height')
    img_width = models.IntegerField('image width')

    # expedition meta
    desc = models.CharField('description', max_length=768, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    waypoint = models.ForeignKey(Waypoint, on_delete=models.SET_NULL, null=True, blank=True)

    # user
    owner = models.ForeignKey(Commander, on_delete=models.SET_NULL, null=True)

    # image uses
    public = models.BooleanField('display publicly', default=False)
    edited = models.BooleanField('edited', default=False)

    # imgur
    imgur_url = models.CharField('link to imgur upload', max_length=512, null=True, blank=True)
    del_hash = models.CharField('imgur deletion hash', max_length=512, null=True, blank=True)

    # internal use
    processed = models.BooleanField('processed by image utilities', default=False)

    # todo: when creating LocationForm, auto-populate from parsed image filename

    # todo: add "validated" field and create script to manually approve and then upload to imgur

    def save(self, *args, **kwargs):

        # if file is new, store sha1sum (important that the sha1sum is calculated BEFORE watermarking images)
        if not self.pk:
            sha1 = hashlib.sha1()
            for chunk in self.image.chunks():
                sha1.update(chunk)
            self.sha1sum = sha1.hexdigest()

        if not self.processed:
            # open image in pillow for editing
            orig_path = self.image.path
            img = PImage.open(self.image.file).convert('RGB')

            w, h = img.size

            # resize if greater than 4k
            resize_factor = 1  # default
            if w > 3840:
                resize_factor = 3840 / float(w)
                w_new = 3840
                h_new = round(h * resize_factor)
                img = img.resize((w_new, h_new))

            # ... do stuff

            # watermark
            wmk = PImage.open(str(SITE_ROOT/'static/watermark_margin.png'))
            wmk_ratio = wmk.size[0] / 3840

            wmk_w = wmk_ratio * img.size[0]
            wmk_resize_factor = wmk_w / float(wmk.size[0])
            wmk_h = wmk_resize_factor * wmk.size[1]
            wmk = wmk.resize((round(wmk_ratio * img.size[0]), round(wmk_h)))

            pos = [img.size[i] - wmk.size[i] for i in [0, 1]]

            img.paste(wmk, box=pos, mask=wmk)

            # font = ImageFont.truetype(str(SITE_ROOT/'static/fonts/Cambay-Regular.ttf'), 22)
            # textlayer = PImage.new('RGBA', img.size)
            # draw = ImageDraw.Draw(textlayer)
            # textsize = draw.textsize("Distant Worlds", font=font)
            # textpos = [(img.size[i]) - (textsize[i]) - margin[i] for i in [0, 1]]
            # draw.text(textpos, "Distant Worlds", font=font)
            # watermask = textlayer.convert("L").point(lambda x: min(x, 200))
            # textlayer.putalpha(watermask)
            #
            # img.paste(textlayer, None, textlayer)

            # open output stream and save image
            stream = io.BytesIO()
            img.save(stream, format='jpeg', quality=95)

            # create new django file wrapper for image
            self.image = InMemoryUploadedFile(file=stream, field_name='image',
                                              name=Path(orig_path).with_suffix('.jpg'),
                                              content_type='image/jpeg', size=stream.getbuffer().nbytes,
                                              content_type_extra=None, charset=None)

            # mark image as processed
            self.processed = True

            # save changes to db
            super(Image, self).save(*args, **kwargs)


# delete the image file when the Image instance is deleted by the admin panel.
@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    instance.image.delete(False)  # pass False to ensure that a save() isn't called.

# todo: for upload template, make 'file' and 'url' tabs and use ajax to rewrite the page accordingly

