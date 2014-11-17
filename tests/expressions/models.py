"""
Tests for F() query expression syntax.
"""

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Employee(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)

    def __str__(self):
        return '%s %s' % (self.firstname, self.lastname)


@python_2_unicode_compatible
class Company(models.Model):
    name = models.CharField(max_length=100)
    num_employees = models.PositiveIntegerField()
    num_chairs = models.PositiveIntegerField()
    ceo = models.ForeignKey(
        Employee,
        related_name='company_ceo_set')
    point_of_contact = models.ForeignKey(
        Employee,
        related_name='company_point_of_contact_set',
        null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Number(models.Model):
    integer = models.BigIntegerField(db_column='the_integer')
    float = models.FloatField(null=True, db_column='the_float')

    def __str__(self):
        return '%i, %.3f' % (self.integer, self.float)


class Experiment(models.Model):
    name = models.CharField(max_length=24)
    assigned = models.DateField()
    completed = models.DateField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ('name',)

    def duration(self):
        return self.end - self.start


class Article(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)

class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article)
    lang = models.CharField(max_length=4)
    title = models.CharField(max_length=100)
    body = models.TextField()

@python_2_unicode_compatible
class ShopUser(models.Model):
    username = models.CharField(max_length=60)

    def __str__(self):
        return 'ShopUser(username=%s)' % self.username


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return 'Product(name=%s, price=%s)' % (self.name, self.price)


@python_2_unicode_compatible
class SpecialPrice(models.Model):
    product = models.ForeignKey(Product)
    user = models.ForeignKey(ShopUser)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return 'SpecialPrice(price=%s)' % self.price