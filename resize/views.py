from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os
import zipfile
from io import BytesIO
from django.http import HttpResponse


def upload_images(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')  # Get list of uploaded images
        uploaded_images = []  # List to hold file URLs after upload
        image_names = []  # List to hold image names after upload

        fs = FileSystemStorage()

        for image in images:
            img = Image.open(image)

            # Ensure the 'resized' folder exists
            resized_dir = os.path.join(settings.MEDIA_ROOT, 'images/resized')
            if not os.path.exists(resized_dir):
                os.makedirs(resized_dir)

            resized_image_path = os.path.join(resized_dir, image.name)

            # Save the image with a high initial quality
            quality = 100
            img.save(resized_image_path, quality=quality, optimize=True)

            # Resize if necessary to get file size to 50KB or lower
            while os.path.getsize(resized_image_path) > 50 * 1024:
                max_dimension = max(img.width, img.height) - 100
                new_size = (int(img.width * max_dimension / max(img.width, img.height)),
                            int(img.height * max_dimension / max(img.width, img.height)))
                img = img.resize(new_size, Image.LANCZOS)
                img.save(resized_image_path, quality=quality, optimize=True)

            # Add image URL and name
            uploaded_images.append(fs.url(os.path.join('images/resized', image.name)))
            image_names.append(image.name)

        return render(request, 'resize/upload.html', {'uploaded_images': uploaded_images, 'image_names': image_names})

    return render(request, 'resize/upload.html')




def download_images(request):
    # The 'images/resized' folder inside MEDIA_ROOT where the resized images are saved
    image_folder = 'images/resized/'  # This is the correct folder

    # List all files in the 'images/resized' folder
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, image_folder))
    uploaded_images = fs.listdir('')[1]  # This lists all the files (ignore folders if any)

    # DEBUG: Print the list of uploaded images
    print("Uploaded images: ", uploaded_images)

    # Create an in-memory ZIP file
    zip_subdir = "images"
    zip_filename = f"{zip_subdir}.zip"
    s = BytesIO()

    with zipfile.ZipFile(s, "w") as zf:
        for image in uploaded_images:
            # Get the actual file path
            file_path = os.path.join(settings.MEDIA_ROOT, image_folder, image)

            # DEBUG: Check if the file exists
            if os.path.exists(file_path):
                print(f"File found: {file_path}")
            else:
                print(f"File not found: {file_path}")

            # Ensure it's a file and not a directory
            if os.path.isfile(file_path):
                # Add the image to the ZIP file under the 'images' folder
                zf.write(file_path, f"{zip_subdir}/{image}")
            else:
                print(f"Skipping non-file: {file_path}")  # DEBUG: If it's not a file

    # Set the response headers to serve the ZIP file
    response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    response['Content-Length'] = s.tell()

    return response
