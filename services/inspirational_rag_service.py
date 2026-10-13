from pathlib import Path
import chromadb

from langchain_huggingface import HuggingFaceEmbeddings
from utils.logger import get_logger

logger = get_logger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base" / "inspirational"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "inspirational_knowledge"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class InspirationalRAGService:
    def __init__(self):
        logger.info("Initializing Inspirational RAG Service")

        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info("Inspirational RAG Service initialized")

    def index_documents(self):
        """Read text files and store their embeddings in ChromaDB."""

        if not KNOWLEDGE_DIR.exists():
            raise FileNotFoundError(f"Knowledge directory not found: {KNOWLEDGE_DIR}")

        files = sorted(KNOWLEDGE_DIR.glob("*.txt"))

        if not files:
            raise FileNotFoundError(f"No .txt documents found in {KNOWLEDGE_DIR}")

        ids = []
        documents = []
        metadatas = []

        for file_path in files:
            content = file_path.read_text(encoding="utf-8").strip()

            if not content:
                logger.warning(
                    "Skipping empty document: %s",
                    file_path.name,
                )
                continue

            ids.append(file_path.stem)
            documents.append(content)
            metadatas.append(
                {
                    "source": file_path.name,
                    "topic": file_path.stem.replace("_", " "),
                }
            )

        if not documents:
            raise ValueError("No non-empty knowledge documents found.")

        # Generate embeddings for all documents.
        vectors = self.embeddings.embed_documents(documents)

        # Upsert creates new entries or updates existing ones.
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=vectors,
        )

        logger.info(
            "Indexed %d inspirational documents",
            len(documents),
        )

        return len(documents)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """Retrieve the most semantically similar documents."""

        if not query or not query.strip():
            return []

        if self.collection.count() == 0:
            raise ValueError(
                "The knowledge base is empty. " "Run index_documents() first."
            )

        query_vector = self.embeddings.embed_query(query.strip())

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(
                top_k,
                self.collection.count(),
            ),
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved = []

        for index, document in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]
            distance = results["distances"][0][index]

            retrieved.append(
                {
                    "content": document,
                    "source": metadata.get("source", ""),
                    "topic": metadata.get("topic", ""),
                    "distance": distance,
                }
            )

        logger.info(
            "Retrieved %d documents for query: %s",
            len(retrieved),
            query,
        )

        return retrieved


inspirational_rag_service = InspirationalRAGService()
