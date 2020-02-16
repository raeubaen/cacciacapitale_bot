from django.db import models

class Bot(models.Model):
    id = models.IntegerField(
        unique=True, primary_key=True, default=1
    )  # to be sure there's only one instance of the model
    token = models.CharField(max_length=70, null=True)
    admin_id = models.IntegerField(null=True)
    max_team_size = models.IntegerField(null=True)
    def save(self, *args, **kwargs):
        if self._state.adding and self.__class__.objects.exists():
            raise T.exceptions.UniqueObjectError(
                f"There can be only one {self.__class__.__name__} instance"
            )
        super().save(*args, **kwargs)

class Key(models.Model):
  key = models.CharField(max_length=50)

  def __str__(self):
    return self.key


class Person(models.Model):
  id = models.IntegerField(primary_key=True)

  class Meta:
    abstract = True


class Captain(Person):
  anagraphic = models.CharField(max_length=100, null=True)

  def __str__(self):
    return self.anagraphic


class Hunter(Person):
  name = models.CharField(max_length=50, null=True)
  phone = models.CharField(max_length=15, null=True)
  surname = models.CharField(max_length=50, null=True)
  age = models.IntegerField(null=True)
  uni = models.CharField(max_length=50, null=True)
  tframe = models.CharField(max_length=50, null=True)
  perc = models.IntegerField(null=True)
  captain = models.ForeignKey(
    Captain,
    on_delete=models.CASCADE,
    null=True,
    blank=True
  )

  def __str__(self):
    return f"{self.name} {self.surname}"


class Queue(models.Model):
  situation = models.CharField(max_length=30, null=True)
  hunter = models.OneToOneField(
    Hunter,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    parent_link = True
  )

  def __str__(self):
    s = f"{self.situation}\n" + ", ".join(map(str, self.node_set.all()))
    return s


class Node(models.Model):
  queue = models.ForeignKey(
    Queue,
    on_delete=models.CASCADE,
    null=True,
    blank=True
  )
  captain = models.OneToOneField(
    Captain,
    on_delete=models.CASCADE,
    null=True,
    blank=True
  )
  status = models.CharField(max_length=20, null=True)
  number = models.IntegerField(null=True)

  def __str__(self):
    return f"({self.captain.anagraphic}: {self.status})"
