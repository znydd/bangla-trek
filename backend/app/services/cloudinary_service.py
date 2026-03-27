import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

class CloudinaryService:
    @staticmethod
    def upload_image(file: UploadFile, folder: str = "bangla-trek/community") -> dict:
        """
        Uploads an image to Cloudinary and returns its URL and public_id.
        """
        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="image"
        )
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }

    @staticmethod
    def delete_image(public_id: str) -> bool:
        """
        Deletes an image from Cloudinary by its public_id.
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            # Log error but don't fail as this is best-effort
            print(f"Failed to delete image from Cloudinary: {e}")
            return False
