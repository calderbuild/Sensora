"""
Physio-RAG Engine: Retrieval-Augmented Generation for physiological corrections.
Uses ChromaDB with sentence-transformers for semantic similarity search.
"""

import json
from typing import Optional
from dataclasses import dataclass

from app.config import settings


@dataclass
class PhysioRule:
    """A physiological correction rule."""
    id: str
    condition: dict
    target: str
    action: str
    factor: Optional[float] = None
    threshold: Optional[dict] = None
    substitute: Optional[dict] = None
    reasoning: str = ""


@dataclass
class RetrievedRule:
    """A rule retrieved from the vector database with relevance score."""
    rule: PhysioRule
    relevance_score: float
    matched_condition: str


class SentenceTransformerEmbedding:
    """Custom embedding function using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = None
        self._model_name = model_name

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
            except ImportError:
                raise ImportError("sentence-transformers required for embeddings")

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Generate embeddings for input texts."""
        self._load_model()
        embeddings = self._model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()


class PhysioRAG:
    """
    Physio-RAG Engine for retrieving physiological correction rules.

    Uses ChromaDB with sentence-transformers for semantic similarity search
    to find relevant rules based on user physiological profile.
    """

    def __init__(self):
        self._rules: list[PhysioRule] = []
        self._collection = None
        self._embedder: Optional[SentenceTransformerEmbedding] = None
        self._initialized = False

    def initialize(self, use_vector_db: bool = True):
        """
        Initialize the RAG engine.

        Args:
            use_vector_db: Whether to use ChromaDB for vector search.
                          If False, uses simple keyword matching.
        """
        self._load_rules()

        if use_vector_db:
            self._setup_embedder()
            self._setup_vector_db()

        self._initialized = True

    def _setup_embedder(self):
        """Initialize sentence-transformers embedder."""
        try:
            self._embedder = SentenceTransformerEmbedding()
        except ImportError:
            self._embedder = None

    def _load_rules(self):
        """Load physio rules from JSON file."""
        rules_path = settings.data_dir / "physio_rules.json"

        if not rules_path.exists():
            self._rules = []
            return

        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for rule_data in data.get('rules', []):
            rule = PhysioRule(
                id=rule_data['id'],
                condition=rule_data['condition'],
                target=rule_data['target'],
                action=rule_data['action'],
                factor=rule_data.get('factor'),
                threshold=rule_data.get('threshold'),
                substitute=rule_data.get('substitute'),
                reasoning=rule_data.get('reasoning', '')
            )
            self._rules.append(rule)

    def _setup_vector_db(self):
        """Set up ChromaDB collection with sentence-transformer embeddings."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            # Initialize ChromaDB client (in-memory for MVP)
            client = chromadb.Client(ChromaSettings(
                anonymized_telemetry=False,
                is_persistent=False
            ))

            # Create collection with custom embedding function if available
            if self._embedder:
                self._collection = client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "Physio-chemical rules for perfume formulation"},
                    embedding_function=self._embedder
                )
            else:
                self._collection = client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "Physio-chemical rules for perfume formulation"}
                )

            # Embed rules if collection is empty
            if self._collection.count() == 0:
                self._embed_rules()

        except ImportError:
            # Fallback to keyword matching if ChromaDB not available
            self._collection = None

    def _embed_rules(self):
        """Embed rules into the vector database with rich semantic content."""
        if not self._collection or not self._rules:
            return

        documents = []
        ids = []
        metadatas = []

        for rule in self._rules:
            condition = rule.condition
            param = condition.get('parameter', '')
            operator = condition.get('operator', '')
            value = condition.get('value', '')

            # Create rich semantic document for better retrieval
            doc_parts = [
                f"Condition: {param} {operator} {value}",
                f"Affects: {rule.target}",
                f"Action: {rule.action}",
            ]
            if rule.factor:
                doc_parts.append(f"Adjustment factor: {rule.factor}")
            if rule.reasoning:
                doc_parts.append(f"Reasoning: {rule.reasoning}")

            # Add semantic expansion for better matching
            semantic_hints = self._get_semantic_hints(param, operator, value)
            if semantic_hints:
                doc_parts.append(f"Related concepts: {semantic_hints}")

            documents.append(" | ".join(doc_parts))
            ids.append(rule.id)
            metadatas.append({
                "target": rule.target,
                "action": rule.action,
                "parameter": param,
                "operator": operator,
                "value": str(value),
                "factor": str(rule.factor) if rule.factor else ""
            })

        self._collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def _get_semantic_hints(self, param: str, operator: str, value) -> str:
        """Generate semantic hints for better embedding similarity."""
        hints = []

        if param == "ph":
            if operator == "<" and isinstance(value, (int, float)) and value <= 5.5:
                hints.extend(["acidic skin", "dry skin chemistry", "faster evaporation"])
            elif operator == ">" and isinstance(value, (int, float)) and value >= 5.5:
                hints.extend(["alkaline skin", "oily skin chemistry", "slower breakdown"])

        elif param == "skin_type":
            if value == "dry":
                hints.extend(["low sebum", "faster absorption", "needs moisturizing bases"])
            elif value == "oily":
                hints.extend(["high sebum", "better projection", "avoid heavy oils"])

        elif param == "temperature":
            if operator == ">" and isinstance(value, (int, float)) and value >= 37:
                hints.extend(["warm skin", "faster diffusion", "enhanced projection"])
            elif operator == "<" and isinstance(value, (int, float)) and value <= 36:
                hints.extend(["cool skin", "slower evaporation", "subtle sillage"])

        return ", ".join(hints)

    def query(self, user_profile: dict, n_results: int = 5) -> list[RetrievedRule]:
        """
        Query for relevant physio rules based on user profile.

        Args:
            user_profile: Dict with keys like 'ph', 'skin_type', 'temperature', 'allergies'
            n_results: Maximum number of rules to return

        Returns:
            List of RetrievedRule objects sorted by relevance
        """
        if not self._initialized:
            self.initialize()

        # Build semantic query from profile
        query_parts = []

        if 'ph' in user_profile:
            ph = user_profile['ph']
            query_parts.append(f"pH level {ph}")
            if ph < 5.2:
                query_parts.append("acidic skin chemistry faster evaporation")
            elif ph > 5.8:
                query_parts.append("alkaline skin chemistry slower breakdown")

        if 'skin_type' in user_profile:
            skin = user_profile['skin_type'].lower()
            query_parts.append(f"skin type {skin}")
            if skin == "dry":
                query_parts.append("low sebum fast absorption")
            elif skin == "oily":
                query_parts.append("high sebum enhanced projection")

        if 'temperature' in user_profile:
            temp = user_profile['temperature']
            query_parts.append(f"body temperature {temp}")
            if temp > 37.0:
                query_parts.append("warm skin fast diffusion")
            elif temp < 36.0:
                query_parts.append("cool skin slow evaporation")

        if 'allergies' in user_profile:
            for allergy in user_profile.get('allergies', []):
                query_parts.append(f"allergen sensitivity {allergy}")

        query_text = " ".join(query_parts)

        if self._collection is not None:
            return self._vector_query(query_text, n_results)
        else:
            return self._keyword_query(user_profile, n_results)

    def _vector_query(self, query_text: str, n_results: int) -> list[RetrievedRule]:
        """Query using ChromaDB vector similarity with sentence-transformers."""
        if self._collection is None:
            return []

        results = self._collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        retrieved = []
        ids = results.get('ids', [[]])[0]
        distances = results.get('distances', [[]])[0]

        for i, rule_id in enumerate(ids):
            rule = self._get_rule_by_id(rule_id)
            if rule:
                distance = distances[i] if i < len(distances) else 1.0
                relevance = 1.0 / (1.0 + distance)
                retrieved.append(RetrievedRule(
                    rule=rule,
                    relevance_score=relevance,
                    matched_condition=query_text
                ))

        return retrieved

    def _keyword_query(self, user_profile: dict, n_results: int) -> list[RetrievedRule]:
        """Fallback keyword-based matching when vector DB not available."""
        matched = []

        for rule in self._rules:
            condition = rule.condition
            param = condition.get('parameter', '')
            operator = condition.get('operator', '')
            value = condition.get('value')

            if param not in user_profile or value is None:
                continue

            user_value = user_profile[param]
            matches = False
            relevance = 0.5

            if operator == '<' and isinstance(user_value, (int, float)) and isinstance(value, (int, float)):
                matches = user_value < value
            elif operator == '>' and isinstance(user_value, (int, float)) and isinstance(value, (int, float)):
                matches = user_value > value
            elif operator == '==':
                matches = user_value == value
            elif operator == 'contains' and isinstance(user_value, list):
                matches = value in user_value

            if matches:
                relevance = 0.9
                matched.append(RetrievedRule(
                    rule=rule,
                    relevance_score=relevance,
                    matched_condition=f"{param} {operator} {value}"
                ))

        matched.sort(key=lambda x: x.relevance_score, reverse=True)
        return matched[:n_results]

    def _get_rule_by_id(self, rule_id: str) -> Optional[PhysioRule]:
        """Get a rule by its ID."""
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def get_applicable_rules(self, user_profile: dict) -> list[PhysioRule]:
        """
        Get all rules that apply to a user profile (exact condition matching).

        Args:
            user_profile: User physiological data

        Returns:
            List of applicable PhysioRule objects
        """
        if not self._initialized:
            self.initialize()

        applicable = []

        for rule in self._rules:
            condition = rule.condition
            param = condition.get('parameter', '')
            operator = condition.get('operator', '')
            value = condition.get('value')

            if param not in user_profile or value is None:
                continue

            user_value = user_profile[param]

            if operator == '<' and isinstance(user_value, (int, float)) and isinstance(value, (int, float)):
                if user_value < value:
                    applicable.append(rule)
            elif operator == '>' and isinstance(user_value, (int, float)) and isinstance(value, (int, float)):
                if user_value > value:
                    applicable.append(rule)
            elif operator == '==' and user_value == value:
                applicable.append(rule)
            elif operator == 'contains' and isinstance(user_value, list) and value in user_value:
                applicable.append(rule)

        return applicable


# Singleton instance
physio_rag = PhysioRAG()
