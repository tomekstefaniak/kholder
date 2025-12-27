from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from cryptography.fernet import InvalidToken
import json

from .models import Key
from .utils.utils import *


# View to handle key list operations: list all keys, create new key
@csrf_exempt
def key_list(request) -> JsonResponse:
    try:
        # List all keys
        if request.method == "GET":
            # Retrieve all Key objects but exclude the binary `encrypted_key` field
            keys_qs = Key.objects.all()

            # Use `.values()` to select only JSON-serializable fields
            keys_list = list(keys_qs.values("label", "created_at", "updated_at"))
            return JsonResponse(keys_list, safe=False, status=200)

        # Create a new key
        elif request.method == "POST":
            try:
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Invalid JSON"}, status=400)

                # Extract and validate label field
                if "label" not in data:
                    return JsonResponse({"error": "Missing field: label"}, status=400)
                label = validate_label(data["label"])

                # Extract and validate decrypted_key field
                if "decrypted_key" not in data:
                    return JsonResponse({"error": "Missing field: decrypted_key"}, status=400)
                decrypted_key = validate_decrypted_key(data["decrypted_key"])

                # Extract and validate password field
                if "password" not in data:
                    return JsonResponse({"error": "Missing field: password"}, status=400)
                password = validate_password(data["password"])

                # Encrypt value and store the key
                encrypted_key = encrypt(decrypted_key, password)

                # Create and save the new Key object
                new_key_obj = Key(label=label, encrypted_key=encrypted_key)

                # Validate the object before saving
                try:
                    new_key_obj.full_clean()
                except ValidationError as e:
                    return JsonResponse({"error": str(e)}, status=400)
                
                new_key_obj.save()

                return JsonResponse({"message": "Key created successfully"}, status=201)

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Unsupported method
        else:
            return JsonResponse({"error": "Unsupported HTTP method"}, status=405)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# View to handle individual key operations: update, delete
@csrf_exempt
def key_detail(request, label: str) -> JsonResponse:
    try:
        # Update particular key by label
        if request.method == "PATCH":
            try:
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Invalid JSON"}, status=400)

                # Retrieve Key object by label
                try:
                    key_obj = Key.objects.get(label=label)
                except Key.DoesNotExist:
                    return JsonResponse({"error": "Key not found"}, status=404)

                # Update label if provided
                new_label = data.get("label")
                if new_label is not None:
                    # Check if new label already exists
                    if Key.objects.filter(label=new_label).exists():
                        return JsonResponse({"error": "Label already exists"}, status=400)
                    key_obj.label = new_label

                # Update encrypted_key if provided
                decrypted_key = data.get("decrypted_key")
                password = data.get("password")
                if decrypted_key is not None and password is not None:
                    key_obj.encrypted_key = encrypt(decrypted_key, password)

                # Validate the object before saving
                try:
                    key_obj.full_clean()
                except ValidationError as e:
                    return JsonResponse({"error": str(e)}, status=400)

                key_obj.save()

                return JsonResponse({"message": "Key updated successfully"}, status=200)

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Delete particular key by label
        elif request.method == "DELETE":
            # Retrieve Key object by label
            try:
                key_obj = Key.objects.get(label=label)
            except Key.DoesNotExist:
                return JsonResponse({"error": "Key not found"}, status=404)

            key_obj.delete()
            return JsonResponse({"message": "Key deleted successfully"}, status=200)

        # Unsupported method
        else:
            return JsonResponse({"error": "Unsupported HTTP method"}, status=405)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# View to handle key decryption and retrieval of the decrypted key
@csrf_exempt
def key_detail_decrypt(request, label: str) -> JsonResponse:
    try:
        # Get particular key by label
        if request.method == "POST":
            data = None
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            # Extract password field
            password = data.get("password")
            if password is None:
                return JsonResponse({"error": "Missing field: password"}, status=400)

            # Retrieve Key object by label
            try:
                key_detail = Key.objects.get(label=label)
            except Key.DoesNotExist:
                return JsonResponse({"error": "Key not found"}, status=404)
            
            # Convert Key object to dict and decrypt value, pop encrypted_key
            decrypted_key = None
            try:
                decrypted_key = decrypt(key_detail.encrypted_key, password)
            except InvalidToken as e:
                return JsonResponse({"error": "Invalid password or corrupted data"}, status=400)

            return JsonResponse({"decrypted_key": decrypted_key}, status=200)
        
        else:
            return JsonResponse({"error": "Unsupported HTTP method"}, status=405)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
