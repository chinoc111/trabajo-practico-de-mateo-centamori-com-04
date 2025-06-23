from django.db import models
from django.conf import settings


class Favourite(models.Model):
    # Detalles del pokemon.
    id = models.IntegerField(primary_key=True, blank=True) #ID de pokeapi
    name = models.CharField(max_length=200)  # Nombre del personaje
    height = models.CharField(max_length=200)  # Altura
    weight = models.CharField(max_length=200)  # Peso
    base_experience = models.IntegerField(null=True, blank=True)  # Experiencia base
    types = models.JSONField(default=list)  # Lista de tipos (ej: ["grass", "poison"])
    image = models.URLField()  # URL de la imagen

    # Asociamos el favorito con el usuario que lo guarda.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        # Restringe duplicados: un mismo usuario no puede guardar el mismo personaje varias veces.
        unique_together = (('user', 'name'),)

    def __str__(self):
        return (f"{self.name} - Altura: {self.height if self.height else 'Desconocida'} "
                f"(Peso: {self.weight if self.weight else 'Desconocido'}) - "
                f"User: {self.user.username}")

#es para agregar los favoritos 
def agregar_favorito(request):
    if request.method == 'POST':
        # Obtenemos datos del formulario
        poke_id = request.POST.get('id')
        name = request.POST.get('name')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        base_experience = request.POST.get('base_experience')
        types = request.POST.get('types')  # Aquí puede venir como JSON string, ver más abajo
        image = request.POST.get('image')

        import json
        try:
            types = json.loads(types)  # Convertir string JSON a lista
        except:
            types = []

        # Verificamos que no exista ya para evitar errores (por unique_together)
        if not Favourite.objects.filter(user=request.user, name=name).exists():
            Favourite.objects.create(
                id=poke_id,
                name=name,
                height=height,
                weight=weight,
                base_experience=base_experience if base_experience else None,
                types=types,
                image=image,
                user=request.user
            )
    return redirect('favoritos')
#requiere logear, es para borrar los favoritos 
def borrar_favorito(request):
    if request.method == 'POST':
        fav_id = request.POST.get('id')
        favorito = get_object_or_404(Favourite, id=fav_id, user=request.user)
        favorito.delete()
    return redirect('favoritos')
