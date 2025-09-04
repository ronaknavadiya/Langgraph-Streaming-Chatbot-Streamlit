From python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# expose streamlit port
EXPOSE 8501

CMD [ "streamlit","run","chatbot.frontend.py" ]