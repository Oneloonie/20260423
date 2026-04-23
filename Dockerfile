FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the database setup script during build or startup
# Better to run it in build.sh or as a CMD part
RUN chmod +x build.sh

EXPOSE 8000

CMD ["./build.sh"]
