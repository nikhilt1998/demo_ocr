# Some container that is already suitable for unicover
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY uploaded /app/uploaded
COPY processed /app/processed
COPY ner /app/ner
COPY ./job.py /app/
COPY ./ner.py /app/
COPY ./requirements.txt /app/
COPY ./spell_checker.py /app/
COPY ./states.py /app/
COPY ./words.txt /app/
COPY ./main.py /app/
COPY ./start.sh /app/
COPY ./university.py /app/
WORKDIR '/app'
# install dependencies, we could also use the conda env, but it is more minimal
# we could probably find an image including this
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN python job.py
RUN chmod +x ./start.sh
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["bash","start.sh"]