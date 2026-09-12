# BASE IMAGE
FROM python:3.12-slim

# WORKING DIRECTORY
WORKDIR /app

# PYTHON CONFIGURATION
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# JAVA
RUN apt-get update && apt-get install -y default-jdk wget && apt-get clean && rm -rf /var/lib/apt/lists/*

# JAVA ENVIRONMENT
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# INSTALL PYTHON DEPENDENCIES
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -P /usr/local/lib/python3.12/site-packages/pyspark/jars/

RUN wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
    -P /usr/local/lib/python3.12/site-packages/pyspark/jars/

# COPY APPLICATION
COPY src/ ./src/

# RUN APPLICATION
CMD ["python", "src/main.py"]