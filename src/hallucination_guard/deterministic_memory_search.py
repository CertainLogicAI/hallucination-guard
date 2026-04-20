#!/usr/bin/env python3
"""
CertainLogic Verifier - Deterministic Memory Search
Embedding‑free search over local text files using TF‑IDF cosine similarity.
Useful for on‑premises document retrieval without external API calls.
MIT License
"""

import os
import re
import json
import math
import hashlib
from collections import defaultdict
from typing import List, Tuple, Dict

MEMORY_DIR = os.getenv("MEMORY_DIR", "./memory")

def tokenize(text: str) -> List[str]:
    """Simple tokenization: lowercase, split on non-alphanumeric."""
    return re.findall(r'\w+', text.lower())

def load_memory_files() -> List[Tuple[str, str, List[str]]]:
    """
    Load all .md files in MEMORY_DIR.
    Returns list of (file_path, content, lines).
    """
    files = []
    if not os.path.isdir(MEMORY_DIR):
        return files
    for fname in os.listdir(MEMORY_DIR):
        if fname.endswith('.md'):
            path = os.path.join(MEMORY_DIR, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = content.splitlines()
                files.append((path, content, lines))
            except Exception as e:
                print(f"Warning: Could not read {path}: {e}")
    return files

def build_index(files: List[Tuple[str, str, List[str]]]) -> Tuple[Dict[str, List[Tuple[str, int]]], int, Dict[str, int]]:
    """
    Build inverted index: term -> list of (file_path, term_frequency).
    Also returns total number of documents and document frequency per term.
    """
    index = defaultdict(list)  # term -> list of (file_path, tf)
    doc_freq = defaultdict(int)  # term -> number of docs containing term
    total_docs = len(files)
    
    for file_path, content, lines in files:
        terms = tokenize(content)
        term_counts = defaultdict(int)
        for term in terms:
            term_counts[term] += 1
        # Update index and doc freq
        for term, tf in term_counts.items():
            index[term].append((file_path, tf))
            doc_freq[term] += 1
    
    return dict(index), total_docs, dict(doc_freq)

def compute_idf(doc_freq: Dict[str, int], total_docs: int) -> Dict[str, float]:
    """Compute inverse document frequency for each term."""
    idf = {}
    for term, df in doc_freq.items():
        idf[term] = math.log((total_docs + 1) / (df + 1)) + 1  # smoothed
    return idf

def compute_tfidf_vector(terms: List[str], term_counts: Dict[str, int], idf: Dict[str, float]) -> Dict[str, float]:
    """Compute TF-IDF vector for a document given term counts and IDF."""
    vector = {}
    max_tf = max(term_counts.values()) if term_counts else 1
    for term, tf in term_counts.items():
        # normalized TF (term frequency / max TF in doc)
        tf_norm = tf / max_tf
        vector[term] = tf_norm * idf.get(term, 0.0)
    return vector

def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in set(vec1) & set(vec2))
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def search_memory(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search memory files for query.
    Returns list of results with file path, lines, snippet, and hash.
    """
    files = load_memory_files()
    if not files:
        return []
    
    # Build index
    index, total_docs, doc_freq = build_index(files)
    idf = compute_idf(doc_freq, total_docs)
    
    # Tokenize query
    query_terms = tokenize(query)
    if not query_terms:
        return []
    
    # Compute query vector
    query_term_counts = defaultdict(int)
    for term in query_terms:
        query_term_counts[term] += 1
    query_vec = compute_tfidf_vector(query_terms, query_term_counts, idf)
    
    # Score each document
    scores = []
    for file_path, content, lines in files:
        # Compute term counts for this doc
        terms = tokenize(content)
        term_counts = defaultdict(int)
        for term in terms:
            term_counts[term] += 1
        # Compute TF-IDF vector for doc
        doc_vec = compute_tfidf_vector(terms, term_counts, idf)
        # Compute similarity
        score = cosine_similarity(query_vec, doc_vec)
        if score > 0:
            scores.append((score, file_path, content, lines))
    
    # Sort by score descending
    scores.sort(key=lambda x: x[0], reverse=True)
    
    # Build results with snippets
    results = []
    for score, file_path, content, lines in scores[:top_k]:
        # Find lines that contain any query term (for snippet)
        matched_line_nums = []
        for i, line in enumerate(lines, start=1):
            line_terms = tokenize(line)
            if any(term in line_terms for term in query_terms):
                matched_line_nums.append(i)
        
        if not matched_line_nums:
            # If no line matched exactly, fallback to first few lines
            matched_line_nums = list(range(1, min(4, len(lines)) + 1))
        
        # Build snippet: show matched lines with some context
        snippet_lines = []
        for ln in matched_line_nums:
            start = max(0, ln - 2)  # show 2 lines before
            end = min(len(lines), ln + 1)  # show line itself
            snippet_lines.extend(lines[start:end])
        
        snippet = '\n'.join(snippet_lines)
        
        # Compute hash of snippet for verification
        snippet_hash = hashlib.sha256(snippet.encode('utf-8')).hexdigest()
        
        results.append({
            "file_path": file_path,
            "lines": matched_line_nums,
            "snippet": snippet,
            "hash": snippet_hash,
            "score": score
        })
    
    return results

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python deterministic_memory_search.py <query> [top_k]")
        sys.exit(1)
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    results = search_memory(query, top_k)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()