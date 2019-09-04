FROM python
ADD requirements.txt requirements.txt
RUN apt install -y libpq-dev && pip install --upgrade pip && pip install -r requirements.txt
ADD rmm app/
WORKDIR app
ENTRYPOINT python main.py