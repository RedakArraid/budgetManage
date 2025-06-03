# Multi-stage build pour optimiser la taille de l'image
FROM python:3.11-slim as builder

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="BudgetManage Team"
LABEL description="Système de Gestion Budget - Architecture MVC avec Streamlit"
LABEL version="2.0"

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r budgetuser && useradd -r -g budgetuser budgetuser

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=budgetuser:budgetuser . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/data && \
    chown -R budgetuser:budgetuser /app

# Changer vers l'utilisateur non-root
USER budgetuser

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck pour vérifier que l'application fonctionne
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Variables d'environnement par défaut
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Commande de démarrage
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
