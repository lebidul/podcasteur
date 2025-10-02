# Makefile pour Podcasteur
# Commandes utiles pour le développement et les releases

.PHONY: help install dev test format lint clean build release

# Couleurs pour les messages
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Affiche cette aide
	@echo "$(GREEN)Podcasteur - Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Installe les dépendances
	@echo "$(GREEN)Installation des dépendances...$(NC)"
	pip install -r requirements.txt
	pip install -e .
	@echo "$(GREEN)✓ Installation terminée$(NC)"

dev: ## Installe les dépendances de développement
	@echo "$(GREEN)Installation des dépendances de développement...$(NC)"
	pip install pytest pytest-cov black flake8 mypy
	@echo "$(GREEN)✓ Installation terminée$(NC)"

test: ## Lance les tests
	@echo "$(GREEN)Lancement des tests...$(NC)"
	pytest tests/ -v

test-cov: ## Lance les tests avec couverture
	@echo "$(GREEN)Tests avec couverture...$(NC)"
	pytest --cov=src --cov-report=html --cov-report=term tests/

format: ## Formate le code avec Black
	@echo "$(GREEN)Formatage du code...$(NC)"
	black src/ tests/
	@echo "$(GREEN)✓ Code formaté$(NC)"

lint: ## Vérifie le style avec Flake8
	@echo "$(GREEN)Vérification du style...$(NC)"
	flake8 src/ tests/ --max-line-length=100
	@echo "$(GREEN)✓ Style vérifié$(NC)"

type-check: ## Vérifie les types avec mypy
	@echo "$(GREEN)Vérification des types...$(NC)"
	mypy src/ --ignore-missing-imports
	@echo "$(GREEN)✓ Types vérifiés$(NC)"

clean: ## Nettoie les fichiers temporaires
	@echo "$(GREEN)Nettoyage...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ .coverage htmlcov/ sortie/
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

build: clean ## Construit le package Python
	@echo "$(GREEN)Construction du package...$(NC)"
	python -m build
	@echo "$(GREEN)✓ Package construit dans dist/$(NC)"

release-check: ## Vérifie que tout est prêt pour une release
	@echo "$(GREEN)Vérification pré-release...$(NC)"
	@echo "  Checking git status..."
	@git diff-index --quiet HEAD || (echo "$(YELLOW)⚠  Il y a des changements non committés$(NC)" && exit 1)
	@echo "  Running tests..."
	@make test
	@echo "  Checking code style..."
	@make lint
	@echo "$(GREEN)✓ Prêt pour la release$(NC)"

release: release-check ## Crée une nouvelle release (usage: make release VERSION=1.2.3)
	@if [ -z "$(VERSION)" ]; then \
		echo "$(YELLOW)Usage: make release VERSION=1.2.3$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Création de la release v$(VERSION)...$(NC)"
	@echo "  Updating RELEASE_NOTES.md..."
	@if ! grep -q "## v$(VERSION)" RELEASE_NOTES.md; then \
		echo "$(YELLOW)⚠  Ajoutez d'abord les notes pour v$(VERSION) dans RELEASE_NOTES.md$(NC)"; \
		exit 1; \
	fi
	@echo "  Creating and pushing tag..."
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "$(GREEN)✓ Tag v$(VERSION) créé et poussé$(NC)"
	@echo "$(GREEN)✓ GitHub Actions va créer la release automatiquement$(NC)"
	@echo "$(YELLOW)Suivez le progrès sur: https://github.com/lebidul/podcasteur/actions$(NC)"

run-example: ## Lance un exemple de workflow manuel
	@echo "$(GREEN)Exemple de workflow manuel...$(NC)"
	podcasteur exemple exemple_decoupage.json
	@echo "$(GREEN)✓ Fichier d'exemple créé$(NC)"
	@echo "$(YELLOW)Éditez exemple_decoupage.json puis lancez:$(NC)"
	@echo "  podcasteur manuel exemple_decoupage.json dossier_audio/"

run-auto: ## Lance un exemple de workflow automatique (nécessite clé API)
	@echo "$(GREEN)Exemple de workflow automatique...$(NC)"
	@if [ -z "$${ANTHROPIC_API_KEY}" ]; then \
		echo "$(YELLOW)⚠  Définissez ANTHROPIC_API_KEY dans .env$(NC)"; \
		exit 1; \
	fi
	@echo "Lancez: podcasteur auto fichier1.wav fichier2.wav --duree 5"

docs: ## Génère la documentation
	@echo "$(GREEN)Génération de la documentation...$(NC)"
	@echo "$(YELLOW)TODO: Configurer Sphinx ou MkDocs$(NC)"

install-hooks: ## Installe les git hooks
	@echo "$(GREEN)Installation des git hooks...$(NC)"
	@echo '#!/bin/bash\nmake format\nmake lint' > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✓ Git hooks installés$(NC)"

version: ## Affiche la version actuelle
	@python -c "from src import __version__; print(f'Podcasteur v{__version__}')" 2>/dev/