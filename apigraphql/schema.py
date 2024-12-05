import graphene
from graphene_django import DjangoObjectType

from ingredients.models import Category, Ingredient

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")

class Query(graphene.ObjectType):
    all_ingredients = graphene.List(IngredientType)
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    def resolve_all_ingredients(root, info):
        return Ingredient.objects.select_related("category").all() #it is a join query (select_related)
    
    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None

class IngredientCreateMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required = True)
        notes = graphene.String()
        category = graphene.Int()

    ingredient = graphene.Field(IngredientType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, notes, category):
        try:
            category_data = Category.objects.get(id = category)
        except:
            return IngredientCreateMutation(message="Category not found", ingredient=None)
            # raise ValueError("Category not found")
        
        new_ingredient = Ingredient.objects.create(
            name=name,
            notes=notes,
            category=category_data
        )
        return IngredientCreateMutation(message = "create data success", ingredient = new_ingredient)

class IngredientUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        notes = graphene.String()
        category = graphene.Int()
    
    ingredient = graphene.Field(IngredientType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id, name = None, notes = None, category = None):
        try:
            ingredient = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            return IngredientUpdateMutation(ingredient = None, message = "Ingredient with ID %s not found" %id)
        
        if name is not None:
            ingredient.name = name
        if notes is not None:
            ingredient.notes = notes
        if category is not None:
            try:
                 category_data = Category.objects.get(id = category)
            except Category.DoesNotExist:
                return IngredientUpdateMutation(message="Category not found", ingredient=None)
            ingredient.category = category_data
       
        ingredient.save()
        return IngredientUpdateMutation(ingredient = ingredient, message = "Update success")

class IngredientDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required = True)
   
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            ingredient = Ingredient.objects.get(pk = id)
        except Ingredient.DoesNotExist:
            return IngredientDeleteMutation(message="Ingredient with ID %s is not found" %id)
        ingredient.delete()
        
        return IngredientDeleteMutation(message="Ingredient with ID %s is successfully deleted" %id)

class Mutation(graphene.ObjectType):
    create_ingredient = IngredientCreateMutation.Field()
    update_ingredient = IngredientUpdateMutation.Field()
    delete_ingredient = IngredientDeleteMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)