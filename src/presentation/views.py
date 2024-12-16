from asgiref.sync import sync_to_async
from django.shortcuts import render, redirect
from django.http import HttpResponse

from src.presentation.forms import PublicKeyForm
from src.infrastructure.yandex_api import AsyncYandexDiskClient
from src.business_logic.services import FileService

def index_view(request) -> HttpResponse:
    """
    View главной страницы
    """

    if request.method == 'POST':
        form = PublicKeyForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data['public_key']
            request.session['public_key'] = public_key
            return redirect('list_files')
        else:
            print("форма не валидна", form.errors)
    else:
        form = PublicKeyForm()
    return render(request, 'main_app/index.html', {'form': form})


async def list_files_view(request) -> HttpResponse:
    """
    View страницы с файлами
    """

    public_key = await sync_to_async(request.session.get)('public_key')
    if not public_key:
        return redirect('index')

    # Инициализация сервиса и клиента
    disk_client = AsyncYandexDiskClient()
    file_service = FileService(disk_client=disk_client)
    file_filter = await sync_to_async(request.GET.get)('filter', '')

    try:
        files_list = await file_service.get_filtered_files(public_key, file_filter)
    except Exception as e:
        return HttpResponse(f"Ошибка при получении списка: {e}", status=400)

    return render(request, 'main_app/list_files.html', {'files_list': files_list, 'current_filter': file_filter})


async def download_multiple_files_view(request) -> HttpResponse:
    """
    View для скачивания нескольких файлов и их архивации в ZIP.
    """

    if request.method == 'POST':
        public_key = await sync_to_async(request.session.get)('public_key')
        selected_files = await sync_to_async(request.POST.getlist)('selected_files')

        if not public_key or not selected_files:
            return HttpResponse("Не выбраны файлы для скачивания.", status=400)

        # Инициализация клиента и сервиса
        disk_client = AsyncYandexDiskClient()
        file_service = FileService(disk_client=disk_client)

        try:
            # Создаем архив с файлами
            zip_buffer = await file_service.create_files_archive(public_key, selected_files)
        except ValueError as e:
            return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse(f"Произошла ошибка: {e}", status=500)

        # Отдаем архив пользователю
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="files_archive.zip"'
        return response

    return redirect('list_files')

