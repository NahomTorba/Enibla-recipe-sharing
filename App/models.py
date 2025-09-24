from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image


# Create your models here.

