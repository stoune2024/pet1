FROM python:3.12-slim
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /pet1
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY pytest.ini database.db .env ./
COPY ./app ./app
EXPOSE 80
USER appuser
#VOLUME /pet1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]