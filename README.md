# Company Manager

## Requirement
* docker-compose

### 서버시작
    docker-compose -f docker-compose.yml up -d --build

### 서버종료
    docker-compose -f docker-compose.yml down
    
#### 기본 url
csv fixture 가 mysql docker가 구동되면 insert 되므로 서버구동후 5~10초 후에 접속한다.
* http://127.0.0.1

### api명세
* http://127.0.0.1/api/spec.html

### test 
    docker exec -i wantedlab_flask_1 python test.py

### db 접속정보
* host : 127.0.0.1
* port : 32770
* username : user
* password : wantedlab!@
* dbname: wantedlab