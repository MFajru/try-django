from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="ingredients")

    def __str__(self):
        return self.name
    
