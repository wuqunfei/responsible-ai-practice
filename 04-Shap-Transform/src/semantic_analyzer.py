"""
Semantic Analysis Utilities for Pet Insurance Claims
Provides domain-specific feature extraction and pattern analysis
"""

import re
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


class SemanticAnalyzer:
    """Analyzes semantic patterns in pet insurance claims"""
    
    def __init__(self):
        """Initialize with domain-specific vocabularies"""
        self.medical_terms = {
            'conditions': [
                'fracture', 'broken', 'cancer', 'tumor', 'infection', 
                'inflammation', 'allergy', 'diabetes', 'kidney', 'liver',
                'heart', 'breathing', 'seizure', 'poisoning', 'injury'
            ],
            'procedures': [
                'surgery', 'operation', 'x-ray', 'xray', 'scan', 'mri', 
                'blood test', 'biopsy', 'ultrasound', 'examination',
                'treatment', 'therapy', 'medication', 'anesthesia'
            ],
            'emergency': [
                'emergency', 'urgent', 'critical', 'immediate', 'acute',
                'severe', 'life-threatening', 'accident', 'trauma'
            ],
            'preventive': [
                'routine', 'regular', 'preventive', 'checkup', 'wellness',
                'vaccination', 'dental cleaning', 'grooming', 'spay', 'neuter'
            ]
        }
        
        self.cost_patterns = re.compile(r'\$?\d+[,.\d]*')
        self.age_patterns = re.compile(r'(\d+)[\s-]*(year|month|week)s?\s*old', re.IGNORECASE)
    
    def extract_features(self, claim_text: str) -> Dict:
        """
        Extract semantic features from a claim
        
        Args:
            claim_text: Raw claim text
            
        Returns:
            Dictionary of extracted features
        """
        claim_lower = claim_text.lower()
        
        features = {
            # Medical features
            'has_condition': any(term in claim_lower for term in self.medical_terms['conditions']),
            'has_procedure': any(term in claim_lower for term in self.medical_terms['procedures']),
            'is_emergency': any(term in claim_lower for term in self.medical_terms['emergency']),
            'is_preventive': any(term in claim_lower for term in self.medical_terms['preventive']),
            
            # Cost features
            'mentions_cost': bool(self.cost_patterns.search(claim_text)),
            'cost_amount': self._extract_cost(claim_text),
            
            # Pet features
            'pet_age_months': self._extract_age(claim_text),
            
            # Complexity features
            'claim_length': len(claim_text.split()),
            'medical_term_count': sum(
                1 for category in self.medical_terms.values()
                for term in category if term in claim_lower
            )
        }
        
        # Add severity score
        features['severity_score'] = self._calculate_severity(features)
        
        return features
    
    def _extract_cost(self, text: str) -> Optional[float]:
        """Extract cost amount from text"""
        matches = self.cost_patterns.findall(text)
        if matches:
            # Clean and convert to float
            cost_str = matches[0].replace('$', '').replace(',', '')
            try:
                return float(cost_str)
            except ValueError:
                return None
        return None
    
    def _extract_age(self, text: str) -> Optional[int]:
        """Extract pet age in months"""
        matches = self.age_patterns.findall(text)
        if matches:
            number, unit = matches[0]
            number = int(number)
            
            if 'year' in unit:
                return number * 12
            elif 'month' in unit:
                return number
            elif 'week' in unit:
                return number // 4
        
        return None
    
    def _calculate_severity(self, features: Dict) -> float:
        """Calculate severity score based on features"""
        score = 0.0
        
        if features['is_emergency']:
            score += 0.8
        if features['has_condition']:
            score += 0.5
        if features['has_procedure']:
            score += 0.4
        if features['is_preventive']:
            score -= 0.6
        
        # Normalize to 0-1
        return max(0, min(1, score))
    
    def cluster_claims(self, claims: List[str], n_clusters: int = 4) -> Tuple[np.ndarray, Dict]:
        """
        Cluster claims by semantic similarity
        
        Args:
            claims: List of claim texts
            n_clusters: Number of clusters
            
        Returns:
            Cluster labels and cluster descriptions
        """
        # Extract features for all claims
        features_list = [self.extract_features(claim) for claim in claims]
        
        # Convert to feature matrix
        feature_names = list(features_list[0].keys())
        feature_matrix = np.array([
            [f.get(name, 0) if isinstance(f.get(name, 0), (int, float)) else float(f.get(name, False))
             for name in feature_names]
            for f in features_list
        ])
        
        # Normalize features
        feature_matrix = (feature_matrix - feature_matrix.mean(axis=0)) / (feature_matrix.std(axis=0) + 1e-8)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(feature_matrix)
        
        # Describe clusters
        cluster_descriptions = {}
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_features = feature_matrix[cluster_mask]
            
            if len(cluster_features) > 0:
                # Find dominant features
                mean_features = cluster_features.mean(axis=0)
                top_features_idx = np.argsort(np.abs(mean_features))[-3:]
                
                cluster_descriptions[cluster_id] = {
                    'size': int(cluster_mask.sum()),
                    'dominant_features': [feature_names[idx] for idx in top_features_idx],
                    'mean_severity': float(np.mean([
                        features_list[i]['severity_score'] 
                        for i, mask in enumerate(cluster_mask) if mask
                    ]))
                }
        
        return labels, cluster_descriptions
    
    def identify_patterns(self, claims: List[str], predictions: List[str]) -> Dict:
        """
        Identify patterns in approved vs rejected claims
        
        Args:
            claims: List of claim texts
            predictions: List of predictions (Approved/Rejected)
            
        Returns:
            Dictionary of identified patterns
        """
        approved_features = []
        rejected_features = []
        
        for claim, pred in zip(claims, predictions):
            features = self.extract_features(claim)
            if pred == 'Approved':
                approved_features.append(features)
            else:
                rejected_features.append(features)
        
        patterns = {
            'approved_patterns': self._summarize_features(approved_features),
            'rejected_patterns': self._summarize_features(rejected_features),
            'key_differences': self._find_key_differences(approved_features, rejected_features)
        }
        
        return patterns
    
    def _summarize_features(self, features_list: List[Dict]) -> Dict:
        """Summarize common features in a list"""
        if not features_list:
            return {}
        
        summary = {}
        
        # Boolean features - calculate percentage
        bool_features = ['has_condition', 'has_procedure', 'is_emergency', 'is_preventive', 'mentions_cost']
        for feat in bool_features:
            summary[f'{feat}_rate'] = np.mean([f.get(feat, False) for f in features_list])
        
        # Numeric features - calculate statistics
        numeric_features = ['cost_amount', 'pet_age_months', 'severity_score', 'medical_term_count']
        for feat in numeric_features:
            values = [f.get(feat) for f in features_list if f.get(feat) is not None]
            if values:
                summary[f'{feat}_mean'] = np.mean(values)
                summary[f'{feat}_median'] = np.median(values)
        
        return summary
    
    def _find_key_differences(self, approved_features: List[Dict], rejected_features: List[Dict]) -> Dict:
        """Find key differences between approved and rejected claims"""
        if not approved_features or not rejected_features:
            return {}
        
        approved_summary = self._summarize_features(approved_features)
        rejected_summary = self._summarize_features(rejected_features)
        
        differences = {}
        for key in approved_summary:
            if key in rejected_summary:
                diff = approved_summary[key] - rejected_summary[key]
                if abs(diff) > 0.2:  # Significant difference threshold
                    differences[key] = {
                        'approved_value': approved_summary[key],
                        'rejected_value': rejected_summary[key],
                        'difference': diff
                    }
        
        return differences
    
    def generate_business_rules(self, patterns: Dict, min_confidence: float = 0.75) -> List[str]:
        """
        Generate human-readable business rules from patterns
        
        Args:
            patterns: Pattern dictionary from identify_patterns
            min_confidence: Minimum confidence for rule generation
            
        Returns:
            List of business rules
        """
        rules = []
        
        # Check approved patterns
        approved = patterns.get('approved_patterns', {})
        if approved.get('is_emergency_rate', 0) > min_confidence:
            rules.append(f"Emergency claims have {approved['is_emergency_rate']*100:.1f}% approval rate")
        
        if approved.get('has_procedure_rate', 0) > min_confidence:
            rules.append(f"Claims with medical procedures have {approved['has_procedure_rate']*100:.1f}% approval rate")
        
        # Check rejected patterns
        rejected = patterns.get('rejected_patterns', {})
        if rejected.get('is_preventive_rate', 0) > min_confidence:
            rules.append(f"Preventive care claims have {rejected['is_preventive_rate']*100:.1f}% rejection rate")
        
        # Check key differences
        differences = patterns.get('key_differences', {})
        if 'severity_score_mean' in differences:
            diff = differences['severity_score_mean']
            if diff['difference'] > 0.3:
                rules.append(
                    f"Approved claims have significantly higher severity "
                    f"(avg: {diff['approved_value']:.2f} vs {diff['rejected_value']:.2f})"
                )
        
        if 'cost_amount_mean' in differences:
            diff = differences['cost_amount_mean']
            if abs(diff['difference']) > 1000:
                rules.append(
                    f"Cost threshold appears to be around "
                    f"${(diff['approved_value'] + diff['rejected_value'])/2:,.0f}"
                )
        
        return rules
