# -------------- Build 階段 --------------
FROM node:20-alpine AS build-stage

WORKDIR /app

# 安裝套件
COPY package*.json ./
RUN npm install

# 複製所有前端原始碼並打包
COPY . .
RUN npm run build

# -------------- 執行 階段 (Nginx) --------------
FROM nginx:alpine

# 將打包好的 dist 檔案複製到 Nginx 的對應目錄
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露 Port 80 (內部使用)
EXPOSE 80

# 執行 nginx
CMD ["nginx", "-g", "daemon off;"]
