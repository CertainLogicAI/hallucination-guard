#!/usr/bin/env python3
"""
Hybrid AI Router - Routes queries to appropriate AI type based on context
Deterministic AI for compliance/security tasks, External LLMs for creative tasks
"""

import os
import re
import json
import hashlib
from typing import Dict, Any, Tuple

class HybridAIRouter:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.deterministic_keywords = self._load_deterministic_keywords()
        self.compliance_patterns = self._load_compliance_patterns()
        
    def _load_deterministic_keywords(self) -> set:
        """Load keywords that indicate deterministic processing is needed"""
        return {
            'plc', 'faulttrace', 'verification', 'audit', 'compliance', 
            'regulation', 'legal', 'financial', 'medical', 'hipaa', 'gdpr',
            'sox', 'iso', 'iec', 'nfpa', 'ansi', 'ul', 'csa', 'ce',
            'safety', 'hazard', 'risk', 'assessment', 'validation',
            'verification', 'certification', 'approval', 'inspection',
            'test', 'test procedure', 'test protocol', 'l5x', 'ladder logic',
            'structured text', 'function block', 'instruction list',
            'sequential function chart', 'iec 61131-3', 'iec 61508',
            'iso 13849', 'iso 26262', 'iec 62061', 'iec 62443'
        }
    
    def _load_compliance_patterns(self) -> list:
        """Load regex patterns that indicate compliance requirements"""
        return [
            r'\b(?:must|shall|required|mandatory|obligation)\b.*\b(?:comply|compliance|conform|adhere)\b',
            r'\b(?:audit|inspection|validation|verification)\b.*\b(?:report|record|document|evidence)\b',
            r'\b(?:gdpr|hipaa|sox|pci|dss)\b.*\b(?:data|information|privacy|security)\b',
            r'\b(?:safety|hazard|risk)\b.*\b(?:assessment|analysis|evaluation|mitigation)\b',
            r'\b(?:plc|ladder logic|structured text)\b.*\b(?:verification|validation|test)\b',
            r'\b(?:fault|error|failure)\b.*\b(?:analysis|diagnosis|resolution|root cause)\b'
        ]
    
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[str, float, str]:
        """
        Route query to appropriate AI type
        Returns: (ai_type, confidence, reasoning)
        ai_type: 'deterministic' or 'external'
        confidence: 0.0 to 1.0
        reasoning: explanation of decision
        """
        query_lower = query.lower()
        context = context or {}
        
        # Check for explicit routing hints in context
        if context.get('force_deterministic'):
            return 'deterministic', 1.0, "Forced deterministic processing via context"
        if context.get('force_external'):
            return 'external', 1.0, "Forced external processing via context"
        
        # Check for deterministic keywords
        keyword_matches = sum(1 for kw in self.deterministic_keywords if kw in query_lower)
        keyword_score = min(keyword_matches / 3.0, 1.0)  # Cap at 1.0 after 3 matches
        
        # Check for compliance patterns
        pattern_matches = sum(1 for pattern in self.compliance_patterns 
                             if re.search(pattern, query_lower, re.IGNORECASE))
        pattern_score = min(pattern_matches / 2.0, 1.0)  # Cap at 1.0 after 2 matches
        
        # Check for data sensitivity indicators
        data_sensitivity = self._assess_data_sensitivity(query, context)
        
        # Calculate final scores
        deterministic_score = (keyword_score * 0.4) + (pattern_score * 0.4) + (data_sensitivity * 0.2)
        external_score = 1.0 - deterministic_score
        
        # Determine routing
        if deterministic_score >= 0.6:
            ai_type = 'deterministic'
            confidence = deterministic_score
            reasoning = f"Compliance/security indicators detected (kw:{keyword_matches}, pat:{pattern_matches}, data:{data_sensitivity:.2f})"
        else:
            ai_type = 'external'
            confidence = external_score
            reasoning = f"Creative/exploratory task detected (kw:{keyword_matches}, pat:{pattern_matches}, data:{data_sensitivity:.2f})"
        
        return ai_type, confidence, reasoning
    
    def _assess_data_sensitivity(self, query: str, context: Dict[str, Any]) -> float:
        """Assess sensitivity of data involved in query"""
        sensitivity = 0.0
        
        # Check for PII indicators
        pii_patterns = [r'\b(?:name|address|phone|email|ssn|social security)\b',
                       r'\b(?:medical|health|patient|diagnosis|treatment)\b',
                       r'\b(?:financial|account|credit|bank|payment)\b',
                       r'\b(?:legal|attorney|lawyer|court|litigation)\b']
        
        for pattern in pii_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                sensitivity += 0.2
        
        # Check for regulatory data
        reg_patterns = [r'\b(?:gdpr|hipaa|sox|pci)\b',
                       r'\b(?:personal data|sensitive data|confidential|proprietary)\b']
        
        for pattern in reg_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                sensitivity += 0.3
        
        # Check context for data sensitivity flags
        if context.get('data_sensitivity') == 'high':
            sensitivity += 0.3
        elif context.get('data_sensitivity') == 'medium':
            sensitivity += 0.15
            
        return min(sensitivity, 1.0)
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process query using appropriate AI type
        Returns result with metadata about processing method
        """
        ai_type, confidence, reasoning = self.route_query(query, context)
        
        result = {
            'query': query,
            'ai_type': ai_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'timestamp': int(os.times()[4]),  # Simplified timestamp
            'processing_method': None,
            'output': None,
            'verification_hash': None
        }
        
        if ai_type == 'deterministic':
            # Use deterministic memory search
            from deterministic_memory_search import search_memory
            search_results = search_memory(query, top_k=5)
            
            # Format results for output
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    'file': result['file_path'],
                    'lines': result['lines'],
                    'snippet': result['snippet'],
                    'hash': result['hash'],
                    'score': result['score']
                })
            
            result['processing_method'] = 'deterministic_search'
            result['output'] = formatted_results
            
            # Generate verification hash for entire response
            response_json = json.dumps(formatted_results, sort_keys=True)
            result['verification_hash'] = hashlib.sha256(response_json.encode()).hexdigest()
            
        else:
            # Use external LLM (placeholder - integrate with your preferred LLM)
            result['processing_method'] = 'external_llm'
            result['output'] = {
                'message': 'External LLM processing would occur here',
                'note': 'Integrate with your preferred LLM API (OpenAI, Anthropic, etc.)',
                'suggestion': 'Consider using a local LLM like Llama or Mistral for on-prem processing'
            }
            # For external LLMs, we can't provide deterministic verification hash
            # but we could log the request/response for audit purposes
            result['verification_hash'] = None
        
        return result

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hybrid_ai_router.py \"<query>\" [--context \"{'key':'value'}\"]")
        print("Example: python hybrid_ai_router.py \"How to fix PLC communication errors?\"")
        sys.exit(1)
    
    query = sys.argv[1]
    context = {}
    
    if len(sys.argv) > 3 and sys.argv[2] == '--context':
        try:
            context = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            print("Error: Invalid JSON context")
            sys.exit(1)
    
    router = HybridAIRouter("/data/.openclaw/workspace")
    result = router.process_query(query, context)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()