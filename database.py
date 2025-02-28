from pymongo import MongoClient
from typing import Optional, List, Union
import os
from dotenv import load_dotenv
from models import Roadmap, Quiz, Resource
from bson import ObjectId
from pymongo.operations import SearchIndexModel
from sentence_transformers import SentenceTransformer

load_dotenv()

# MongoDB connection string
PWD = os.getenv("MONGO_PWD")
USER = os.getenv("MONGO_USER")
MONGO_URI = f"mongodb+srv://{USER}:{PWD}@database.0o8ty.mongodb.net/?retryWrites=true&w=majority&appName=database"

# Initialize the model with specific configuration
model = SentenceTransformer("BAAI/bge-large-en-v1.5", trust_remote_code=True)


def get_embedding(data):
    """Generates vector embeddings for the given data."""
    embedding = model.encode(data)
    return embedding.tolist()


class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.ai_tutor_db

    def _get_by_id(self, collection_name: str, item_id: str, model_type: type) -> Optional[
        Union[Roadmap, Quiz, Resource]]:
        """Helper function to get an item by its ID from a specific collection."""
        data = self.db[collection_name].find_one({'_id': ObjectId(item_id)})
        if data:
            data['mongo_id'] = str(data.pop('_id'))
            return model_type.model_validate(data)
        return None

    def _get_by_slug(self, collection_name: str, slug: str, model_type: type) -> Optional[
        Union[Roadmap, Quiz, Resource]]:
        """Helper function to get an item by its slug from a specific collection."""
        data = self.db[collection_name].find_one({'slug': slug})
        if data:
            data['mongo_id'] = str(data.pop('_id'))
            return model_type.model_validate(data)
        return None

    def _create(self, collection_name: str, item: Union[Roadmap, Quiz, Resource]) -> str:
        """Helper function to create a new item in a specific collection."""
        data = item.model_dump(exclude={"mongo_id"})
        if "description" in data and "name" in data:
            embedding = get_embedding(data["description"] + data["name"])
            data["embedding"] = embedding
        result = self.db[collection_name].insert_one(data)
        return str(result.inserted_id)

    def _update(self, collection_name: str, item_id: str, item: Union[Roadmap, Quiz, Resource]) -> bool:
        """Helper function to update an existing item in a specific collection."""
        data = item.model_dump(exclude={"mongo_id"})
        result = self.db[collection_name].update_one(
            {'_id': ObjectId(item_id)},
            {'$set': data}
        )
        return result.modified_count > 0

    def get_all(self, collection_name: str, model_type: type) -> List[Union[Roadmap, Quiz, Resource]]:
        """Helper function to get all items from a specific collection."""
        data = list(self.db[collection_name].find())
        items = []
        for item in data:
            item['mongo_id'] = str(item.pop('_id'))
            items.append(model_type.model_validate(item))
        return items

    def create_roadmap(self, roadmap: Roadmap) -> str:
        """Create a new roadmap"""
        return self._create("roadmaps", roadmap)

    def update_roadmap(self, roadmap_id: str, roadmap: Roadmap) -> bool:
        """Update an existing roadmap"""
        return self._update("roadmaps", roadmap_id, roadmap)

    def get_roadmap(self, roadmap_id: str) -> Optional[Roadmap]:
        """Get a roadmap by ID"""
        return self._get_by_id("roadmaps", roadmap_id, Roadmap)

    def get_roadmap_by_title(self, title: str) -> Optional[Roadmap]:
        """Get a roadmap by title"""
        data = self.db.roadmaps.find_one({'title': title})
        if data:
            data['mongo_id'] = str(data.pop('_id'))
            return Roadmap.model_validate(data)
        return None

    def get_all_roadmaps(self) -> List[Roadmap]:
        """Get all roadmaps"""
        return self.get_all("roadmaps", Roadmap)

    def create_quiz(self, quiz: Quiz) -> str:
        """Create a new quiz"""
        return self._create("quizzes", quiz)

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Get a quiz by ID

        Args:
            quiz_id: MongoDB ObjectId as string

        Returns:
            Quiz object if found, None otherwise
        """
        return self._get_by_id("quizzes", quiz_id, Quiz)

    def get_quiz_by_slug(self, slug: str) -> Optional[Quiz]:
        """Get a quiz by slug"""
        return self._get_by_slug("quizzes", slug, Quiz)

    def get_all_quizzes(self) -> List[Quiz]:
        """Get all available quizzes

        Returns:
            List of Quiz objects sorted by creation date
        """
        quizzes = []
        data = self.db.quizzes.find().sort("created_at", -1)

        for item in data:
            # Convert ObjectId to string for mongo_id
            item['mongo_id'] = str(item.pop('_id'))
            quizzes.append(Quiz.model_validate(item))

        return quizzes

    def create_resource(self, resource: Resource) -> str:
        """Create a new resource"""
        return self._create("resources", resource)

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID"""
        return self._get_by_id("resources", resource_id, Resource)

    def get_resource_by_slug(self, slug: str) -> Optional[Resource]:
        """Get a resource by slug"""
        return self._get_by_slug("resources", slug, Resource)

    def get_all_resources(self) -> List[Resource]:
        """Get all resources"""
        return self.get_all("resources", Resource)

    def search_resources(self, query: str, limit: int = 2) -> list[Resource]:
        """Search resources using vector similarity

        Args:
            query: The search query text
            limit: Maximum number of results to return (default 5)

        Returns:
            List of Resource objects sorted by relevance
        """
        query_embedding = get_embedding(query)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": limit * 10,  # Internal limit for pre-filtering
                    "limit": limit
                }
            },
            {
                "$project": {
                    "name": 1,
                    "description": 1,
                    "asset": 1,
                    "resource_type": 1,
                    "created_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = list(self.db.resources.aggregate(pipeline))
        resources = []

        for item in results:
            # Convert ObjectId to string for mongo_id
            item['mongo_id'] = str(item.pop('_id'))
            # Remove score from the item before creating Resource object
            score = item.pop('score', 0)
            resources.append(Resource.model_validate(item))

        return resources

    def create_index(self):
        collection = self.db.resources

        # List and drop all search indexes
        try:
            indexes = list(collection.list_search_indexes())
            for index in indexes:

                index_name = index.get("name")
                if index_name:
                    print(f"Dropping index: {index_name}")
                    collection.drop_index(index_name)
            print("Dropped all existing search indexes")
        except Exception as e:
            print(f"Error handling existing indexes: {e}")

        # Create your index model, then create the search index
        search_index_model = SearchIndexModel(
            definition={
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "embedding": {
                            "type": "knnVector",
                            "dimensions": 1024,
                            "similarity": "cosine"
                        }
                    }
                }
            },
            name="vector_index"
        )

        # Wait a bit before creating new index
        import time
        time.sleep(2)

        result = collection.create_search_index(model=search_index_model)
        print("New search index named " + result + " is building.")

        # Wait for initial sync to complete
        print("Polling to check if the index is ready. This may take up to a minute.")
        predicate = lambda index: index.get("queryable") is True
        while True:
            indices = list(collection.list_search_indexes(name="vector_index"))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(1)  # Add small delay between checks

        print(result + " is ready for querying.")

    def update_all_embeddings(self):
        """Update embeddings for all existing resources"""
        print("Updating embeddings for all resources...")
        resources = self.get_all_