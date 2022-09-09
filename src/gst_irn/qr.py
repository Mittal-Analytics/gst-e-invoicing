import base64
from io import BytesIO

import qrcode


def _pil_to_base64(pil_img):
    output = BytesIO()
    pil_img.save(output, format="PNG")
    img = output.getvalue()

    # encode to base64
    img = base64.b64encode(img)
    img = "data:image/png;base64," + img.decode()
    return img


def get_qr_code_image_base64(message):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return _pil_to_base64(img)
