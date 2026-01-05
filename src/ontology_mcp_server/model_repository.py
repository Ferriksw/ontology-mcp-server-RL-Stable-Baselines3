import os
import hashlib
import json
from datetime import datetime

class ModelRepository:
    def __init__(self, storage_dir, strategy_model):
        """
        Initialize the Model Repository.

        :param storage_dir: Directory to store models.
        :param strategy_model: Callable strategy model for validation.
        """
        self.storage_dir = storage_dir
        self.strategy_model = strategy_model
        os.makedirs(self.storage_dir, exist_ok=True)
        self.metadata_file = os.path.join(self.storage_dir, "model_metadata.json")
        self.models = self._load_metadata()

    def _load_metadata(self):
        """Load existing metadata from file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.models, f, indent=4)

    def _generate_hash(self, file_path):
        """Generate SHA256 hash for a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def store_model(self, model_path, model_name):
        """
        Store a new model in the repository.

        :param model_path: Path to the model file.
        :param model_name: Name of the model.
        :return: Result dictionary.
        """
        if not os.path.exists(model_path):
            return {"success": False, "message": "Model file does not exist."}

        model_hash = self._generate_hash(model_path)
        timestamp = datetime.now().isoformat()

        # Check if model already exists
        if model_name in self.models:
            if self.models[model_name]["hash"] == model_hash:
                return {
                    "success": True,
                    "hash": model_hash,
                    "message": "Model already stored.",
                }

        # Store the model
        stored_path = os.path.join(self.storage_dir, model_name)
        os.replace(model_path, stored_path)
        self.models[model_name] = {
            "hash": model_hash,
            "stored_at": timestamp,
        }
        self._save_metadata()

        return {
            "success": True,
            "hash": model_hash,
            "message": "Model stored successfully.",
        }

    def verify_model(self, model_name):
        """
        Verify if the model has been modified.

        :param model_name: Name of the model.
        :return: Verification result.
        """
        if model_name not in self.models:
            return {"success": False, "message": "Model not found."}

        stored_path = os.path.join(self.storage_dir, model_name)
        if not os.path.exists(stored_path):
            return {"success": False, "message": "Model file is missing."}

        current_hash = self._generate_hash(stored_path)
        if current_hash == self.models[model_name]["hash"]:
            return {"success": True, "message": "Model is unchanged."}
        else:
            # Call strategy model for decision
            decision = self.strategy_model(model_name, current_hash)
            return {
                "success": False,
                "message": "Model has been modified.",
                "decision": decision,
            }

    def update_model(self, model_path, model_name):
        """
        Update an existing model and validate it.

        :param model_path: Path to the updated model file.
        :param model_name: Name of the model.
        :return: Update result.
        """
        if not os.path.exists(model_path):
            return {"success": False, "message": "Updated model file does not exist."}

        if model_name not in self.models:
            return {"success": False, "message": "Model not found in repository."}

        new_hash = self._generate_hash(model_path)
        stored_path = os.path.join(self.storage_dir, model_name)

        # Call strategy model for decision
        decision = self.strategy_model(model_name, new_hash)
        if decision == "allow":
            os.replace(model_path, stored_path)
            self.models[model_name]["hash"] = new_hash
            self.models[model_name]["updated_at"] = datetime.now().isoformat()
            self._save_metadata()
            return {
                "success": True,
                "hash": new_hash,
                "message": "Model updated successfully.",
            }
        else:
            return {
                "success": False,
                "hash": new_hash,
                "message": "Model update rejected by strategy model.",
            }