# Используем официальный образ Nginx
FROM nginx:alpine

# Удаляем дефолтную конфигурацию
RUN rm /etc/nginx/conf.d/default.conf

# Копируем нашу конфигурацию
COPY nginx.conf /etc/nginx/conf.d

# Создаем директории для статики
RUN mkdir -p /app/static /app/media

VOLUME /app/static /app/media