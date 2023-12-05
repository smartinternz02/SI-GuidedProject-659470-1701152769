FROM python:3.8.0
WORKDIR /app
ADD . /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
RUN pip install --force-reinstall ibm_db==3.1.0 ibm_db_sa==0.3.7 
ENV LISTEN_PORT=5000
EXPOSE 5000
CMD ["python","db2.py"]
