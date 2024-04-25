FROM python

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . .



RUN pip install -r requirements.txt

CMD ["python", "main.py"]