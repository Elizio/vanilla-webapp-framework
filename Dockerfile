# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies including PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=backend.app
ENV FLASK_ENV=production
ENV DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vanilla_webapp

# Create PostgreSQL data directory
RUN mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql
RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

# Initialize PostgreSQL database
USER postgres
RUN /usr/lib/postgresql/13/bin/initdb -D /var/lib/postgresql/data
RUN echo "host all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf
RUN echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf

# Create database and user
RUN /usr/lib/postgresql/13/bin/pg_ctl -D /var/lib/postgresql/data -l logfile start && \
    psql --command "CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';" && \
    createdb -O postgres vanilla_webapp

# Switch back to root for running the application
USER root

# Create startup script
RUN echo '#!/bin/bash\n\
/usr/lib/postgresql/13/bin/pg_ctl -D /var/lib/postgresql/data -l logfile start\n\
python -m flask run --host=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 5000

# Run the application
CMD ["/app/start.sh"] 