FROM nginx:1.21.3
COPY nginx.conf /etc/nginx/nginx.conf
COPY dist/demo /usr/share/nginx/html
EXPOSE 3000
ENTRYPOINT ["nginx","-g","daemon off;"]