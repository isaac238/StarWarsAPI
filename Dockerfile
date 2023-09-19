FROM python

LABEL maintainer="isaac@isaac238.dev"

COPY dependencies.txt dependencies.txt

RUN pip3 install -r dependencies.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
