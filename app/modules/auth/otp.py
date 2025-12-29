import pyotp
import qrcode
import io
import base64

def generate_otp_secret() -> str:
    """Generates a random base32 formatted secret string."""
    return pyotp.random_base32()

def verify_otp_code(secret: str, code: str) -> bool:
    """Verifies a TOTP code against the secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_otp_provisioning_uri(secret: str, username: str, issuer_name: str = "FastAPI Template") -> str:
    """Generates the provisioning URI for the Authenticator app."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer_name)

def generate_qr_code_base64(provisioning_uri: str) -> str:
    """Generates a QR code image encoded in base64."""
    import qrcode.image.svg
    from io import BytesIO
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    # Use SVG factory to avoid PIL dependency
    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(image_factory=factory)
    
    buffered = BytesIO()
    img.save(buffered)
    
    # Return SVG base64 data URI
    return "data:image/svg+xml;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
