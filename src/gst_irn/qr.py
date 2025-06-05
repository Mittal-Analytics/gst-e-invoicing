import segno


def get_qr_code_image_base64(message):
    qr = segno.make(message)
    return qr.png_data_uri(scale=2)


def get_qr_code_image_html(message, pixels=250):
    img_base64 = get_qr_code_image_base64(message)
    pixels = int(pixels)
    html = f'<img src="{img_base64}" style="width: {pixels}px; height: auto">'
    return html
