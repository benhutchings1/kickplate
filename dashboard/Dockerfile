FROM node:20.16.0-alpine

WORKDIR /dashboard

COPY package-lock.json .
COPY package.json .
COPY build/ .

RUN npm install

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
