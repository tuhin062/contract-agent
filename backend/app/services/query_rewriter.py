"""
Query rewriting and intent detection for legal document queries.
Enhances queries to improve retrieval accuracy.
"""
from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class QueryRewriter:
    """
    Service for rewriting and enhancing legal document queries.
    Features:
    - Intent detection
    - Query expansion
    - Legal term normalization
    - Context-aware rewriting
    """
    
    # Legal intent patterns
    INTENT_PATTERNS = {
        "payment": {
            "keywords": ["payment", "pay", "compensation", "fee", "invoice", "billing", "price", "cost", "amount", "remuneration"],
            "questions": ["how much", "what is the payment", "payment terms", "when is payment"]
        },
        "termination": {
            "keywords": ["termination", "terminate", "cancel", "end", "expire", "expiration", "cancel", "rescind"],
            "questions": ["how to terminate", "termination clause", "when can I cancel"]
        },
        "liability": {
            "keywords": ["liability", "liable", "responsible", "responsibility", "damage", "loss", "harm"],
            "questions": ["who is liable", "liability clause", "what are the liabilities"]
        },
        "indemnification": {
            "keywords": ["indemnif", "indemnity", "hold harmless", "defend", "defense"],
            "questions": ["indemnification", "who indemnifies", "indemnity clause"]
        },
        "scope": {
            "keywords": ["scope", "work", "services", "deliverables", "obligations", "duties", "responsibilities"],
            "questions": ["what is the scope", "scope of work", "what services", "deliverables"]
        },
        "confidentiality": {
            "keywords": ["confidential", "non-disclosure", "nda", "proprietary", "secret", "privacy"],
            "questions": ["confidentiality", "non-disclosure", "what is confidential"]
        },
        "warranty": {
            "keywords": ["warranty", "warrant", "guarantee", "representation", "warranties"],
            "questions": ["warranty", "what warranties", "guarantee"]
        },
        "insurance": {
            "keywords": ["insurance", "coverage", "policy", "insured", "insurer"],
            "questions": ["insurance", "what insurance", "coverage requirements"]
        },
        "dispute": {
            "keywords": ["dispute", "arbitration", "mediation", "jurisdiction", "governing law", "litigation"],
            "questions": ["dispute resolution", "how to resolve disputes", "jurisdiction"]
        }
    }
    
    # Query expansion terms
    EXPANSION_TERMS = {
        "payment": ["compensation", "remuneration", "fee", "invoice"],
        "termination": ["cancellation", "expiration", "ending"],
        "liability": ["responsibility", "accountability"],
        "scope": ["work", "services", "deliverables"],
    }
    
    def detect_intent(self, query: str) -> Tuple[Optional[str], float]:
        """
        Detect the legal intent of a query.
        
        Returns:
            Tuple of (intent_type, confidence)
        """
        query_lower = query.lower()
        best_intent = None
        best_score = 0.0
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0.0
            
            # Check keyword matches
            keyword_matches = sum(1 for kw in patterns["keywords"] if kw in query_lower)
            score += keyword_matches * 0.3
            
            # Check question pattern matches
            question_matches = sum(1 for q in patterns["questions"] if q in query_lower)
            score += question_matches * 0.5
            
            # Normalize score
            score = min(1.0, score)
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return (best_intent, best_score) if best_score > 0.3 else (None, 0.0)
    
    def expand_query(self, query: str, intent: Optional[str] = None) -> str:
        """
        Expand query with relevant synonyms and terms.
        
        Args:
            query: Original query
            intent: Detected intent (optional)
            
        Returns:
            Expanded query
        """
        if not intent:
            intent, _ = self.detect_intent(query)
        
        expanded_terms = []
        query_lower = query.lower()
        
        # Add expansion terms based on intent
        if intent and intent in self.EXPANSION_TERMS:
            for term in self.EXPANSION_TERMS[intent]:
                if term not in query_lower:
                    expanded_terms.append(term)
        
        # Add legal context terms
        legal_context = ["clause", "provision", "section", "term", "agreement"]
        for term in legal_context:
            if term not in query_lower and any(legal_word in query_lower for legal_word in ["what", "where", "how", "when"]):
                expanded_terms.append(term)
        
        if expanded_terms:
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            logger.info(f"Expanded query: '{query}' -> '{expanded_query}'")
            return expanded_query
        
        return query
    
    def rewrite_query(self, query: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, str]:
        """
        Rewrite query for better retrieval.
        
        Args:
            query: Original query
            chat_history: Previous messages for context
            
        Returns:
            Dictionary with original, expanded, and rewritten queries
        """
        # Detect intent
        intent, confidence = self.detect_intent(query)
        
        # Expand query
        expanded_query = self.expand_query(query, intent)
        
        # Rewrite for better retrieval
        rewritten_query = self._rewrite_for_retrieval(query, intent, chat_history)
        
        return {
            "original": query,
            "expanded": expanded_query,
            "rewritten": rewritten_query,
            "intent": intent,
            "intent_confidence": confidence
        }
    
    def _rewrite_for_retrieval(self, query: str, intent: Optional[str], chat_history: Optional[List[Dict]]) -> str:
        """Rewrite query specifically for vector retrieval."""
        # Handle common question patterns
        question_patterns = {
            r"what (is|are) (the )?(payment|fee|cost)": "payment terms compensation fee",
            r"how (much|many)": "amount quantity number",
            r"when (is|are|can|do)": "time date schedule deadline",
            r"who (is|are)": "party person entity responsible",
            r"where (is|are)": "location place section",
        }
        
        rewritten = query
        for pattern, addition in question_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                rewritten = f"{query} {addition}"
                break
        
        # Add intent-specific terms
        if intent:
            intent_keywords = self.INTENT_PATTERNS[intent]["keywords"]
            # Add 1-2 most relevant keywords if not already present
            query_lower = query.lower()
            for keyword in intent_keywords[:2]:
                if keyword not in query_lower:
                    rewritten = f"{rewritten} {keyword}"
                    break
        
        return rewritten.strip()
    
    def extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for keyword matching."""
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                     "have", "has", "had", "do", "does", "did", "will", "would", "should",
                     "could", "may", "might", "can", "this", "that", "these", "those",
                     "what", "where", "when", "who", "why", "how", "which"}
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter stop words and short words
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        return key_terms


# Global query rewriter instance
query_rewriter = QueryRewriter()

