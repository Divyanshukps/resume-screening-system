FROM python:3.11-slim

# Hugging Face Spaces runs containers as user 1000
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data at build time (the app falls back to a built-in tokenizer if this fails)
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')" || true

COPY --chown=user . .

EXPOSE 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "app:app"]
