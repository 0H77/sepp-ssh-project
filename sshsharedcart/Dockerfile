FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


RUN echo '#!/bin/bash\n\
# Run database migrations\n\
python manage.py migrate\n\
\n\
# # Load initial data if the JSON exists\n\
# if [ -f initial_data.json ]; then\n\
#     python manage.py loaddata initial_data.json\n\
# fi\n\
# \n\
echo ""\n\
echo "🌐 Django Development Server is starting..."\n\
echo ""\n\
echo "********************************"\n\
echo "Access at: http://localhost:8000"\n\
echo "********************************"\n\
echo ""\n\
\n\
# Start Django development server\n\
python manage.py runserver 0.0.0.0:8000' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]