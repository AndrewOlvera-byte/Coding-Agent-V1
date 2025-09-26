from typing import Dict, Any, List, Optional
import os

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover
    chromadb = None
    embedding_functions = None


class VectorMemory:
    def __init__(
        self,
        client,
        collection,
        namespace: str,
        top_k: int,
    ):
        self.client = client
        self.collection = collection
        self.namespace = namespace
        self.top_k = top_k

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]):
        persist_path = cfg.get("persist_path", "./.memory")
        namespace = cfg.get("namespace", "default")
        top_k = int(cfg.get("top_k", 6))
        if chromadb is None:
            return _NoopVectorMemory(namespace=namespace, top_k=top_k)
        try:
            client = chromadb.PersistentClient(path=persist_path)
            embed = embedding_functions.DefaultEmbeddingFunction()
            collection = client.get_or_create_collection(
                name=f"mem_{namespace}", embedding_function=embed
            )
            return cls(client, collection, namespace, top_k)
        except Exception:
            return _NoopVectorMemory(namespace=namespace, top_k=top_k)

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        doc_id = f"{self.namespace}_{self.collection.count()+1}"
        self.collection.add(ids=[doc_id], documents=[text], metadatas=[metadata or {}])
        return doc_id

    def search(self, query: str) -> List[Dict[str, Any]]:
        res = self.collection.query(query_texts=[query], n_results=self.top_k)
        results: List[Dict[str, Any]] = []
        for idx, doc in enumerate(res.get("documents", [[]])[0]):
            results.append(
                {
                    "document": doc,
                    "metadata": res.get("metadatas", [[]])[0][idx],
                    "distance": res.get("distances", [[]])[0][idx] if res.get("distances") else None,
                }
            )
        return results


class _NoopVectorMemory:
    def __init__(self, namespace: str, top_k: int):
        self.namespace = namespace
        self.top_k = top_k
        self._docs: List[Dict[str, Any]] = []

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]):  # type: ignore[override]
        return cls(namespace=cfg.get("namespace", "default"), top_k=int(cfg.get("top_k", 6)))

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        self._docs.append({"document": text, "metadata": metadata or {}})
        return f"noop_{len(self._docs)}"

    def search(self, query: str) -> List[Dict[str, Any]]:
        ranked = [d for d in self._docs if query.lower() in d["document"].lower()]
        return ranked[: self.top_k]


