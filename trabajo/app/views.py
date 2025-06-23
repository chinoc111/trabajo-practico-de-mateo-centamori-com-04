
from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Favourite
import json
def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    images = services.getAllImages()
    
    if request.user.is_authenticated:
        favourite_list = Favourite.objects.filter(user=request.user).values_list('name', flat=True)
    else:
        favourite_list = []

    return render(request, 'home.html', {
        'images': images,
        'favourite_list': favourite_list
    })
# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '').strip()

    if name != '':
        images = services.filterByCharacter(name)  # ✅ Usás tu función

        favourite_list = []  # cargá favoritos si corresponde

        if len(images) == 0:
            return render(request, 'home.html', {
                'images': [],
                'favourite_list': [],
                'error_message': f"No se encontraron resultados para '{name}'"
            })

        return render(request, 'home.html', {
            'images': images,
            'favourite_list': favourite_list
        })

    else:
        return redirect('home')
# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    tipo = request.POST.get('type', '')
    if tipo != '':
        images = services.filterByType(tipo)  # ✅ LLAMADA A TU FUNCIÓN DE FILTRADO

        # Si usás favoritos, podés cargarlos desde BD o sesión. Si no, vacía:
        favourite_list = []  

        return render(request, 'home.html', {
            'images': images,
            'favourite_list': favourite_list
        })
    else:
        return redirect('home')
# Estas funciones se usan cuando el usuario está logueado en la aplicación.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            return redirect('home')  # cambiá por donde quieras redirigir después de registrarse
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})



@login_required
def getAllFavouritesByUser(request):
    favourites = Favourite.objects.filter(user=request.user)
    print("Favoritos del usuario:", favourites)
    return render(request, 'favourites.html', {'favourite_list': favourites})

@login_required
def saveFavourite(request):
    if request.method == 'POST':
        try:
            # Recibimos los datos del formulario
            poke_id = int(request.POST.get('id'))
            name = request.POST.get('name')
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            base_experience = request.POST.get('base') or 0
            types_raw = request.POST.get('types')
            image = request.POST.get('image')

            # Convertimos los tipos (si vienen en string tipo lista)
            types = json.loads(types_raw.replace("'", '"')) if types_raw else []

            # Guardamos el favorito si aún no está guardado para este usuario
            Favourite, created = Favourite.objects.get_or_create(
                user=request.user,
                name=name,
                defaults={
                    'id': poke_id,
                    'height': height,
                    'weight': weight,
                    'base_experience': base_experience,
                    'types': types,
                    'image': image,
                }
            )

            if created:
                messages.success(request, f"{name} fue agregado a tus favoritos.")
            else:
                messages.info(request, f"{name} ya está en tus favoritos.")

        except Exception as e:
            print("Error guardando favorito:", e)
            messages.error(request, "No se pudo agregar a favoritos.")

    return redirect('home')

@login_required
def deleteFavourite(request):
    if request.method == 'POST':
        fav_id = request.POST.get('id')
        try:
            fav = Favourite.objects.get(id=fav_id, user=request.user)
            fav.delete()
        except Favourite.DoesNotExist:
            pass
    return redirect('favoritos')
@login_required
def exit(request):
    logout(request)
    return redirect('index-page')


