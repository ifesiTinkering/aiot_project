#!/usr/bin/env python3
"""
Knowledge Base Module - Semantic search over curated facts
Uses RAG (Retrieval-Augmented Generation) approach with sentence embeddings
"""

import json
import os
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import torch

class KnowledgeBase:
    """RAG-based knowledge base with semantic search"""

    def __init__(self, kb_path: str = "knowledge_base.json"):
        self.kb_path = kb_path
        self.facts = []
        self.embeddings = None

        # Load sentence transformer model (same as emotion classifier)
        print("[INFO] Loading sentence embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_model.eval()

        # Load knowledge base
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load facts from JSON file and compute embeddings"""
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r') as f:
                data = json.load(f)
                self.facts = data.get('facts', [])

            print(f"[INFO] Loaded {len(self.facts)} facts from knowledge base")

            # Compute embeddings for all facts
            if self.facts:
                fact_texts = [fact['text'] for fact in self.facts]
                print("[INFO] Computing embeddings for facts...")
                self.embeddings = self.embedding_model.encode(
                    fact_texts,
                    convert_to_tensor=True,
                    show_progress_bar=False
                )
                print(f"[INFO] Computed embeddings with shape {self.embeddings.shape}")
        else:
            print(f"[WARNING] Knowledge base not found at {self.kb_path}")
            print("[INFO] Starting with empty knowledge base")
            self.facts = []
            self.embeddings = None

    def search(self, query: str, top_k: int = 3, threshold: float = 0.3) -> List[Dict]:
        """
        Search for relevant facts using semantic similarity

        Args:
            query: Text to search for
            top_k: Number of top results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of relevant facts with similarity scores
        """
        if not self.facts or self.embeddings is None:
            return []

        # Encode query
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_tensor=True,
            show_progress_bar=False
        )

        # Compute cosine similarity
        similarities = torch.nn.functional.cosine_similarity(
            query_embedding.unsqueeze(0),
            self.embeddings
        )

        # Get top-k results above threshold
        scores, indices = torch.topk(similarities, min(top_k, len(self.facts)))

        results = []
        for score, idx in zip(scores.tolist(), indices.tolist()):
            if score >= threshold:
                fact = self.facts[idx].copy()
                fact['similarity_score'] = score
                results.append(fact)

        return results

    def categorize_facts(self, query: str, top_k: int = 5) -> Dict[str, List[Dict]]:
        """
        Search and categorize facts as supporting or contradicting

        Args:
            query: Text to analyze
            top_k: Number of facts to retrieve

        Returns:
            Dictionary with 'supporting' and 'contradicting' lists
        """
        relevant_facts = self.search(query, top_k=top_k, threshold=0.3)

        supporting = []
        contradicting = []

        for fact in relevant_facts:
            # Check if fact supports or contradicts based on stance field
            stance = fact.get('stance', 'neutral')

            fact_data = {
                'text': fact['text'],
                'source_type': 'database',
                'source_name': fact.get('source', 'Knowledge Base'),
                'url': fact.get('url', None),
                'similarity': fact['similarity_score'],
                'icon': '📊'
            }

            if stance == 'supporting':
                supporting.append(fact_data)
            elif stance == 'contradicting':
                contradicting.append(fact_data)
            else:
                # Neutral facts go to supporting by default
                supporting.append(fact_data)

        return {
            'supporting': supporting,
            'contradicting': contradicting
        }

    def add_fact(self, text: str, source: str = None, url: str = None,
                 stance: str = 'neutral', category: str = None):
        """Add a new fact to the knowledge base"""
        fact = {
            'text': text,
            'source': source,
            'url': url,
            'stance': stance,
            'category': category
        }

        self.facts.append(fact)

        # Recompute embeddings
        if self.facts:
            fact_texts = [f['text'] for f in self.facts]
            self.embeddings = self.embedding_model.encode(
                fact_texts,
                convert_to_tensor=True,
                show_progress_bar=False
            )

        # Save to file
        self.save_knowledge_base()

    def save_knowledge_base(self):
        """Save knowledge base to JSON file"""
        with open(self.kb_path, 'w') as f:
            json.dump({'facts': self.facts}, f, indent=2)
        print(f"[INFO] Saved {len(self.facts)} facts to {self.kb_path}")


def test_knowledge_base():
    """Test the knowledge base with sample queries"""
    kb = KnowledgeBase()

    # Test queries
    queries = [
        "remote work is more productive",
        "climate change is caused by humans",
        "electric vehicles are better for the environment"
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        results = kb.search(query, top_k=3)

        if results:
            for i, fact in enumerate(results, 1):
                print(f"\n{i}. {fact['text']}")
                print(f"   Source: {fact.get('source', 'Unknown')}")
                print(f"   Similarity: {fact['similarity_score']:.3f}")
        else:
            print("No relevant facts found")


if __name__ == "__main__":
    test_knowledge_base()
