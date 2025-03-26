FROM nginx:stable-alpine

RUN apk add --no-cache nginx-mod-http-modsecurity \
    && mkdir /etc/nginx/modsec

COPY modsecurity.conf /etc/nginx/modsec/
COPY waf.conf /etc/nginx/modsec/
COPY nginx.conf /etc/nginx/nginx.conf

RUN ln -s /usr/lib/nginx/modules/ngx_http_modsecurity_module.so /etc/nginx/modules/

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
