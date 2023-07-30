from django.contrib import messages
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.views import View
import qrcode
import io
import base64
from PIL import Image

def home(request):
    return render(request, 'gimics/home.html')

class QRCodeView(View):
    def get(self, request):
        return render(request, 'gimics/generator.html')

    def post(self, request):
        if 'generator' in request.POST:
            qr_input = request.POST.get('qr_input', '').strip()  # Remove leading/trailing spaces
            qr_image = request.FILES.get('qr_image')
            qr_color = request.POST.get('qr_color', '').strip()  # Get the selected QR code color
            qr_logo = request.FILES.get('qr_logo')  # Get the uploaded logo

            if not qr_input and not qr_image:
                # Display an error message
                messages.error(request, "Please enter text or upload an image to generate a QR code.")
                return render(request, 'gimics/generator.html')

            if qr_image:
                # Save the uploaded image
                filename = default_storage.save(qr_image.name, qr_image)
                qr_image_path = default_storage.path(filename)

                # Generate QR code from the uploaded image
                img = qrcode.make(qr_image_path)

            else:  # If no image is uploaded, generate QR code from input data
                if qr_input.startswith('http://') or qr_input.startswith('https://'):
                    qr_data = qr_input
                else:
                    qr_data = qr_input.encode()

                img = qrcode.make(qr_data)

            # Customize the QR code color if provided
            if qr_color:
                img = img.convert("RGB")
                qr_color = tuple(int(qr_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
                data = img.getdata()
                new_data = []
                for item in data:
                    if item[:3] == (0, 0, 0):
                        new_data.append(qr_color)
                    else:
                        new_data.append(item)
                img.putdata(new_data)

            # Convert PIL Image to BytesIO
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Convert BytesIO to base64 string
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return render(request, 'gimics/generator_result.html', {'qr_image_base64': qr_image_base64, 'qr_color': qr_color, 'qr_logo': qr_logo})

        return render(request, 'gimics/generator.html')