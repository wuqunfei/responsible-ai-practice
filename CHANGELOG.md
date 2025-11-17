# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Model Caching**: The GPT-2 model is now cached locally in the `cached_models` directory to prevent repeated downloads. This significantly speeds up initialization after the first run.
- **Unique SHAP Explanation Files**: The `get_shap_explanation` function now accepts a `claim_id` to generate unique filenames for SHAP explanation HTML and PNG files (e.g., `shap_explanation_CLM-2024-001.html`). This prevents overwriting files when processing multiple claims.

### Changed
- `GPT2ClaimClassifier` now accepts a `cache_dir` parameter in its constructor to specify the model cache directory.
- `demo_shap.py` and `main.py` have been updated to use the new model caching and unique file output features.