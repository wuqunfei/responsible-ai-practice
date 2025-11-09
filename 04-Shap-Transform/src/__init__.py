"""
Pet Insurance SHAP Analysis Package

A comprehensive solution for explaining GPT model decisions on pet insurance claims
using SHAP (SHapley Additive exPlanations).
"""

from .shap_explainer import PetClaimExplainer
from .semantic_analyzer import SemanticAnalyzer
from .visualization import ClaimVisualizer

__version__ = "1.0.0"
__author__ = "AI Team"
__email__ = "ai-team@your-company.com"

__all__ = [
    "PetClaimExplainer",
    "SemanticAnalyzer", 
    "ClaimVisualizer"
]

# Module level docstring
__doc__ = """
Pet Insurance SHAP Analysis

This package provides tools for:
- Explaining GPT model decisions using SHAP
- Semantic analysis of pet insurance claims
- Visualization of decision factors
- Business rule generation

Quick Start:
    >>> from src import PetClaimExplainer
    >>> explainer = PetClaimExplainer()
    >>> explanation = explainer.explain_claim("Emergency surgery for dog")
"""
